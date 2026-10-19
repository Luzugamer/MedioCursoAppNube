from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.session import get_db
from app.models.user import User
from app.models.company import Company
from app.schemas.user import UserCreate, UserUpdate, UserResponse
from app.api.deps import get_current_user, require_admin
from app.api.tenant import creation_tenant, tenant_query, is_superadmin
from app.models.role import Role
from app.core.security import get_password_hash
from app.services.audit_service import log_audit

router = APIRouter()

@router.get("/roles")
def get_roles(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    from app.models.role import Role
    query = db.query(Role)
    if current_user.rol.nombre != "SUPERADMIN":
        query = query.filter(Role.nombre != "SUPERADMIN")
    roles = query.all()
    return [{"id": r.id, "nombre": r.nombre} for r in roles]

@router.get("/", response_model=List[UserResponse])
def get_users(
    empresa_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    query = db.query(User)
    
    # Si es SUPERADMIN, puede filtrar por cualquier empresa o listar todos
    query = tenant_query(query, User, current_user, empresa_id)
        
    return query.order_by(User.created_at.desc()).all()

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(
    user_in: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    role = db.query(Role).filter(Role.id == user_in.rol_id).first()
    if role is None:
        raise HTTPException(404, "Rol no encontrado")
    if not is_superadmin(current_user) and role.nombre == "SUPERADMIN":
        raise HTTPException(403, "No puede crear un superadministrador")
    if role.nombre == "SUPERADMIN":
        if user_in.empresa_id is not None:
            raise HTTPException(400, "El superadministrador global no pertenece a una empresa")
        target_empresa_id = None
    else:
        target_empresa_id = creation_tenant(db, current_user, user_in.empresa_id)
        
    # Verificar límite de usuarios de la empresa
    if target_empresa_id:
        company = db.query(Company).filter(Company.id == target_empresa_id).first()
        if company:
            current_count = db.query(User).filter(User.empresa_id == target_empresa_id).count()
            if current_count >= company.limite_usuarios:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Ha alcanzado el límite máximo de usuarios ({company.limite_usuarios}) permitido para su suscripción."
                )

    existing = db.query(User).filter(User.email == user_in.email).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El correo ya se encuentra registrado")
        
    user = User(
        empresa_id=target_empresa_id,
        nombre=user_in.nombre,
        email=user_in.email,
        password_hash=get_password_hash(user_in.password),
        rol_id=user_in.rol_id,
        permisos=user_in.permisos,
        activo=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    db.expire(user, ["rol"])
    
    log_audit(
        db,
        usuario_id=current_user.id,
        empresa_id=target_empresa_id,
        accion="CREAR_USUARIO",
        entidad="User",
        entidad_id=user.id,
        descripcion=f"Usuario creado: {user.email}"
    )
    return user

@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    user_in: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    query = db.query(User).filter(User.id == user_id)
    query = tenant_query(query, User, current_user)
        
    user = query.first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")

    update_data = user_in.model_dump(exclude_unset=True)
    if "rol_id" in update_data:
        role = db.query(Role).filter(Role.id == update_data["rol_id"]).first()
        if role is None:
            raise HTTPException(404, "Rol no encontrado")
        if not is_superadmin(current_user) and role.nombre == "SUPERADMIN":
            raise HTTPException(403, "No puede asignar el rol superadministrador")
        if (role.nombre == "SUPERADMIN") != (user.empresa_id is None):
            raise HTTPException(400, "El rol no corresponde a la pertenencia empresarial del usuario")
    if "password" in update_data and update_data["password"]:
        update_data["password_hash"] = get_password_hash(update_data.pop("password"))
    elif "password" in update_data:
        update_data.pop("password")

    for field, value in update_data.items():
        setattr(user, field, value)

    db.commit()
    db.refresh(user)
    db.expire(user, ["rol"])

    log_audit(
        db,
        usuario_id=current_user.id,
        empresa_id=user.empresa_id,
        accion="ACTUALIZAR_USUARIO",
        entidad="User",
        entidad_id=user.id,
        descripcion=f"Usuario actualizado: {user.email}"
    )
    return user

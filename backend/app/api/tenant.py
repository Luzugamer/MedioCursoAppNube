from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.company import Company
from app.models.user import User


def is_superadmin(user: User) -> bool:
    return user.rol.nombre == "SUPERADMIN"


def tenant_query(query, model, user: User, empresa_id: int | None = None):
    """Scope a tenant-owned query; only the global administrator can see all."""
    if is_superadmin(user):
        return query.filter(model.empresa_id == empresa_id) if empresa_id is not None else query
    if user.empresa_id is None:
        raise HTTPException(403, "El usuario no pertenece a una empresa")
    if empresa_id is not None and empresa_id != user.empresa_id:
        raise HTTPException(403, "No puede acceder a otra empresa")
    return query.filter(model.empresa_id == user.empresa_id)


def creation_tenant(db: Session, user: User, requested_id: int | None) -> int:
    if is_superadmin(user):
        if requested_id is None:
            raise HTTPException(422, "El superadministrador debe indicar empresa_id")
        empresa_id = requested_id
    else:
        if user.empresa_id is None:
            raise HTTPException(403, "El usuario no pertenece a una empresa")
        if requested_id is not None and requested_id != user.empresa_id:
            raise HTTPException(403, "No puede crear datos en otra empresa")
        empresa_id = user.empresa_id
    company = db.query(Company).filter(Company.id == empresa_id, Company.activo.is_(True)).first()
    if company is None:
        raise HTTPException(404, "Empresa no encontrada o inactiva")
    return empresa_id


def require_same_tenant(user: User, empresa_id: int) -> None:
    if not is_superadmin(user) and user.empresa_id != empresa_id:
        raise HTTPException(404, "Registro no encontrado")

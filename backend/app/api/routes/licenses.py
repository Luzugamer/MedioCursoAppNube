from datetime import date, datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from app.db.session import get_db
from app.models.license import License
from app.models.client import Client
from app.models.equipment import Equipment
from app.models.user import User
from app.schemas.license import LicenseCreate, LicenseUpdate, LicenseResponse
from app.api.deps import get_current_user, check_permission
from app.api.tenant import creation_tenant, tenant_query
from app.services.audit_service import log_audit

router = APIRouter()

def compute_license_response(lic: License) -> LicenseResponse:
    today = date.today()
    dias_restantes = None
    estado = "ACTIVA"

    if lic.es_permanente:
        estado = "PERMANENTE"
    elif lic.fecha_fin:
        delta = (lic.fecha_fin - today).days
        dias_restantes = delta
        if delta < 0:
            estado = "VENCIDA"
        elif delta <= 30:
            estado = "POR_VENCER"
        else:
            estado = "ACTIVA"

    cliente_nombre = None
    if lic.cliente:
        cliente_nombre = f"{lic.cliente.nombres} {lic.cliente.apellidos}".strip()

    equipo_info = None
    if lic.equipo:
        equipo_info = f"{lic.equipo.tipo} {lic.equipo.marca} {lic.equipo.modelo}".strip()

    return LicenseResponse(
        id=lic.id,
        empresa_id=lic.empresa_id,
        cliente_id=lic.cliente_id,
        equipo_id=lic.equipo_id,
        categoria=lic.categoria,
        nombre_producto=lic.nombre_producto,
        clave_licencia=lic.clave_licencia,
        cantidad_dispositivos=lic.cantidad_dispositivos,
        es_permanente=lic.es_permanente,
        fecha_inicio=lic.fecha_inicio,
        fecha_fin=lic.fecha_fin,
        proveedor=lic.proveedor,
        notas=lic.notas,
        cliente_nombre=cliente_nombre,
        equipo_info=equipo_info,
        dias_restantes=dias_restantes,
        estado_vencimiento=estado,
        created_at=lic.created_at,
        updated_at=lic.updated_at
    )

@router.get("/", response_model=List[LicenseResponse])
def get_licenses(
    categoria: Optional[str] = None,
    cliente_id: Optional[int] = None,
    empresa_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_permission("licencias", "ver"))
):
    query = db.query(License).options(joinedload(License.cliente), joinedload(License.equipo))
    query = tenant_query(query, License, current_user, empresa_id)
        
    if categoria:
        query = query.filter(License.categoria == categoria.upper())
    if cliente_id:
        query = query.filter(License.cliente_id == cliente_id)

    licenses = query.order_by(License.created_at.desc()).all()
    return [compute_license_response(lic) for lic in licenses]

@router.post("/", response_model=LicenseResponse, status_code=status.HTTP_201_CREATED)
def create_license(
    lic_in: LicenseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_permission("licencias", "crear"))
):
    empresa_id = creation_tenant(db, current_user, lic_in.empresa_id)
    
    # Validaciones de cliente y equipo pertenencia a la empresa
    if lic_in.cliente_id:
        client = db.query(Client).filter(Client.id == lic_in.cliente_id, Client.empresa_id == empresa_id)
        if not client.first():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cliente no encontrado o no pertenece a su empresa")

    if lic_in.equipo_id:
        eq = db.query(Equipment).filter(Equipment.id == lic_in.equipo_id, Equipment.empresa_id == empresa_id)
        if not eq.first():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Equipo no encontrado o no pertenece a su empresa")
    if lic_in.cliente_id and lic_in.equipo_id:
        equipment = db.query(Equipment).filter(Equipment.id == lic_in.equipo_id).first()
        if equipment.cliente_id != lic_in.cliente_id:
            raise HTTPException(400, "El equipo no pertenece al cliente")

    new_lic = License(
        empresa_id=empresa_id,
        cliente_id=lic_in.cliente_id,
        equipo_id=lic_in.equipo_id,
        categoria=lic_in.categoria.upper(),
        nombre_producto=lic_in.nombre_producto,
        clave_licencia=lic_in.clave_licencia,
        cantidad_dispositivos=lic_in.cantidad_dispositivos,
        es_permanente=lic_in.es_permanente,
        fecha_inicio=lic_in.fecha_inicio,
        fecha_fin=lic_in.fecha_fin,
        proveedor=lic_in.proveedor,
        notas=lic_in.notas
    )
    db.add(new_lic)
    db.commit()
    db.refresh(new_lic)

    log_audit(
        db,
        usuario_id=current_user.id,
        empresa_id=empresa_id,
        accion="CREAR_LICENCIA",
        entidad="License",
        entidad_id=new_lic.id,
        descripcion=f"Licencia '{new_lic.nombre_producto}' ({new_lic.categoria}) creada"
    )

    # Re-cargar con relaciones
    loaded_lic = db.query(License).options(joinedload(License.cliente), joinedload(License.equipo)).filter(License.id == new_lic.id).first()
    return compute_license_response(loaded_lic)

@router.put("/{license_id}", response_model=LicenseResponse)
def update_license(
    license_id: int,
    lic_in: LicenseUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_permission("licencias", "editar"))
):
    query = db.query(License).filter(License.id == license_id)
    query = tenant_query(query, License, current_user)
    
    lic = query.first()
    if not lic:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Licencia no encontrada")

    update_data = lic_in.model_dump(exclude_unset=True)
    if "cliente_id" in update_data and update_data["cliente_id"] is not None:
        if not db.query(Client).filter(Client.id == update_data["cliente_id"], Client.empresa_id == lic.empresa_id).first():
            raise HTTPException(404, "Cliente no encontrado")
    if "equipo_id" in update_data and update_data["equipo_id"] is not None:
        if not db.query(Equipment).filter(Equipment.id == update_data["equipo_id"], Equipment.empresa_id == lic.empresa_id).first():
            raise HTTPException(404, "Equipo no encontrado")
    effective_client = update_data.get("cliente_id", lic.cliente_id)
    effective_equipment = update_data.get("equipo_id", lic.equipo_id)
    if effective_client is not None and effective_equipment is not None:
        equipment = db.query(Equipment).filter(Equipment.id == effective_equipment).first()
        if equipment.cliente_id != effective_client:
            raise HTTPException(400, "El equipo no pertenece al cliente")
    for field, value in update_data.items():
        if field == "categoria" and value:
            setattr(lic, field, value.upper())
        else:
            setattr(lic, field, value)

    # Validar reglas de Antivirus en update
    if lic.categoria == "ANTIVIRUS":
        if lic.es_permanente:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Las licencias de Antivirus no pueden ser permanentes")
        if not lic.fecha_inicio or not lic.fecha_fin:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Las licencias de Antivirus requieren fechas de inicio y fin")

    db.commit()
    db.refresh(lic)

    log_audit(
        db,
        usuario_id=current_user.id,
        empresa_id=lic.empresa_id,
        accion="ACTUALIZAR_LICENCIA",
        entidad="License",
        entidad_id=lic.id,
        descripcion=f"Licencia '{lic.nombre_producto}' actualizada"
    )

    loaded_lic = db.query(License).options(joinedload(License.cliente), joinedload(License.equipo)).filter(License.id == lic.id).first()
    return compute_license_response(loaded_lic)

@router.delete("/{license_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_license(
    license_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_permission("licencias", "eliminar"))
):
    query = db.query(License).filter(License.id == license_id)
    query = tenant_query(query, License, current_user)

    lic = query.first()
    if not lic:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Licencia no encontrada")

    db.delete(lic)
    db.commit()

    log_audit(
        db,
        usuario_id=current_user.id,
        empresa_id=lic.empresa_id,
        accion="ELIMINAR_LICENCIA",
        entidad="License",
        entidad_id=license_id,
        descripcion=f"Licencia #{license_id} eliminada"
    )

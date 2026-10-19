from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.product import Product
from app.models.service import Service
from app.models.user import User
from app.models.inventory import InventoryMovement, MovementType
from app.services.audit_service import log_audit

def discount_inventory_for_service(
    db: Session,
    producto_id: int,
    cantidad: int,
    servicio_id: int,
    usuario_id: int,
    empresa_id: int,
    observacion: str = "Consumo en Servicio"
):
    if cantidad <= 0:
        raise HTTPException(status_code=400, detail="La cantidad debe ser mayor a 0")
        
    service = db.query(Service).filter(Service.id == servicio_id, Service.empresa_id == empresa_id).first()
    user = db.query(User).filter(User.id == usuario_id).first()
    if service is None or user is None or (user.empresa_id != empresa_id and user.rol.nombre != "SUPERADMIN"):
        raise HTTPException(status_code=404, detail="Servicio o usuario no pertenece a la empresa")
    product = db.query(Product).filter(Product.id == producto_id, Product.empresa_id == empresa_id, Product.activo == True).with_for_update().first()
    if not product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
        
    if product.stock < cantidad:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Stock insuficiente para '{product.nombre}'. Stock actual: {product.stock}, Solicitado: {cantidad}"
        )
        
    # Descontar stock
    product.stock -= cantidad
    
    # Registrar Movimiento
    movement = InventoryMovement(
        empresa_id=empresa_id,
        producto_id=product.id,
        tipo=MovementType.SALIDA,
        cantidad=cantidad,
        servicio_id=servicio_id,
        usuario_id=usuario_id,
        observacion=observacion
    )
    db.add(movement)
    
    log_audit(
        db, usuario_id=usuario_id, empresa_id=empresa_id, accion="MOVIMIENTO_INVENTARIO",
        entidad="Product", entidad_id=product.id,
        descripcion=f"Salida de {cantidad} unidades de '{product.nombre}' por Servicio #{servicio_id}"
    )
    db.commit()
    db.refresh(product)
    return movement

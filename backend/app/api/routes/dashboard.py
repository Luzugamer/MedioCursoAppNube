from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timezone
from app.db.session import get_db
from app.models.client import Client
from app.models.service import Service, ServiceStatus
from app.models.product import Product
from app.models.payment import Payment
from app.schemas.dashboard import DashboardStats
from app.models.user import User
from app.api.deps import get_current_user
from app.api.tenant import tenant_query

router = APIRouter()

@router.get("/stats", response_model=DashboardStats)
def get_dashboard_stats(
    empresa_id: int | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    cl_q = db.query(func.count(Client.id)).filter(Client.activo == True)
    srv_rec = db.query(func.count(Service.id)).filter(Service.estado == ServiceStatus.RECIBIDO)
    srv_proc = db.query(func.count(Service.id)).filter(Service.estado == ServiceStatus.EN_PROCESO)
    srv_term = db.query(func.count(Service.id)).filter(Service.estado == ServiceStatus.TERMINADO)
    stk_q = db.query(func.count(Product.id)).filter(Product.activo == True, Product.stock <= Product.stock_minimo)
    
    today = datetime.now(timezone.utc).date()
    pay_q = db.query(func.sum(Payment.monto)).filter(func.date(Payment.fecha) == today)

    cl_q = tenant_query(cl_q, Client, current_user, empresa_id)
    srv_rec = tenant_query(srv_rec, Service, current_user, empresa_id)
    srv_proc = tenant_query(srv_proc, Service, current_user, empresa_id)
    srv_term = tenant_query(srv_term, Service, current_user, empresa_id)
    stk_q = tenant_query(stk_q, Product, current_user, empresa_id)
    pay_q = tenant_query(pay_q, Payment, current_user, empresa_id)

    total_clients = cl_q.scalar() or 0
    recibidos = srv_rec.scalar() or 0
    en_proceso = srv_proc.scalar() or 0
    terminados = srv_term.scalar() or 0
    stock_bajo = stk_q.scalar() or 0
    ingresos_hoy = pay_q.scalar() or 0.0

    return {
        "total_clientes": total_clients,
        "servicios_pendientes": recibidos,
        "servicios_en_proceso": en_proceso,
        "servicios_terminados": terminados,
        "productos_stock_bajo": stock_bajo,
        "ingresos_hoy": float(ingresos_hoy)
    }

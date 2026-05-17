from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_admin, get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.service import (
    ServiceCreate,
    ServiceDetail,
    ServiceResponse,
    ServiceSearchParams,
    ServiceSummary,
    ServiceUpdate,
)
from app.services.service import ServiceService
from app.utils.enums import ServiceStatus

router = APIRouter(prefix="/services", tags=["services"])


@router.get("", response_model=list[ServiceSummary])
def list_services(
    params: ServiceSearchParams = Depends(),
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
):
    service_layer = ServiceService(db)
    return service_layer.search_services(params=params, skip=skip, limit=limit)


@router.get("/{service_id}", response_model=ServiceDetail)
def get_service(service_id: int, db: Session = Depends(get_db)):
    service_layer = ServiceService(db)

    try:
        return service_layer.get_service(service_id)
    except LookupError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error)) from error


@router.get("/seller/{seller_id}", response_model=list[ServiceSummary])
def list_services_by_seller(
    seller_id: int, db: Session = Depends(get_db), skip: int = 0, limit: int = 20
):
    service_layer = ServiceService(db)
    return service_layer.list_service_by_seller_id(seller_id, skip=skip, limit=limit)


@router.post("", response_model=ServiceResponse, status_code=status.HTTP_201_CREATED)
def create_service(
    data: ServiceCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service_layer = ServiceService(db)
    return service_layer.create_service(seller_id=current_user.id, data=data)


@router.patch("/{service_id}", response_model=ServiceResponse)
def update_service(
    service_id: int,
    data: ServiceUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service_layer = ServiceService(db)

    try:
        return service_layer.update_service(
            service_id=service_id, user_id=current_user.id, data=data
        )
    except LookupError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error)) from error
    except PermissionError as error:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(error)) from error


@router.delete("/{service_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_service(
    service_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    service_layer = ServiceService(db)

    try:
        service_layer.delete_service(service_id=service_id, user_id=current_user.id)
    except LookupError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error)) from error
    except PermissionError as error:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(error)) from error


@router.patch("/{service_id}/admin/status", response_model=ServiceResponse)
def admin_set_status(
    service_id: int,
    new_status: ServiceStatus,
    _admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    service_layer = ServiceService(db)

    try:
        return service_layer.admin_set_status(service_id=service_id, status=new_status)
    except LookupError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error)) from error


@router.delete("/{service_id}/admin", status_code=status.HTTP_204_NO_CONTENT)
def admin_delete_service(
    service_id: int, _admin: User = Depends(get_current_admin), db: Session = Depends(get_db)
):
    service_layer = ServiceService(db)

    try:
        service_layer.admin_delete_service(service_id=service_id)
    except LookupError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error)) from error

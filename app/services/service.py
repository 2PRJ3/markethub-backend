
from sqlalchemy.orm import Session

from app.models.service import Service
from app.repositories.service import ServiceRepository
from app.schemas.service import ServiceCreate, ServiceUpdate
from app.utils.enums import ServiceStatus


class ServiceService:
    def __init__(self, db: Session):
        self.db: Session = db
        self.repo: ServiceRepository = ServiceRepository(db)

    def create_service(self, seller_id: int, data: ServiceCreate) -> Service:
        service = Service(
            seller_id=seller_id,
            category_id=data.category_id,
            title=data.title,
            description=data.description,
            price=data.price,
            image_url=data.image_url,
            status=ServiceStatus.ACTIVE,
            reviews_count=0,
        )
        service_created = self.repo.create(service)
        self.db.commit()
        self.db.refresh(service_created)

        return service_created

    def get_service(self, service_id: int) -> Service:
        service = self.repo.get_by_id(service_id)

        if not service:
            raise LookupError(f"Service introuvable: {service_id}")
        return service

    def list_services(self, skip: int = 0, limit: int = 20) -> list[Service]:
        return self.repo.get_all(skip=skip, limit=limit)

    def list_service_by_seller_id(
        self, seller_id: int, skip: int = 0, limit: int = 20
    ) -> list[Service]:
        return self.repo.get_by_seller(seller_id, skip=skip, limit=limit)

    def update_service(self, service_id: int, user_id: int, data: ServiceUpdate) -> Service:
        service = self.get_service(service_id)

        if service.seller_id != user_id:
            raise PermissionError("Vous n'êtes pas permis à modifier ce service")
        update_data = data.model_dump(exclude_unset=True)
        print(f"[DEBUG] Champs reçus pour update: {update_data}")

        if update_data.get("status") == ServiceStatus.BANNED:
            raise PermissionError("Ce service a été bannis, impossible de le modifier")

        service_updated = self.repo.update(service, update_data)
        self.db.commit()
        self.db.refresh(service_updated)
        return service_updated

    def delete_service(self, service_id: int, user_id: int) -> None:
        service = self.get_service(service_id)

        if service.seller_id != user_id:
            raise PermissionError("Vous n'êtes pas autorisé à supprimé ce service")

        self.repo.delete(service)
        self.db.commit()

    def admin_set_status(self, service_id: int, status: ServiceStatus) -> Service:
        service = self.get_service(service_id)
        status_updated = self.repo.update(service, {"status": status})
        self.db.commit()
        self.db.refresh(status_updated)
        return status_updated

    def admin_delete_service(self, service_id: int) -> None:
        service = self.get_service(service_id)
        self.repo.delete(service)
        self.db.commit()

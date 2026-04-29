from enum import Enum

class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"

class ServiceStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    BANNED = "banned"
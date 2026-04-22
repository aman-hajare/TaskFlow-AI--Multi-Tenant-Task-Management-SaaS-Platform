from enum import Enum

class RoleEnum(str, Enum):
    super_admin = "super_admin"
    admin = "admin"
    manager = "manager"
    employee = "employee"

class SkillEnum(str, Enum):
    frontend = "frontend"
    backend = "backend"
    fullstack = "fullstack"
    devops = "devops"
    qa = "qa"
    design = "design"

class StatusEnum(str, Enum):
    pending = "pending"
    in_progress = "in_progress"
    blocked = "blocked"
    completed = "completed"

class PriorityEnum(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"
    urgent = "urgent"

class InviteStatusEnum(str, Enum):
    pending = "pending"
    accepted = "accepted"
    expired = "expired"
    
from enum import StrEnum


class Department(StrEnum):
    ENGINEERING = "ENGINEERING"
    SNT = "SNT"
    TRACTION = "TRACTION"


class AssetType(StrEnum):
    TRACK = "TRACK"
    SIGNAL = "SIGNAL"
    OHE = "OHE"
    POINT_MACHINE = "POINT_MACHINE"
    LEVEL_CROSSING = "LEVEL_CROSSING"
    OTHER = "OTHER"


class TaskStatus(StrEnum):
    PENDING = "PENDING"
    SCHEDULED = "SCHEDULED"
    COMPLETED = "COMPLETED"
    OVERDUE = "OVERDUE"
    EMERGENCY = "EMERGENCY"


class TrainType(StrEnum):
    EXPRESS = "EXPRESS"
    PASSENGER = "PASSENGER"
    FREIGHT = "FREIGHT"
    LOCAL = "LOCAL"
    SPECIAL = "SPECIAL"


class BlockType(StrEnum):
    TRAFFIC_BLOCK = "TRAFFIC_BLOCK"
    POWER_BLOCK = "POWER_BLOCK"
    LINE_BLOCK = "LINE_BLOCK"
    COMBINED_BLOCK = "COMBINED_BLOCK"


class TrafficDensity(StrEnum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class BlockPlanStatus(StrEnum):
    DRAFT = "DRAFT"
    RECOMMENDED = "RECOMMENDED"
    APPROVED = "APPROVED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"

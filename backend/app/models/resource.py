from sqlalchemy import Integer, String
from sqlalchemy import Enum as SqlEnum
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base
from app.models.enums import Department


class Resource(Base):
    __tablename__ = "resources"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    resource_code: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    department: Mapped[Department] = mapped_column(SqlEnum(Department, name="department"), index=True)
    resource_type: Mapped[str] = mapped_column(String(100))
    capacity: Mapped[int] = mapped_column(Integer, default=1)

from typing import Optional
from enum import Enum

from data_subjects.requests.base_request import BaseFilter, BaseSort


class AmbulanceStatus(str, Enum):
    """Статусы активов скорой помощи"""
    ALL = "all"  # Все
    NEW = "new"  # Новый
    IN_PROGRESS = "in_progress"  # В процессе
    COMPLETED = "completed"  # Завершен


class AmbulanceFilter(BaseFilter):
    """Фильтр для активов скорой помощи"""
    status: Optional[AmbulanceStatus] = AmbulanceStatus.ALL
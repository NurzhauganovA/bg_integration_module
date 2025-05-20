from typing import Optional
from enum import Enum

from data_subjects.requests.base_request import BaseFilter, BaseSort


class ClinicStatus(str, Enum):
    """Статусы активов поликлиники"""
    ALL = "all"  # Все
    SCHEDULED = "scheduled"  # Запланировано
    IN_PROGRESS = "in_progress"  # В процессе
    COMPLETED = "completed"  # Завершен


class ClinicFilter(BaseFilter):
    """Фильтр для активов поликлиники"""
    status: Optional[ClinicStatus] = ClinicStatus.ALL
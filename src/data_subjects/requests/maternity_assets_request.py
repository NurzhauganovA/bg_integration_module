from typing import Optional
from enum import Enum

from data_subjects.requests.base_request import BaseFilter, BaseSort


class MaternityStatus(str, Enum):
    """Статусы активов роддома"""
    ALL = "all"  # Все
    ACTIVE = "active"  # Активный
    DISCHARGED = "discharged"  # Выписан


class MaternityFilter(BaseFilter):
    """Фильтр для активов роддома"""
    status: Optional[MaternityStatus] = MaternityStatus.ALL
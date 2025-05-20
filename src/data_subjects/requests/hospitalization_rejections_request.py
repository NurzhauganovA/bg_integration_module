from typing import Optional
from enum import Enum

from data_subjects.requests.base_request import BaseFilter, BaseSort


class RejectionStatus(str, Enum):
    """Статусы отказов от госпитализации"""
    ALL = "all"  # Все
    REJECTED = "rejected"  # Отказано
    PENDING = "pending"  # В ожидании


class RejectionFilter(BaseFilter):
    """Фильтр для отказов от госпитализации"""
    status: Optional[RejectionStatus] = RejectionStatus.ALL
from typing import Optional
from enum import Enum

from data_subjects.requests.base_request import BaseFilter, BaseSort


class NewbornStatus(str, Enum):
    """Статусы новорожденных"""
    ALL = "all"  # Все
    ACTIVE = "active"  # Активный
    DISCHARGED = "discharged"  # Выписан


class NewbornFilter(BaseFilter):
    """Фильтр для новорожденных"""
    status: Optional[NewbornStatus] = NewbornStatus.ALL
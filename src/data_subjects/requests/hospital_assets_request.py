from typing import Optional
from enum import Enum

from data_subjects.requests.base_request import BaseFilter, BaseSort


class HospitalAssetStatus(str, Enum):
    """Статусы активов стационара"""
    ALL = "all"  # Все
    HOSPITALIZED = "hospitalized"  # Госпитализирован
    WAITING = "waiting"  # В приемном покое
    DISCHARGED = "discharged"  # Выписан


class HospitalAssetsFilter(BaseFilter):
    """Фильтр для активов стационара"""
    status: Optional[HospitalAssetStatus] = HospitalAssetStatus.ALL
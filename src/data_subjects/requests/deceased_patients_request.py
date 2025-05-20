from typing import Optional

from data_subjects.requests.base_request import BaseFilter, BaseSort


class DeceasedFilter(BaseFilter):
    """Фильтр для умерших пациентов"""
    pass  # Наследуем все параметры от базового фильтра
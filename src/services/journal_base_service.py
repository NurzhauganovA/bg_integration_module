from abc import ABC, abstractmethod
from typing import Dict, Any, Generic, TypeVar, Optional, Type

from handlers.bg_search_referrals_handler import BGReferralsHandler
from integration_sdk_orkendeu_mis.handlers.dto.handler_result_dto import HandlerResultDTO

ResponseType = TypeVar('ResponseType')
FilterType = TypeVar('FilterType')


class JournalBaseService(ABC, Generic[ResponseType, FilterType]):
    """Базовый сервис для всех журнальных сервисов."""

    @classmethod
    async def get_data(cls, filter_params: FilterType) -> ResponseType:
        """
        Получение данных из БГ и их преобразование в требуемый формат.

        :param filter_params: Параметры фильтрации
        :return: Преобразованные данные
        """
        bg_params = cls._filter_to_bg_params(filter_params)

        bg_data = await cls._get_bg_data(bg_params)

        if not bg_data.success:
            return cls._get_empty_response(filter_params)

        return cls._transform_data(bg_data.data, filter_params)

    @classmethod
    def _filter_to_bg_params(cls, filter_params: FilterType) -> Dict[str, Any]:
        """
        Преобразование параметров фильтрации в параметры запроса к БГ.

        :param filter_params: Параметры фильтрации
        :return: Параметры запроса к БГ
        """
        params = {
            "patientIINOrFIO": getattr(filter_params, "patient_identifier", ""),
            "dateFrom": getattr(filter_params, "date_from", ""),
            "dateTo": getattr(filter_params, "date_to", "")
        }

        return {k: v for k, v in params.items() if v is not None and v != ""}

    @staticmethod
    async def _get_bg_data(params: Dict[str, Any]) -> HandlerResultDTO:
        """
        Получение данных из БГ.

        :param params: Параметры запроса
        :return: Результат запроса к БГ
        """
        handler = BGReferralsHandler()
        return await handler.handle(params)

    @classmethod
    @abstractmethod
    def _transform_data(cls, data: Dict[str, Any], filter_params: FilterType) -> ResponseType:
        """
        Преобразование данных БГ в требуемый формат.

        :param data: Данные БГ
        :param filter_params: Параметры фильтрации
        :return: Преобразованные данные
        """
        pass

    @classmethod
    @abstractmethod
    def _get_empty_response(cls, filter_params: FilterType) -> ResponseType:
        """
        Получение пустого ответа.

        :param filter_params: Параметры фильтрации
        :return: Пустой ответ
        """
        pass
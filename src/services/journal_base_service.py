import re
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, Any, Generic, TypeVar, Optional, Type, List

from handlers.bg_search_referrals_handler import BGReferralsHandler
from integration_sdk_orkendeu_mis.handlers.dto.handler_result_dto import HandlerResultDTO
from data_subjects.enums.service_enums import (
    SortType, GenderCode, ContactInfo, PhonePattern, DefaultValues
)

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
    def _is_date_in_range(cls, reg_date_str: str, date_from: datetime, date_to: datetime) -> bool:
        """Проверка, входит ли дата в диапазон."""
        if not reg_date_str:
            return False

        try:
            reg_date = datetime.strptime(reg_date_str.split("T")[0], "%Y-%m-%d")
            return date_from <= reg_date <= date_to
        except ValueError:
            return False

    @classmethod
    def _is_patient_match(cls, item: Dict[str, Any], patient_identifier: str) -> bool:
        """Проверка соответствия пациента фильтру."""
        if not patient_identifier:
            return True

        patient_data = item.get("patient", {})
        patient_iin = patient_data.get("personin", "")
        patient_name = patient_data.get("personFullName", "").lower()

        return (patient_identifier.lower() in patient_name or
                patient_identifier == patient_iin)

    @classmethod
    def _is_patient_match_extended(cls, item: Dict[str, Any], patient_identifier: str) -> bool:
        """Расширенная проверка соответствия пациента фильтру (включая дополнительную информацию)."""
        if not patient_identifier:
            return True

        patient_data = item.get("patient", {})
        patient_iin = patient_data.get("personin", "")
        patient_name = patient_data.get("personFullName", "").lower()
        additional_info = item.get("addiditonalInformation", "").lower()

        return (patient_identifier.lower() in patient_name or
                patient_identifier == patient_iin or
                patient_identifier.lower() in additional_info)

    @classmethod
    def _is_department_match(cls, item: Dict[str, Any], department: str) -> bool:
        """Проверка соответствия отделения фильтру."""
        if not department or department == "all":
            return True

        item_department = item.get("bedProfile", {}).get("code", "")
        return item_department == department

    @classmethod
    def _extract_phone_number(cls, additional_info: str) -> str:
        """
        Извлечение номера телефона из дополнительной информации.

        :param additional_info: Дополнительная информация
        :return: Номер телефона или значение по умолчанию
        """
        if not additional_info:
            return ContactInfo.DEFAULT_PHONE.value

        phone_match = re.search(PhonePattern.PHONE_REGEX.value, additional_info)
        return phone_match.group(0) if phone_match else ContactInfo.DEFAULT_PHONE.value

    @classmethod
    def _get_patient_gender(cls, sex_code: str) -> str:
        """
        Получение пола пациента по коду.

        :param sex_code: Код пола
        :return: Строковое представление пола
        """
        gender_mapping = {
            GenderCode.MALE.value: "Мужской",
            GenderCode.FEMALE.value: "Женский"
        }
        return gender_mapping.get(sex_code, DefaultValues.GENDER_UNKNOWN.value)

    @classmethod
    def _format_department(cls, department_code: str) -> str:
        """
        Форматирование номера отделения.

        :param department_code: Код отделения
        :return: Отформатированный номер отделения
        """
        if not department_code:
            department_code = DefaultValues.DEPARTMENT_NUMBER.value
        return f"{DefaultValues.DEPARTMENT_PREFIX.value}{department_code}"

    @classmethod
    def _format_diagnosis(cls, sick_data: Dict[str, Any]) -> str:
        """
        Форматирование диагноза.

        :param sick_data: Данные о диагнозе
        :return: Отформатированный диагноз
        """
        return f"{sick_data.get('code', '')} {sick_data.get('name', '')}".strip()

    @classmethod
    def _apply_sort(cls, items: List, sort_by: str) -> List:
        """
        Применение сортировки к списку элементов.

        :param items: Список элементов
        :param sort_by: Поле для сортировки
        :return: Отсортированный список элементов
        """
        sort_mapping = {
            SortType.DATE_ASC.value: (lambda x: x.receipt_date, False),
            SortType.DATE_DESC.value: (lambda x: x.receipt_date, True),
            SortType.PATIENT_NAME_ASC.value: (lambda x: x.patient.full_name, False),
            SortType.PATIENT_NAME_DESC.value: (lambda x: x.patient.full_name, True)
        }

        if sort_by in sort_mapping:
            key_func, reverse = sort_mapping[sort_by]
            return sorted(items, key=key_func, reverse=reverse)

        return items

    @classmethod
    def _apply_pagination(cls, items: List, page: int, limit: int) -> tuple:
        """
        Применение пагинации к списку элементов.

        :param items: Список элементов
        :param page: Номер страницы
        :param limit: Количество элементов на странице
        :return: Кортеж из списка элементов на странице и общего количества страниц
        """
        total_pages = (len(items) + limit - 1) // limit if items else 0

        start_idx = (page - 1) * limit
        end_idx = start_idx + limit

        return items[start_idx:end_idx], total_pages

    @staticmethod
    def _format_period(start_date: str, end_date: str) -> str:
        """
        Форматирование периода госпитализации.

        :param start_date: Дата начала периода
        :param end_date: Дата окончания периода
        :return: Отформатированный период
        """
        if not start_date:
            return ""

        try:
            formatted_start = datetime.strptime(start_date.split("T")[0], "%Y-%m-%d").strftime("%d.%m.%Y")

            if end_date:
                formatted_end = datetime.strptime(end_date.split("T")[0], "%Y-%m-%d").strftime("%d.%m.%Y")
                return f"С {formatted_start} – По {formatted_end}"
            else:
                return f"С {formatted_start}"
        except (ValueError, TypeError):
            return ""

    @staticmethod
    def _calculate_age(birth_date: str) -> int:
        """
        Расчет возраста на основе даты рождения.

        :param birth_date: Дата рождения
        :return: Возраст
        """
        if not birth_date:
            return 0

        try:
            birth_date_obj = datetime.strptime(birth_date.split("T")[0], "%Y-%m-%d")
            current_date = datetime.now()

            age = current_date.year - birth_date_obj.year

            if (current_date.month, current_date.day) < (birth_date_obj.month, birth_date_obj.day):
                age -= 1

            return max(0, age)
        except (ValueError, TypeError):
            return 0

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
import re
from datetime import datetime
from typing import Dict, Any

from services.journal_base_service import JournalBaseService
from data_subjects.responses.newborns_response import (
    NewbornResponse, NewbornAsset, NewbornPatient, NewbornStatusColor, Mother
)
from data_subjects.requests.newborns_request import NewbornFilter
from data_subjects.enums.service_enums import (
    StatusColor, ContactInfo, PhonePattern, DefaultValues
)
from tests.constants import HOSPITAL_NAME, NEWBORN_MAX_AGE_DAYS


class NewbornsService(JournalBaseService[NewbornResponse, NewbornFilter]):
    """Сервис для обработки данных новорожденных."""

    @classmethod
    def _transform_data(cls, data: Dict[str, Any], filter_params: NewbornFilter) -> NewbornResponse:
        """Преобразование данных БГ в формат данных новорожденных."""
        items = []
        referral_items = data.get("referralItems", [])
        filtered_items = cls._apply_filter(referral_items, filter_params)

        for item in filtered_items:
            patient_data = item.get("patient", {})
            patient = NewbornPatient(
                id=patient_data.get("id", ""),
                iin=patient_data.get("personin", ""),
                full_name=patient_data.get("personFullName", ""),
                birth_date=patient_data.get("birthDate", "")
            )

            mother = cls._extract_mother_info(item.get("addiditonalInformation", ""))
            phone_number = cls._extract_phone_number(item.get("addiditonalInformation", ""))
            additional_info = cls._build_additional_info(item, mother, phone_number)

            asset = NewbornAsset(
                id=item.get("id", ""),
                number=item.get("protocolNumber", ""),
                receipt_date=item.get("regDate", ""),
                patient=patient,
                status_color=NewbornStatusColor.GREEN,  # Все новорожденные - зеленые (активные)
                additional_info=additional_info
            )
            items.append(asset)

        sorted_items = cls._apply_sort(items, filter_params.sort_by)
        paginated_items, total_pages = cls._apply_pagination(
            sorted_items, filter_params.page, filter_params.limit
        )

        return NewbornResponse(
            hospital_name=HOSPITAL_NAME,
            items=paginated_items,
            total=len(items),
            page=filter_params.page,
            limit=filter_params.limit,
            total_pages=total_pages
        )

    @classmethod
    def _extract_mother_info(cls, additional_info: str) -> Mother:
        """Извлечение информации о матери из дополнительной информации."""
        mother_name = DefaultValues.MOTHER_NAME.value

        if additional_info:
            mother_match = re.search(PhonePattern.MOTHER_REGEX.value, additional_info, re.IGNORECASE)
            if mother_match:
                mother_name = mother_match.group(1).strip()

        return Mother(
            id=None,
            iin=None,
            full_name=mother_name,
            birth_date=None
        )

    @classmethod
    def _build_additional_info(cls, item: Dict[str, Any], mother: Mother, phone_number: str) -> Dict[str, Any]:
        """Построение дополнительной информации для актива."""
        sick_data = item.get("sick", {})
        bed_profile = item.get("bedProfile", {})

        return {
            "executor": ContactInfo.DEFAULT_EXECUTOR.value,
            "diagnosis": cls._format_diagnosis(sick_data),
            "mother": mother,
            "phone": phone_number,
            "department": cls._format_department(bed_profile.get('code', ''))
        }

    @classmethod
    def _apply_filter(cls, items: list, filter_params: NewbornFilter) -> list:
        """Применение фильтров к списку элементов."""
        filtered_items = []
        date_from = datetime.strptime(filter_params.date_from, "%Y-%m-%d")
        date_to = datetime.strptime(filter_params.date_to, "%Y-%m-%d")

        for item in items:
            if not cls._is_date_in_range(item.get("regDate", ""), date_from, date_to):
                continue
            if not cls._is_patient_match_extended(item, filter_params.patient_identifier):
                continue
            if not cls._is_department_match(item, filter_params.department):
                continue
            if not cls._is_status_match(item, filter_params.status):
                continue

            filtered_items.append(item)
        return filtered_items

    @classmethod
    def _is_status_match(cls, item: Dict[str, Any], status) -> bool:
        """Проверка соответствия статуса фильтру."""
        if not status or status.value == "all":
            return True

        out_date = item.get("outDate")

        if status.value == "discharged":
            return bool(out_date)
        elif status.value == "active":
            return not out_date

        return True

    @classmethod
    def _is_newborn_by_age(cls, birth_date: str) -> bool:
        """Проверка, является ли пациент новорожденным по возрасту."""
        if not birth_date:
            return False

        try:
            birth_date_obj = datetime.strptime(birth_date.split("T")[0], "%Y-%m-%d")
            current_date = datetime.now()

            age_in_days = (current_date - birth_date_obj).days
            return age_in_days <= NEWBORN_MAX_AGE_DAYS
        except (ValueError, TypeError):
            return False

    @classmethod
    def _get_empty_response(cls, filter_params: NewbornFilter) -> NewbornResponse:
        """Получение пустого ответа с данными новорожденных."""
        return NewbornResponse(
            hospital_name=HOSPITAL_NAME,
            items=[],
            total=0,
            page=filter_params.page,
            limit=filter_params.limit,
            total_pages=0
        )
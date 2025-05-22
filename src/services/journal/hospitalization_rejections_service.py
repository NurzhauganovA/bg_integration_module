from datetime import datetime
from typing import Dict, Any

from services.journal_base_service import JournalBaseService
from data_subjects.responses.hospitalization_rejections_response import (
    RejectionResponse, RejectionAsset, RejectionPatient, RejectionStatusColor
)
from data_subjects.requests.hospitalization_rejections_request import RejectionFilter
from data_subjects.enums.service_enums import (
    RefusalStatus, StatusColor, ContactInfo, DefaultValues
)
from tests.constants import HOSPITAL_NAME


class HospitalizationRejectionsService(JournalBaseService[RejectionResponse, RejectionFilter]):
    """Сервис для обработки данных отказов от госпитализации."""

    @classmethod
    def _transform_data(cls, data: Dict[str, Any], filter_params: RejectionFilter) -> RejectionResponse:
        """Преобразование данных БГ в формат отказов от госпитализации."""
        items = []
        referral_items = data.get("referralItems", [])
        filtered_items = cls._apply_filter(referral_items, filter_params)

        for item in filtered_items:
            # Фильтруем только отказы
            if not cls._has_refusal(item):
                continue

            patient_data = item.get("patient", {})
            patient = RejectionPatient(
                id=patient_data.get("id", ""),
                iin=patient_data.get("personin", ""),
                full_name=patient_data.get("personFullName", ""),
                birth_date=patient_data.get("birthDate", "")
            )

            additional_info = cls._build_additional_info(item)

            asset = RejectionAsset(
                id=item.get("id", ""),
                number=item.get("protocolNumber", ""),
                receipt_date=item.get("regDate", ""),
                patient=patient,
                status_color=RejectionStatusColor.RED,  # Все отказы - красные
                additional_info=additional_info
            )
            items.append(asset)

        sorted_items = cls._apply_sort(items, filter_params.sort_by)
        paginated_items, total_pages = cls._apply_pagination(
            sorted_items, filter_params.page, filter_params.limit
        )

        return RejectionResponse(
            hospital_name=HOSPITAL_NAME,
            items=paginated_items,
            total=len(items),
            page=filter_params.page,
            limit=filter_params.limit,
            total_pages=total_pages
        )

    @classmethod
    def _has_refusal(cls, item: Dict[str, Any]) -> bool:
        """Проверка наличия отказа в записи."""
        return item.get("hasRefusal", "").lower() == RefusalStatus.TRUE.value

    @classmethod
    def _build_additional_info(cls, item: Dict[str, Any]) -> Dict[str, Any]:
        """Построение дополнительной информации для актива."""
        sick_data = item.get("sick", {})
        bed_profile = item.get("bedProfile", {})

        return {
            "diagnosis": cls._format_diagnosis(sick_data),
            "executor": ContactInfo.DEFAULT_EXECUTOR.value,
            "rejection_reason": item.get("refuseJustification", DefaultValues.REFUSAL_REASON.value),
            "department": cls._format_department(bed_profile.get('code', ''))
        }

    @classmethod
    def _apply_filter(cls, items: list, filter_params: RejectionFilter) -> list:
        """Применение фильтров к списку элементов."""
        filtered_items = []
        date_from = datetime.strptime(filter_params.date_from, "%Y-%m-%d")
        date_to = datetime.strptime(filter_params.date_to, "%Y-%m-%d")

        for item in items:
            # Проверяем, есть ли отказ
            if not cls._has_refusal(item):
                continue

            if not cls._is_date_in_range(item.get("regDate", ""), date_from, date_to):
                continue
            if not cls._is_patient_match(item, filter_params.patient_identifier):
                continue
            if not cls._is_department_match(item, filter_params.department):
                continue

            filtered_items.append(item)
        return filtered_items

    @classmethod
    def _get_empty_response(cls, filter_params: RejectionFilter) -> RejectionResponse:
        """Получение пустого ответа с отказами от госпитализации."""
        return RejectionResponse(
            hospital_name=HOSPITAL_NAME,
            items=[],
            total=0,
            page=filter_params.page,
            limit=filter_params.limit,
            total_pages=0
        )
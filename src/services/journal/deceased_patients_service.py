from datetime import datetime
from typing import Dict, Any

from services.journal_base_service import JournalBaseService
from data_subjects.responses.deceased_patients_response import (
    DeceasedResponse, DeceasedAsset, DeceasedPatientModel, DeceasedStatusColor
)
from data_subjects.requests.deceased_patients_request import DeceasedFilter
from data_subjects.enums.service_enums import (
    StatusColor, ContactInfo, MedicalPersonnel, TreatmentOutcome,
    DischargeOutcome, DeathMarker
)
from tests.constants import HOSPITAL_NAME


class DeceasedPatientsService(JournalBaseService[DeceasedResponse, DeceasedFilter]):
    """Сервис для обработки данных умерших пациентов."""

    @classmethod
    def _transform_data(cls, data: Dict[str, Any], filter_params: DeceasedFilter) -> DeceasedResponse:
        """Преобразование данных БГ в формат данных умерших пациентов."""
        items = []
        referral_items = data.get("referralItems", [])
        filtered_items = cls._apply_filter(referral_items, filter_params)

        for item in filtered_items:
            patient_data = item.get("patient", {})
            patient = DeceasedPatientModel(
                id=patient_data.get("id", ""),
                iin=patient_data.get("personin", ""),
                full_name=patient_data.get("personFullName", ""),
                birth_date=patient_data.get("birthDate", "")
            )

            phone_number = cls._extract_phone_number(item.get("addiditonalInformation", ""))
            address = item.get("address", ContactInfo.DEFAULT_ADDRESS.value)
            additional_info = cls._build_additional_info(item, phone_number, address)

            asset = DeceasedAsset(
                id=item.get("id", ""),
                number=item.get("protocolNumber", ""),
                receipt_date=item.get("regDate", ""),
                patient=patient,
                status_color=DeceasedStatusColor.RED,  # Все умершие - красные
                additional_info=additional_info
            )
            items.append(asset)

        sorted_items = cls._apply_sort(items, filter_params.sort_by)
        paginated_items, total_pages = cls._apply_pagination(
            sorted_items, filter_params.page, filter_params.limit
        )

        return DeceasedResponse(
            hospital_name=HOSPITAL_NAME,
            items=paginated_items,
            total=len(items),
            page=filter_params.page,
            limit=filter_params.limit,
            total_pages=total_pages
        )

    @classmethod
    def _build_additional_info(cls, item: Dict[str, Any], phone_number: str, address: str) -> Dict[str, Any]:
        """Построение дополнительной информации для актива."""
        sick_data = item.get("sick", {})
        bed_profile = item.get("bedProfile", {})

        return {
            "phone": phone_number,
            "address": address,
            "treatment_outcome": TreatmentOutcome.DEATH.value,
            "discharge_outcome": DischargeOutcome.DIED.value,
            "hospitalization_period": cls._format_period(item.get("hospitalDate"), item.get("outDate")),
            "diagnosis": cls._format_diagnosis(sick_data),
            "specialist": item.get("directDoctor", MedicalPersonnel.DEFAULT_SPECIALIST.value),
            "department": cls._format_department(bed_profile.get('code', ''))
        }

    @classmethod
    def _apply_filter(cls, items: list, filter_params: DeceasedFilter) -> list:
        """Применение фильтров к списку элементов."""
        filtered_items = []
        date_from = datetime.strptime(filter_params.date_from, "%Y-%m-%d")
        date_to = datetime.strptime(filter_params.date_to, "%Y-%m-%d")

        for item in items:
            if not cls._is_date_in_range(item.get("regDate", ""), date_from, date_to):
                continue
            if not cls._is_patient_match(item, filter_params.patient_identifier):
                continue
            if not cls._is_department_match(item, filter_params.department):
                continue
            if not cls._has_death_markers(item):
                continue

            filtered_items.append(item)
        return filtered_items

    @classmethod
    def _has_death_markers(cls, item: Dict[str, Any]) -> bool:
        """Проверка наличия маркеров смерти в записи."""
        additional_info = item.get("addiditonalInformation", "").lower()

        death_markers = [
            DeathMarker.DEATH.value, DeathMarker.DIED.value,
            DeathMarker.FATAL.value, DeathMarker.DECEASED.value
        ]

        for marker in death_markers:
            if marker in additional_info:
                return True

        if item.get("outDate"):
            return True

        return False

    @classmethod
    def _get_empty_response(cls, filter_params: DeceasedFilter) -> DeceasedResponse:
        """Получение пустого ответа с данными умерших пациентов."""
        return DeceasedResponse(
            hospital_name=HOSPITAL_NAME,
            items=[],
            total=0,
            page=filter_params.page,
            limit=filter_params.limit,
            total_pages=0
        )
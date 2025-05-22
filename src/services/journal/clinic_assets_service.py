from datetime import datetime
from typing import Dict, Any

from services.journal_base_service import JournalBaseService
from data_subjects.responses.clinic_assets_response import (
    ClinicResponse, ClinicAsset, ClinicPatient, ClinicStatusColor, ClinicDoctor
)
from data_subjects.requests.clinic_assets_request import ClinicFilter
from data_subjects.enums.service_enums import StatusColor, ContactInfo, MedicalPersonnel
from tests.constants import HOSPITAL_NAME


class ClinicAssetsService(JournalBaseService[ClinicResponse, ClinicFilter]):
    """Сервис для обработки данных активов поликлиники."""

    @classmethod
    def _transform_data(cls, data: Dict[str, Any], filter_params: ClinicFilter) -> ClinicResponse:
        """Преобразование данных БГ в формат активов поликлиники."""
        items = []
        referral_items = data.get("referralItems", [])
        filtered_items = cls._apply_filter(referral_items, filter_params)

        for item in filtered_items:
            patient_data = item.get("patient", {})
            patient = ClinicPatient(
                id=patient_data.get("id", ""),
                iin=patient_data.get("personin", ""),
                full_name=patient_data.get("personFullName", ""),
                birth_date=patient_data.get("birthDate", "")
            )

            doctor = cls._create_doctor(item)
            phone_number = cls._extract_phone_number(item.get("addiditonalInformation", ""))
            address = item.get("address", ContactInfo.DEFAULT_ADDRESS.value)
            additional_info = cls._build_additional_info(item, phone_number, address, doctor.full_name)

            asset = ClinicAsset(
                id=item.get("id", ""),
                number=item.get("protocolNumber", ""),
                receipt_date=item.get("regDate", ""),
                patient=patient,
                doctor=doctor,
                status_color=ClinicStatusColor.YELLOW,  # Все записи поликлиники - желтые (запланировано)
                additional_info=additional_info
            )
            items.append(asset)

        sorted_items = cls._apply_sort(items, filter_params.sort_by)
        paginated_items, total_pages = cls._apply_pagination(
            sorted_items, filter_params.page, filter_params.limit
        )

        return ClinicResponse(
            hospital_name=HOSPITAL_NAME,
            items=paginated_items,
            total=len(items),
            page=filter_params.page,
            limit=filter_params.limit,
            total_pages=total_pages
        )

    @classmethod
    def _create_doctor(cls, item: Dict[str, Any]) -> ClinicDoctor:
        """Создание объекта врача."""
        doctor_name = item.get("directDoctor", MedicalPersonnel.DEFAULT_DOCTOR.value)

        return ClinicDoctor(
            id="",
            full_name=doctor_name,
            specialization=MedicalPersonnel.DEFAULT_SPECIALIZATION.value,
            department=MedicalPersonnel.DEFAULT_DEPARTMENT_NAME.value
        )

    @classmethod
    def _build_additional_info(cls, item: Dict[str, Any], phone_number: str, address: str, doctor_name: str) -> Dict[
        str, Any]:
        """Построение дополнительной информации для актива."""
        bed_profile = item.get("bedProfile", {})

        return {
            "address": address,
            "phone": phone_number,
            "specialist": doctor_name,
            "executor": ContactInfo.DEFAULT_EXECUTOR.value,
            "department": cls._format_department(bed_profile.get('code', ''))
        }

    @classmethod
    def _apply_filter(cls, items: list, filter_params: ClinicFilter) -> list:
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

            filtered_items.append(item)
        return filtered_items

    @classmethod
    def _get_empty_response(cls, filter_params: ClinicFilter) -> ClinicResponse:
        """Получение пустого ответа с активами поликлиники."""
        return ClinicResponse(
            hospital_name=HOSPITAL_NAME,
            items=[],
            total=0,
            page=filter_params.page,
            limit=filter_params.limit,
            total_pages=0
        )
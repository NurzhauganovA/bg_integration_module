from datetime import datetime
from typing import Dict, Any

from services.journal_base_service import JournalBaseService
from data_subjects.responses.maternity_assets_response import (
    MaternityResponse, MaternityAsset, MaternityPatient, MaternityStatusColor
)
from data_subjects.requests.maternity_assets_request import MaternityFilter
from data_subjects.enums.service_enums import (
    GenderCode, StatusColor, ContactInfo, MedicalPersonnel,
    TreatmentOutcome, DischargeOutcome
)
from tests.constants import HOSPITAL_NAME


class MaternityAssetsService(JournalBaseService[MaternityResponse, MaternityFilter]):
    """Сервис для обработки данных активов роддома."""

    @classmethod
    def _transform_data(cls, data: Dict[str, Any], filter_params: MaternityFilter) -> MaternityResponse:
        """Преобразование данных БГ в формат активов роддома."""
        items = []
        referral_items = data.get("referralItems", [])
        filtered_items = cls._apply_filter(referral_items, filter_params)

        for item in filtered_items:
            patient_data = item.get("patient", {})
            patient = MaternityPatient(
                id=patient_data.get("id", ""),
                iin=patient_data.get("personin", ""),
                full_name=patient_data.get("personFullName", ""),
                birth_date=patient_data.get("birthDate", "")
            )

            phone_number = cls._extract_phone_number(item.get("addiditonalInformation", ""))
            address = item.get("address", ContactInfo.DEFAULT_ADDRESS.value)
            status_color = cls._determine_status_color(item)
            additional_info = cls._build_additional_info(item, phone_number, address, status_color)

            asset = MaternityAsset(
                id=item.get("id", ""),
                number=item.get("protocolNumber", ""),
                receipt_date=item.get("regDate", ""),
                patient=patient,
                status_color=status_color,
                additional_info=additional_info
            )
            items.append(asset)

        sorted_items = cls._apply_sort(items, filter_params.sort_by)
        paginated_items, total_pages = cls._apply_pagination(
            sorted_items, filter_params.page, filter_params.limit
        )

        return MaternityResponse(
            hospital_name=HOSPITAL_NAME,
            items=paginated_items,
            total=len(items),
            page=filter_params.page,
            limit=filter_params.limit,
            total_pages=total_pages
        )

    @classmethod
    def _determine_status_color(cls, item: Dict[str, Any]) -> MaternityStatusColor:
        """Определение цвета статуса на основе данных."""
        out_date = item.get("outDate")
        return MaternityStatusColor.GRAY if out_date else MaternityStatusColor.GREEN

    @classmethod
    def _build_additional_info(cls, item: Dict[str, Any], phone_number: str, address: str,
                               status_color: MaternityStatusColor) -> Dict[str, Any]:
        """Построение дополнительной информации для актива."""
        sick_data = item.get("sick", {})
        bed_profile = item.get("bedProfile", {})
        out_date = item.get("outDate")

        return {
            "phone": phone_number,
            "address": address,
            "treatment_outcome": TreatmentOutcome.IMPROVEMENT.value,
            "discharge_outcome": DischargeOutcome.DISCHARGED.value if out_date else None,
            "diagnosis": cls._format_diagnosis(sick_data),
            "specialist": item.get("directDoctor", MedicalPersonnel.DEFAULT_SPECIALIST.value),
            "executor": ContactInfo.DEFAULT_EXECUTOR.value,
            "department": cls._format_department(bed_profile.get('code', ''))
        }

    @classmethod
    def _apply_filter(cls, items: list, filter_params: MaternityFilter) -> list:
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
            if not cls._is_status_match(item, filter_params.status):
                continue
            if not cls._is_maternity_related(item):
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
    def _is_maternity_related(cls, item: Dict[str, Any]) -> bool:
        """Проверка, относится ли запись к роддому."""
        patient_data = item.get("patient", {})
        sex_code = patient_data.get("sexIdCode", "")

        if sex_code == GenderCode.FEMALE.value:
            return True

        return False

    @classmethod
    def _get_empty_response(cls, filter_params: MaternityFilter) -> MaternityResponse:
        """Получение пустого ответа с активами роддома."""
        return MaternityResponse(
            hospital_name=HOSPITAL_NAME,
            items=[],
            total=0,
            page=filter_params.page,
            limit=filter_params.limit,
            total_pages=0
        )
from datetime import datetime
from typing import Dict, Any

from services.journal_base_service import JournalBaseService
from data_subjects.responses.hospital_assets_response import (
    HospitalAssetsResponse, HospitalAsset, HospitalPatient,
    HospitalStatus, HospitalStatusColor
)
from data_subjects.requests.hospital_assets_request import HospitalAssetsFilter
from data_subjects.enums.service_enums import (
    ConfirmStatus, TreatmentOutcome, DischargeOutcome,
    ContactInfo, StatusColor
)
from tests.constants import HOSPITAL_NAME


class HospitalAssetsService(JournalBaseService[HospitalAssetsResponse, HospitalAssetsFilter]):
    """Сервис для обработки данных активов стационара."""

    @classmethod
    def _transform_data(cls, data: Dict[str, Any], filter_params: HospitalAssetsFilter) -> HospitalAssetsResponse:
        """
        Преобразование данных БГ в формат активов стационара.
        """
        items = []
        referral_items = data.get("referralItems", [])
        filtered_items = cls._apply_filter(referral_items, filter_params)

        for item in filtered_items:
            patient_data = item.get("patient", {})
            patient = HospitalPatient(
                id=patient_data.get("id", ""),
                iin=patient_data.get("personin", ""),
                full_name=patient_data.get("personFullName", ""),
                birth_date=patient_data.get("birthDate", "")
            )

            status, status_color = cls._determine_patient_status(item)
            additional_info = cls._build_additional_info(item)

            asset = HospitalAsset(
                id=item.get("id", ""),
                number=item.get("protocolNumber", ""),
                receipt_date=item.get("regDate", ""),
                patient=patient,
                status=status,
                status_color=status_color,
                additional_info=additional_info
            )
            items.append(asset)

        sorted_items = cls._apply_sort(items, filter_params.sort_by)
        paginated_items, total_pages = cls._apply_pagination(
            sorted_items, filter_params.page, filter_params.limit
        )

        return HospitalAssetsResponse(
            hospital_name=HOSPITAL_NAME,
            items=paginated_items,
            total=len(items),
            page=filter_params.page,
            limit=filter_params.limit,
            total_pages=total_pages
        )

    @classmethod
    def _determine_patient_status(cls, item: Dict[str, Any]) -> tuple[HospitalStatus, HospitalStatusColor]:
        """Определение статуса пациента на основе данных."""
        has_confirm = item.get("hasConfirm", "").lower() == ConfirmStatus.TRUE.value
        out_date = item.get("outDate")

        if out_date:
            return HospitalStatus.DISCHARGED, HospitalStatusColor.GRAY
        elif has_confirm:
            return HospitalStatus.HOSPITALIZED, HospitalStatusColor.BLUE
        else:
            return HospitalStatus.WAITING, HospitalStatusColor.GREEN

    @classmethod
    def _build_additional_info(cls, item: Dict[str, Any]) -> Dict[str, Any]:
        """Построение дополнительной информации для актива."""
        out_date = item.get("outDate")
        sick_data = item.get("sick", {})
        bed_profile = item.get("bedProfile", {})

        return {
            "treatment_outcome": TreatmentOutcome.IMPROVEMENT.value,
            "discharge_outcome": DischargeOutcome.DISCHARGED.value if out_date else None,
            "hospitalization_period": cls._format_period(item.get("hospitalDate"), out_date),
            "diagnosis": cls._format_diagnosis(sick_data),
            "doctor": item.get("directDoctor", ""),
            "executor": ContactInfo.DEFAULT_EXECUTOR.value,
            "department": cls._format_department(bed_profile.get('code', ''))
        }

    @classmethod
    def _apply_filter(cls, items: list, filter_params: HospitalAssetsFilter) -> list:
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

            filtered_items.append(item)
        return filtered_items

    @classmethod
    def _is_status_match(cls, item: Dict[str, Any], status) -> bool:
        """Проверка соответствия статуса фильтру."""
        if not status or status.value == "all":
            return True

        has_confirm = item.get("hasConfirm", "").lower() == ConfirmStatus.TRUE.value
        out_date = item.get("outDate")

        if status.value == "hospitalized":
            return has_confirm and not out_date
        elif status.value == "waiting":
            return not has_confirm and not out_date
        elif status.value == "discharged":
            return bool(out_date)

        return True

    @classmethod
    def _get_empty_response(cls, filter_params: HospitalAssetsFilter) -> HospitalAssetsResponse:
        """Получение пустого ответа с активами стационара."""
        return HospitalAssetsResponse(
            hospital_name=HOSPITAL_NAME,
            items=[],
            total=0,
            page=filter_params.page,
            limit=filter_params.limit,
            total_pages=0
        )
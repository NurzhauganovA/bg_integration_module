import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime

from services.journal.deceased_patients_service import DeceasedPatientsService
from data_subjects.requests.deceased_patients_request import DeceasedFilter
from data_subjects.responses.deceased_patients_response import DeceasedStatusColor
from data_subjects.enums.service_enums import (
    ContactInfo, MedicalPersonnel, TreatmentOutcome, DischargeOutcome, DeathMarker
)
from integration_sdk_orkendeu_mis.handlers.dto.handler_result_dto import HandlerResultDTO
from tests.constants import *


class TestDeceasedPatientsService:
    """Тесты для сервиса умерших пациентов."""

    @pytest.mark.asyncio
    async def test_get_data_success(self, mock_journal_base_service, referrals_json_data):
        """Проверка успешного получения и преобразования данных."""
        for item in referrals_json_data:
            item["addiditonalInformation"] = DEATH_MARKER
            item["outDate"] = TEST_OUT_DATE

        mock_journal_base_service.return_value = HandlerResultDTO(
            success=True,
            data={"referralItems": referrals_json_data}
        )

        filter_params = DeceasedFilter(
            date_from=TEST_DATE_FROM,
            date_to=TEST_DATE_TO,
            patient_identifier=TEST_PATIENT_IIN,
            department=TEST_DEPARTMENT_CODE
        )

        result = await DeceasedPatientsService.get_data(filter_params)

        assert result.hospital_name == HOSPITAL_NAME
        assert isinstance(result.items, list)
        assert result.page == filter_params.page
        assert result.limit == filter_params.limit

        for item in result.items:
            assert item.status_color == DeceasedStatusColor.RED

    @pytest.mark.asyncio
    async def test_get_data_empty(self, mock_journal_base_service):
        """Проверка получения пустого ответа при отсутствии данных."""
        mock_journal_base_service.return_value = HandlerResultDTO(
            success=False,
            error=ERROR_NO_DATA_FOUND,
            status_code=HTTP_NOT_FOUND
        )

        filter_params = DeceasedFilter(
            date_from=TEST_DATE_FROM,
            date_to=TEST_DATE_TO
        )

        result = await DeceasedPatientsService.get_data(filter_params)

        assert result.hospital_name == HOSPITAL_NAME
        assert result.items == []
        assert result.total == 0
        assert result.page == filter_params.page
        assert result.limit == filter_params.limit
        assert result.total_pages == 0

    def test_transform_data(self, referrals_json_data):
        """Проверка преобразования данных из БГ в формат умерших пациентов."""
        for item in referrals_json_data:
            item["addiditonalInformation"] = DEATH_MARKER
            item["outDate"] = TEST_OUT_DATE

        filter_params = DeceasedFilter(
            date_from=TEST_DATE_FROM,
            date_to=TEST_DATE_TO
        )

        result = DeceasedPatientsService._transform_data(
            {"referralItems": referrals_json_data},
            filter_params
        )

        assert result.hospital_name == HOSPITAL_NAME
        assert isinstance(result.items, list)

        if result.items:
            item = result.items[0]
            assert hasattr(item, "id")
            assert hasattr(item, "patient")
            assert hasattr(item, "status_color")
            assert hasattr(item, "additional_info")
            assert item.status_color == DeceasedStatusColor.RED

            assert "treatment_outcome" in item.additional_info
            assert "discharge_outcome" in item.additional_info
            assert item.additional_info["treatment_outcome"] == TreatmentOutcome.DEATH.value
            assert item.additional_info["discharge_outcome"] == DischargeOutcome.DIED.value

    def test_build_additional_info(self):
        """Проверка построения дополнительной информации для актива."""
        item = {
            "sick": {
                "code": TEST_SICK_CODE,
                "name": TEST_SICK_NAME
            },
            "bedProfile": {
                "code": TEST_DEPARTMENT_CODE
            },
            "directDoctor": TEST_DOCTOR_NAME,
            "hospitalDate": TEST_REG_DATE,
            "outDate": TEST_OUT_DATE
        }

        phone_number = TEST_PHONE_NUMBER
        address = TEST_ADDRESS

        additional_info = DeceasedPatientsService._build_additional_info(item, phone_number, address)

        assert additional_info["phone"] == phone_number
        assert additional_info["address"] == address
        assert additional_info["treatment_outcome"] == TreatmentOutcome.DEATH.value
        assert additional_info["discharge_outcome"] == DischargeOutcome.DIED.value
        assert "hospitalization_period" in additional_info
        assert additional_info["diagnosis"] == f"{TEST_SICK_CODE} {TEST_SICK_NAME}"
        assert additional_info["specialist"] == TEST_DOCTOR_NAME
        assert additional_info["department"] == f"№{TEST_DEPARTMENT_CODE}"

    def test_has_death_markers(self):
        """Проверка наличия маркеров смерти в записи."""
        item_with_death_marker = {
            "addiditonalInformation": DEATH_MARKER
        }
        assert DeceasedPatientsService._has_death_markers(item_with_death_marker)

        item_with_out_date = {
            "addiditonalInformation": "",
            "outDate": TEST_OUT_DATE
        }
        assert DeceasedPatientsService._has_death_markers(item_with_out_date)

        item_without_markers = {
            "addiditonalInformation": "обычная информация"
        }
        assert not DeceasedPatientsService._has_death_markers(item_without_markers)

    def test_apply_filter(self, referrals_json_data):
        """Проверка применения фильтра к списку элементов."""
        for item in referrals_json_data:
            item["addiditonalInformation"] = DEATH_MARKER
            item["outDate"] = TEST_OUT_DATE

        filter_params = DeceasedFilter(
            date_from=TEST_DATE_FROM,
            date_to=TEST_DATE_TO,
            patient_identifier=TEST_PATIENT_IIN,
            department=TEST_DEPARTMENT_CODE
        )

        filtered_items = DeceasedPatientsService._apply_filter(
            referrals_json_data,
            filter_params
        )

        for item in filtered_items:
            reg_date = datetime.strptime(item["regDate"].split("T")[0], "%Y-%m-%d")
            assert datetime(2025, 1, 1) <= reg_date <= datetime(2025, 12, 31)

            if filter_params.patient_identifier:
                patient_data = item.get("patient", {})
                patient_iin = patient_data.get("personin", "")
                patient_name = patient_data.get("personFullName", "").lower()
                assert (filter_params.patient_identifier.lower() in patient_name or
                        filter_params.patient_identifier == patient_iin)

            if filter_params.department != "all":
                department = item.get("bedProfile", {}).get("code", "")
                assert department == filter_params.department

            assert DEATH_MARKER.lower() in item.get("addiditonalInformation", "").lower() or item.get("outDate")

    def test_get_empty_response(self):
        """Проверка получения пустого ответа."""
        filter_params = DeceasedFilter(
            date_from=TEST_DATE_FROM,
            date_to=TEST_DATE_TO,
            page=TEST_PAGE_NUMBER,
            limit=TEST_PAGE_SIZE
        )

        result = DeceasedPatientsService._get_empty_response(filter_params)

        assert result.hospital_name == HOSPITAL_NAME
        assert result.items == []
        assert result.total == 0
        assert result.page == TEST_PAGE_NUMBER
        assert result.limit == TEST_PAGE_SIZE
        assert result.total_pages == 0
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime

from services.journal.clinic_assets_service import ClinicAssetsService
from data_subjects.requests.clinic_assets_request import ClinicFilter, ClinicStatus
from data_subjects.responses.clinic_assets_response import ClinicStatusColor
from data_subjects.enums.service_enums import ContactInfo, MedicalPersonnel
from integration_sdk_orkendeu_mis.handlers.dto.handler_result_dto import HandlerResultDTO
from tests.constants import *


class TestClinicAssetsService:
    """Тесты для сервиса активов поликлиники."""

    @pytest.mark.asyncio
    async def test_get_data_success(self, mock_journal_base_service, referrals_json_data):
        """Проверка успешного получения и преобразования данных."""
        mock_journal_base_service.return_value = HandlerResultDTO(
            success=True,
            data={"referralItems": referrals_json_data}
        )

        filter_params = ClinicFilter(
            date_from=TEST_DATE_FROM,
            date_to=TEST_DATE_TO,
            patient_identifier=TEST_PATIENT_IIN,
            department=TEST_DEPARTMENT_CODE,
            status=ClinicStatus.SCHEDULED
        )

        result = await ClinicAssetsService.get_data(filter_params)

        assert result.hospital_name == HOSPITAL_NAME
        assert isinstance(result.items, list)
        assert result.page == filter_params.page
        assert result.limit == filter_params.limit

    @pytest.mark.asyncio
    async def test_get_data_empty(self, mock_journal_base_service):
        """Проверка получения пустого ответа при отсутствии данных."""
        mock_journal_base_service.return_value = HandlerResultDTO(
            success=False,
            error=ERROR_NO_DATA_FOUND,
            status_code=HTTP_NOT_FOUND
        )

        filter_params = ClinicFilter(
            date_from=TEST_DATE_FROM,
            date_to=TEST_DATE_TO
        )

        result = await ClinicAssetsService.get_data(filter_params)

        assert result.hospital_name == HOSPITAL_NAME
        assert result.items == []
        assert result.total == 0
        assert result.page == filter_params.page
        assert result.limit == filter_params.limit
        assert result.total_pages == 0

    def test_transform_data(self, referrals_json_data):
        """Проверка преобразования данных из БГ в формат активов поликлиники."""
        filter_params = ClinicFilter(
            date_from=TEST_DATE_FROM,
            date_to=TEST_DATE_TO
        )

        result = ClinicAssetsService._transform_data(
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
            assert hasattr(item, "doctor")
            assert hasattr(item, "additional_info")
            assert item.status_color == ClinicStatusColor.YELLOW

    def test_create_doctor(self):
        """Проверка создания объекта врача."""
        item_with_doctor = {
            "directDoctor": TEST_DOCTOR_NAME
        }

        doctor = ClinicAssetsService._create_doctor(item_with_doctor)

        assert doctor.full_name == TEST_DOCTOR_NAME
        assert doctor.specialization == MedicalPersonnel.DEFAULT_SPECIALIZATION.value
        assert doctor.department == MedicalPersonnel.DEFAULT_DEPARTMENT_NAME.value

        item_without_doctor = {}

        doctor = ClinicAssetsService._create_doctor(item_without_doctor)

        assert doctor.full_name == MedicalPersonnel.DEFAULT_DOCTOR.value

    def test_build_additional_info(self):
        """Проверка построения дополнительной информации для актива."""
        item = {
            "address": TEST_ADDRESS,
            "bedProfile": {
                "code": TEST_DEPARTMENT_CODE
            }
        }

        phone_number = TEST_PHONE_NUMBER
        address = TEST_ADDRESS
        doctor_name = TEST_DOCTOR_NAME

        additional_info = ClinicAssetsService._build_additional_info(
            item, phone_number, address, doctor_name
        )

        assert additional_info["address"] == address
        assert additional_info["phone"] == phone_number
        assert additional_info["specialist"] == doctor_name
        assert additional_info["executor"] == ContactInfo.DEFAULT_EXECUTOR.value
        assert additional_info["department"] == f"№{TEST_DEPARTMENT_CODE}"

    def test_apply_filter(self, referrals_json_data):
        """Проверка применения фильтра к списку элементов."""
        filter_params = ClinicFilter(
            date_from=TEST_DATE_FROM,
            date_to=TEST_DATE_TO,
            patient_identifier=TEST_PATIENT_IIN,
            department=TEST_DEPARTMENT_CODE,
            status=ClinicStatus.ALL
        )

        filtered_items = ClinicAssetsService._apply_filter(
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

    def test_get_empty_response(self):
        """Проверка получения пустого ответа."""
        filter_params = ClinicFilter(
            date_from=TEST_DATE_FROM,
            date_to=TEST_DATE_TO,
            page=TEST_PAGE_NUMBER,
            limit=TEST_PAGE_SIZE
        )

        result = ClinicAssetsService._get_empty_response(filter_params)

        assert result.hospital_name == HOSPITAL_NAME
        assert result.items == []
        assert result.total == 0
        assert result.page == TEST_PAGE_NUMBER
        assert result.limit == TEST_PAGE_SIZE
        assert result.total_pages == 0
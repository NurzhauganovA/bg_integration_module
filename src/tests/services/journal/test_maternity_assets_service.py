import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime

from services.journal.maternity_assets_service import MaternityAssetsService
from data_subjects.requests.maternity_assets_request import MaternityFilter, MaternityStatus
from data_subjects.responses.maternity_assets_response import MaternityStatusColor
from data_subjects.enums.service_enums import (
    GenderCode, ContactInfo, MedicalPersonnel, TreatmentOutcome, DischargeOutcome
)
from integration_sdk_orkendeu_mis.handlers.dto.handler_result_dto import HandlerResultDTO
from tests.constants import *


class TestMaternityAssetsService:
    """Тесты для сервиса активов роддома."""

    @pytest.mark.asyncio
    async def test_get_data_success(self, mock_journal_base_service, referrals_json_data):
        """Проверка успешного получения и преобразования данных."""
        for item in referrals_json_data:
            patient_data = item.get("patient", {})
            patient_data["sexIdCode"] = FEMALE_SEX_CODE

        mock_journal_base_service.return_value = HandlerResultDTO(
            success=True,
            data={"referralItems": referrals_json_data}
        )

        filter_params = MaternityFilter(
            date_from=TEST_DATE_FROM,
            date_to=TEST_DATE_TO,
            patient_identifier=TEST_PATIENT_IIN,
            department=TEST_DEPARTMENT_CODE,
            status=MaternityStatus.ACTIVE
        )

        result = await MaternityAssetsService.get_data(filter_params)

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

        filter_params = MaternityFilter(
            date_from=TEST_DATE_FROM,
            date_to=TEST_DATE_TO
        )

        result = await MaternityAssetsService.get_data(filter_params)

        assert result.hospital_name == HOSPITAL_NAME
        assert result.items == []
        assert result.total == 0
        assert result.page == filter_params.page
        assert result.limit == filter_params.limit
        assert result.total_pages == 0

    def test_transform_data(self, referrals_json_data):
        """Проверка преобразования данных из БГ в формат активов роддома."""
        for item in referrals_json_data:
            patient_data = item.get("patient", {})
            patient_data["sexIdCode"] = FEMALE_SEX_CODE

        filter_params = MaternityFilter(
            date_from=TEST_DATE_FROM,
            date_to=TEST_DATE_TO
        )

        result = MaternityAssetsService._transform_data(
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
            assert item.status_color == MaternityStatusColor.GREEN

            assert "phone" in item.additional_info
            assert "address" in item.additional_info
            assert "specialist" in item.additional_info
            assert "executor" in item.additional_info
            assert "department" in item.additional_info

    def test_determine_status_color(self):
        """Проверка определения цвета статуса."""
        item_active = {
            "outDate": None
        }
        color = MaternityAssetsService._determine_status_color(item_active)
        assert color == MaternityStatusColor.GREEN

        item_discharged = {
            "outDate": TEST_OUT_DATE
        }
        color = MaternityAssetsService._determine_status_color(item_discharged)
        assert color == MaternityStatusColor.GRAY

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
            "outDate": None
        }

        phone_number = TEST_PHONE_NUMBER
        address = TEST_ADDRESS
        status_color = MaternityStatusColor.GREEN

        additional_info = MaternityAssetsService._build_additional_info(
            item, phone_number, address, status_color
        )

        assert additional_info["phone"] == phone_number
        assert additional_info["address"] == address
        assert additional_info["treatment_outcome"] == TreatmentOutcome.IMPROVEMENT.value
        assert additional_info["discharge_outcome"] is None
        assert additional_info["diagnosis"] == f"{TEST_SICK_CODE} {TEST_SICK_NAME}"
        assert additional_info["specialist"] == TEST_DOCTOR_NAME
        assert additional_info["executor"] == ContactInfo.DEFAULT_EXECUTOR.value
        assert additional_info["department"] == f"№{TEST_DEPARTMENT_CODE}"

    def test_is_status_match(self):
        """Проверка соответствия статуса фильтру."""
        item_active = {"outDate": None}
        assert MaternityAssetsService._is_status_match(item_active, MaternityStatus.ALL)
        assert MaternityAssetsService._is_status_match(item_active, MaternityStatus.ACTIVE)
        assert not MaternityAssetsService._is_status_match(item_active, MaternityStatus.DISCHARGED)

        item_discharged = {"outDate": TEST_OUT_DATE}
        assert MaternityAssetsService._is_status_match(item_discharged, MaternityStatus.ALL)
        assert MaternityAssetsService._is_status_match(item_discharged, MaternityStatus.DISCHARGED)
        assert not MaternityAssetsService._is_status_match(item_discharged, MaternityStatus.ACTIVE)

    def test_is_maternity_related(self):
        """Проверка принадлежности записи к роддому."""
        item_female = {
            "patient": {
                "sexIdCode": FEMALE_SEX_CODE
            }
        }
        assert MaternityAssetsService._is_maternity_related(item_female)

        item_male = {
            "patient": {
                "sexIdCode": MALE_SEX_CODE
            }
        }
        assert not MaternityAssetsService._is_maternity_related(item_male)

        item_unknown = {
            "patient": {
                "sexIdCode": UNKNOWN_SEX_CODE
            }
        }
        assert not MaternityAssetsService._is_maternity_related(item_unknown)

    def test_apply_filter(self, referrals_json_data):
        """Проверка применения фильтра к списку элементов."""
        for item in referrals_json_data:
            patient_data = item.get("patient", {})
            patient_data["sexIdCode"] = FEMALE_SEX_CODE

        filter_params = MaternityFilter(
            date_from=TEST_DATE_FROM,
            date_to=TEST_DATE_TO,
            patient_identifier=TEST_PATIENT_IIN,
            department=TEST_DEPARTMENT_CODE,
            status=MaternityStatus.ACTIVE
        )

        filtered_items = MaternityAssetsService._apply_filter(
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

            patient_data = item.get("patient", {})
            assert patient_data.get("sexIdCode") == FEMALE_SEX_CODE

            if filter_params.status == MaternityStatus.ACTIVE:
                assert "outDate" not in item or not item["outDate"]

    def test_get_empty_response(self):
        """Проверка получения пустого ответа."""
        filter_params = MaternityFilter(
            date_from=TEST_DATE_FROM,
            date_to=TEST_DATE_TO,
            page=TEST_PAGE_NUMBER,
            limit=TEST_PAGE_SIZE
        )

        result = MaternityAssetsService._get_empty_response(filter_params)

        assert result.hospital_name == HOSPITAL_NAME
        assert result.items == []
        assert result.total == 0
        assert result.page == TEST_PAGE_NUMBER
        assert result.limit == TEST_PAGE_SIZE
        assert result.total_pages == 0
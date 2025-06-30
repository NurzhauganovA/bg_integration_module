import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime

from services.journal.hospital_assets_service import HospitalAssetsService
from data_subjects.requests.hospital_assets_request import HospitalAssetsFilter, HospitalAssetStatus
from data_subjects.responses.hospital_assets_response import HospitalStatus, HospitalStatusColor
from data_subjects.enums.service_enums import ConfirmStatus, TreatmentOutcome, DischargeOutcome
from integration_sdk_orkendeu_mis.handlers.dto.handler_result_dto import HandlerResultDTO
from tests.constants import *


class TestHospitalAssetsService:
    """Тесты для сервиса активов стационара."""

    @pytest.mark.asyncio
    async def test_get_data_success(self, mock_journal_base_service, referrals_json_data):
        """Проверка успешного получения и преобразования данных."""
        mock_journal_base_service.return_value = HandlerResultDTO(
            success=True,
            data={"referralItems": referrals_json_data}
        )

        filter_params = HospitalAssetsFilter(
            date_from=TEST_DATE_FROM,
            date_to=TEST_DATE_TO,
            patient_identifier=TEST_PATIENT_IIN,
            department=TEST_DEPARTMENT_CODE,
            status=HospitalAssetStatus.HOSPITALIZED
        )

        result = await HospitalAssetsService.get_data(filter_params)

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

        filter_params = HospitalAssetsFilter(
            date_from=TEST_DATE_FROM,
            date_to=TEST_DATE_TO
        )

        result = await HospitalAssetsService.get_data(filter_params)

        assert result.hospital_name == HOSPITAL_NAME
        assert result.items == []
        assert result.total == 0
        assert result.page == filter_params.page
        assert result.limit == filter_params.limit
        assert result.total_pages == 0

    def test_transform_data(self, referrals_json_data):
        """Проверка преобразования данных из БГ в формат активов стационара."""
        filter_params = HospitalAssetsFilter(
            date_from=TEST_DATE_FROM,
            date_to=TEST_DATE_TO
        )

        result = HospitalAssetsService._transform_data(
            {"referralItems": referrals_json_data},
            filter_params
        )

        assert result.hospital_name == HOSPITAL_NAME
        assert isinstance(result.items, list)

        if result.items:
            item = result.items[0]
            assert item.id == referrals_json_data[0].get("id", "")
            assert hasattr(item, "status")
            assert hasattr(item, "status_color")
            assert hasattr(item, "patient")
            assert hasattr(item, "additional_info")

    def test_determine_patient_status(self):
        """Проверка определения статуса пациента."""
        # Тест выписанного пациента
        item_discharged = {
            "hasConfirm": "true",
            "outDate": TEST_OUT_DATE
        }
        status, color = HospitalAssetsService._determine_patient_status(item_discharged)
        assert status == HospitalStatus.DISCHARGED
        assert color == HospitalStatusColor.GRAY

        # Тест госпитализированного пациента
        item_hospitalized = {
            "hasConfirm": "true",
            "outDate": None
        }
        status, color = HospitalAssetsService._determine_patient_status(item_hospitalized)
        assert status == HospitalStatus.HOSPITALIZED
        assert color == HospitalStatusColor.BLUE

        # Тест пациента в приемном покое
        item_waiting = {
            "hasConfirm": "false",
            "outDate": None
        }
        status, color = HospitalAssetsService._determine_patient_status(item_waiting)
        assert status == HospitalStatus.WAITING
        assert color == HospitalStatusColor.GREEN

    def test_build_additional_info(self):
        """Проверка построения дополнительной информации для актива."""
        item = {
            "outDate": TEST_OUT_DATE,
            "sick": {
                "code": TEST_SICK_CODE,
                "name": TEST_SICK_NAME
            },
            "bedProfile": {
                "code": TEST_DEPARTMENT_CODE
            },
            "directDoctor": TEST_DOCTOR_NAME,
            "hospitalDate": TEST_REG_DATE
        }

        additional_info = HospitalAssetsService._build_additional_info(item)

        assert additional_info["treatment_outcome"] == TreatmentOutcome.IMPROVEMENT.value
        assert additional_info["discharge_outcome"] == DischargeOutcome.DISCHARGED.value
        assert "hospitalization_period" in additional_info
        assert additional_info["diagnosis"] == "{TEST_SICK_CODE} {TEST_SICK_NAME}"
        assert additional_info["doctor"] == TEST_DOCTOR_NAME
        assert additional_info["department"] == f"№{TEST_DEPARTMENT_CODE}"

    def test_apply_filter(self, referrals_json_data):
        """Проверка применения фильтра к списку элементов."""
        filter_params = HospitalAssetsFilter(
            date_from=TEST_DATE_FROM,
            date_to=TEST_DATE_TO,
            patient_identifier=TEST_PATIENT_IIN,
            department=TEST_DEPARTMENT_CODE,
            status=HospitalAssetStatus.ALL
        )

        filtered_items = HospitalAssetsService._apply_filter(
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

    def test_is_status_match(self):
        """Проверка соответствия статуса фильтру."""
        # Тест для всех статусов
        item = {"hasConfirm": "true", "outDate": None}
        assert HospitalAssetsService._is_status_match(item, HospitalAssetStatus.ALL)

        # Тест для госпитализированных
        item_hospitalized = {"hasConfirm": "true", "outDate": None}
        assert HospitalAssetsService._is_status_match(item_hospitalized, HospitalAssetStatus.HOSPITALIZED)

        item_not_hospitalized = {"hasConfirm": "false", "outDate": None}
        assert not HospitalAssetsService._is_status_match(item_not_hospitalized, HospitalAssetStatus.HOSPITALIZED)

        # Тест для ожидающих
        item_waiting = {"hasConfirm": "false", "outDate": None}
        assert HospitalAssetsService._is_status_match(item_waiting, HospitalAssetStatus.WAITING)

        item_not_waiting = {"hasConfirm": "true", "outDate": None}
        assert not HospitalAssetsService._is_status_match(item_not_waiting, HospitalAssetStatus.WAITING)

        # Тест для выписанных
        item_discharged = {"hasConfirm": "true", "outDate": TEST_OUT_DATE}
        assert HospitalAssetsService._is_status_match(item_discharged, HospitalAssetStatus.DISCHARGED)

        item_not_discharged = {"hasConfirm": "true", "outDate": None}
        assert not HospitalAssetsService._is_status_match(item_not_discharged, HospitalAssetStatus.DISCHARGED)

    def test_get_empty_response(self):
        """Проверка получения пустого ответа."""
        filter_params = HospitalAssetsFilter(
            date_from=TEST_DATE_FROM,
            date_to=TEST_DATE_TO,
            page=TEST_PAGE_NUMBER,
            limit=TEST_PAGE_SIZE
        )

        result = HospitalAssetsService._get_empty_response(filter_params)

        assert result.hospital_name == HOSPITAL_NAME
        assert result.items == []
        assert result.total == 0
        assert result.page == TEST_PAGE_NUMBER
        assert result.limit == TEST_PAGE_SIZE
        assert result.total_pages == 0
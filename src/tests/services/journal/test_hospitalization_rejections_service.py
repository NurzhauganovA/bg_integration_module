import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime

from services.journal.hospitalization_rejections_service import HospitalizationRejectionsService
from data_subjects.requests.hospitalization_rejections_request import RejectionFilter, RejectionStatus
from data_subjects.responses.hospitalization_rejections_response import RejectionStatusColor
from data_subjects.enums.service_enums import RefusalStatus, ContactInfo, DefaultValues
from integration_sdk_orkendeu_mis.handlers.dto.handler_result_dto import HandlerResultDTO
from tests.constants import *


class TestHospitalizationRejectionsService:
    """Тесты для сервиса отказов от госпитализации."""

    @pytest.mark.asyncio
    async def test_get_data_success(self, mock_journal_base_service, referrals_json_data):
        """Проверка успешного получения и преобразования данных."""
        for item in referrals_json_data:
            item["hasRefusal"] = REFUSAL_MARKER

        mock_journal_base_service.return_value = HandlerResultDTO(
            success=True,
            data={"referralItems": referrals_json_data}
        )

        filter_params = RejectionFilter(
            date_from=TEST_DATE_FROM,
            date_to=TEST_DATE_TO,
            patient_identifier=TEST_PATIENT_IIN,
            department=TEST_DEPARTMENT_CODE,
            status=RejectionStatus.REJECTED
        )

        result = await HospitalizationRejectionsService.get_data(filter_params)

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

        filter_params = RejectionFilter(
            date_from=TEST_DATE_FROM,
            date_to=TEST_DATE_TO
        )

        result = await HospitalizationRejectionsService.get_data(filter_params)

        assert result.hospital_name == HOSPITAL_NAME
        assert result.items == []
        assert result.total == 0
        assert result.page == filter_params.page
        assert result.limit == filter_params.limit
        assert result.total_pages == 0

    def test_transform_data(self, referrals_json_data):
        """Проверка преобразования данных из БГ в формат отказов от госпитализации."""
        for item in referrals_json_data:
            item["hasRefusal"] = REFUSAL_MARKER

        filter_params = RejectionFilter(
            date_from=TEST_DATE_FROM,
            date_to=TEST_DATE_TO
        )

        result = HospitalizationRejectionsService._transform_data(
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
            assert item.status_color == RejectionStatusColor.RED

    def test_has_refusal(self):
        """Проверка наличия отказа в записи."""
        item_with_refusal = {
            "hasRefusal": REFUSAL_MARKER
        }
        assert HospitalizationRejectionsService._has_refusal(item_with_refusal)

        item_without_refusal = {
            "hasRefusal": "false"
        }
        assert not HospitalizationRejectionsService._has_refusal(item_without_refusal)

        item_empty_refusal = {}
        assert not HospitalizationRejectionsService._has_refusal(item_empty_refusal)

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
            "refuseJustification": "Медицинские противопоказания"
        }

        additional_info = HospitalizationRejectionsService._build_additional_info(item)

        assert additional_info["diagnosis"] == f"{TEST_SICK_CODE} {TEST_SICK_NAME}"
        assert additional_info["executor"] == ContactInfo.DEFAULT_EXECUTOR.value
        assert additional_info["rejection_reason"] == "Медицинские противопоказания"
        assert additional_info["department"] == f"№{TEST_DEPARTMENT_CODE}"

    def test_build_additional_info_empty_reason(self):
        """Проверка построения дополнительной информации без причины отказа."""
        item = {
            "sick": {
                "code": TEST_SICK_CODE,
                "name": TEST_SICK_NAME
            },
            "bedProfile": {
                "code": TEST_DEPARTMENT_CODE
            }
        }

        additional_info = HospitalizationRejectionsService._build_additional_info(item)

        assert additional_info["rejection_reason"] == DefaultValues.REFUSAL_REASON.value

    def test_apply_filter(self, referrals_json_data):
        """Проверка применения фильтра к списку элементов."""
        for item in referrals_json_data:
            item["hasRefusal"] = REFUSAL_MARKER

        filter_params = RejectionFilter(
            date_from=TEST_DATE_FROM,
            date_to=TEST_DATE_TO,
            patient_identifier=TEST_PATIENT_IIN,
            department=TEST_DEPARTMENT_CODE,
            status=RejectionStatus.ALL
        )

        filtered_items = HospitalizationRejectionsService._apply_filter(
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

            assert item.get("hasRefusal", "").lower() == REFUSAL_MARKER

    def test_get_empty_response(self):
        """Проверка получения пустого ответа."""
        filter_params = RejectionFilter(
            date_from=TEST_DATE_FROM,
            date_to=TEST_DATE_TO,
            page=TEST_PAGE_NUMBER,
            limit=TEST_PAGE_SIZE
        )

        result = HospitalizationRejectionsService._get_empty_response(filter_params)

        assert result.hospital_name == HOSPITAL_NAME
        assert result.items == []
        assert result.total == 0
        assert result.page == TEST_PAGE_NUMBER
        assert result.limit == TEST_PAGE_SIZE
        assert result.total_pages == 0
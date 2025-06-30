import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime
import re

from services.journal.newborns_service import NewbornsService
from data_subjects.requests.newborns_request import NewbornFilter, NewbornStatus
from data_subjects.responses.newborns_response import NewbornStatusColor
from data_subjects.enums.service_enums import ContactInfo, PhonePattern, DefaultValues
from integration_sdk_orkendeu_mis.handlers.dto.handler_result_dto import HandlerResultDTO
from tests.constants import *


class TestNewbornsService:
    """Тесты для сервиса новорожденных."""

    @pytest.mark.asyncio
    async def test_get_data_success(self, mock_journal_base_service, referrals_json_data):
        """Проверка успешного получения и преобразования данных."""
        for item in referrals_json_data:
            patient_data = item.get("patient", {})
            patient_data["birthDate"] = TEST_BIRTH_DATE
            item["addiditonalInformation"] = MOTHER_INFO_MARKER

        mock_journal_base_service.return_value = HandlerResultDTO(
            success=True,
            data={"referralItems": referrals_json_data}
        )

        filter_params = NewbornFilter(
            date_from=TEST_DATE_FROM,
            date_to=TEST_DATE_TO,
            patient_identifier=TEST_PATIENT_IIN,
            department=TEST_DEPARTMENT_CODE,
            status=NewbornStatus.ACTIVE
        )

        result = await NewbornsService.get_data(filter_params)

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

        filter_params = NewbornFilter(
            date_from=TEST_DATE_FROM,
            date_to=TEST_DATE_TO
        )

        result = await NewbornsService.get_data(filter_params)

        assert result.hospital_name == HOSPITAL_NAME
        assert result.items == []
        assert result.total == 0
        assert result.page == filter_params.page
        assert result.limit == filter_params.limit
        assert result.total_pages == 0

    def test_transform_data(self, referrals_json_data):
        """Проверка преобразования данных из БГ в формат данных новорожденных."""
        for item in referrals_json_data:
            patient_data = item.get("patient", {})
            patient_data["birthDate"] = TEST_BIRTH_DATE
            item["addiditonalInformation"] = MOTHER_INFO_MARKER

        filter_params = NewbornFilter(
            date_from=TEST_DATE_FROM,
            date_to=TEST_DATE_TO
        )

        result = NewbornsService._transform_data(
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
            assert item.status_color == NewbornStatusColor.GREEN

            assert "mother" in item.additional_info
            assert item.additional_info["mother"] is not None
            assert hasattr(item.additional_info["mother"], "full_name")

    def test_extract_mother_info(self):
        """Проверка извлечения информации о матери."""
        additional_info_with_mother = f"мать: {TEST_MOTHER_FULL_NAME} {TEST_PHONE_NUMBER}"
        mother = NewbornsService._extract_mother_info(additional_info_with_mother)

        assert mother.full_name == TEST_MOTHER_FULL_NAME
        assert mother.id is None
        assert mother.iin is None
        assert mother.birth_date is None

        additional_info_without_mother = "обычная информация"
        mother = NewbornsService._extract_mother_info(additional_info_without_mother)

        assert mother.full_name == DefaultValues.MOTHER_NAME.value

        empty_info = ""
        mother = NewbornsService._extract_mother_info(empty_info)

        assert mother.full_name == DefaultValues.MOTHER_NAME.value

    def test_build_additional_info(self):
        """Проверка построения дополнительной информации для актива."""
        from data_subjects.responses.newborns_response import Mother

        item = {
            "sick": {
                "code": TEST_SICK_CODE,
                "name": TEST_SICK_NAME
            },
            "bedProfile": {
                "code": TEST_DEPARTMENT_CODE
            }
        }

        mother = Mother(
            id=None,
            iin=None,
            full_name=TEST_MOTHER_FULL_NAME,
            birth_date=None
        )

        phone_number = TEST_PHONE_NUMBER

        additional_info = NewbornsService._build_additional_info(item, mother, phone_number)

        assert additional_info["executor"] == ContactInfo.DEFAULT_EXECUTOR.value
        assert additional_info["diagnosis"] == f"{TEST_SICK_CODE} {TEST_SICK_NAME}"
        assert additional_info["mother"] == mother
        assert additional_info["phone"] == phone_number
        assert additional_info["department"] == f"№{TEST_DEPARTMENT_CODE}"

    def test_is_status_match(self):
        """Проверка соответствия статуса фильтру."""
        item_active = {"outDate": None}
        assert NewbornsService._is_status_match(item_active, NewbornStatus.ALL)
        assert NewbornsService._is_status_match(item_active, NewbornStatus.ACTIVE)
        assert not NewbornsService._is_status_match(item_active, NewbornStatus.DISCHARGED)

        item_discharged = {"outDate": TEST_OUT_DATE}
        assert NewbornsService._is_status_match(item_discharged, NewbornStatus.ALL)
        assert NewbornsService._is_status_match(item_discharged, NewbornStatus.DISCHARGED)
        assert not NewbornsService._is_status_match(item_discharged, NewbornStatus.ACTIVE)

    def test_is_newborn_by_age(self):
        """Проверка определения новорожденного по возрасту."""
        with patch('services.journal.newborns_service.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime(2025, 1, 30)
            mock_datetime.strptime.side_effect = lambda *args, **kwargs: datetime.strptime(*args, **kwargs)

            recent_birth = "2025-01-01T00:00:00"
            assert NewbornsService._is_newborn_by_age(recent_birth)

            old_birth = "2025-12-31T00:00:00"
            assert not NewbornsService._is_newborn_by_age(old_birth)

            invalid_birth = "invalid-date"
            assert not NewbornsService._is_newborn_by_age(invalid_birth)

            empty_birth = ""
            assert not NewbornsService._is_newborn_by_age(empty_birth)

    def test_apply_filter(self, referrals_json_data):
        """Проверка применения фильтра к списку элементов."""
        for item in referrals_json_data:
            patient_data = item.get("patient", {})
            patient_data["birthDate"] = TEST_BIRTH_DATE
            item["addiditonalInformation"] = MOTHER_INFO_MARKER

        filter_params = NewbornFilter(
            date_from=TEST_DATE_FROM,
            date_to=TEST_DATE_TO,
            patient_identifier=TEST_PATIENT_IIN,
            department=TEST_DEPARTMENT_CODE,
            status=NewbornStatus.ACTIVE
        )

        filtered_items = NewbornsService._apply_filter(
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
                additional_info = item.get("addiditonalInformation", "").lower()

                assert (filter_params.patient_identifier.lower() in patient_name or
                        filter_params.patient_identifier == patient_iin or
                        filter_params.patient_identifier.lower() in additional_info)

            if filter_params.department != "all":
                department = item.get("bedProfile", {}).get("code", "")
                assert department == filter_params.department

            if filter_params.status == NewbornStatus.ACTIVE:
                assert "outDate" not in item or not item["outDate"]

    def test_get_empty_response(self):
        """Проверка получения пустого ответа."""
        filter_params = NewbornFilter(
            date_from=TEST_DATE_FROM,
            date_to=TEST_DATE_TO,
            page=TEST_PAGE_NUMBER,
            limit=TEST_PAGE_SIZE
        )

        result = NewbornsService._get_empty_response(filter_params)

        assert result.hospital_name == HOSPITAL_NAME
        assert result.items == []
        assert result.total == 0
        assert result.page == TEST_PAGE_NUMBER
        assert result.limit == TEST_PAGE_SIZE
        assert result.total_pages == 0
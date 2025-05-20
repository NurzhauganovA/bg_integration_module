from datetime import datetime
from typing import Dict, Any

from services.journal_base_service import JournalBaseService
from data_subjects.responses.hospital_assets_response import (
    HospitalAssetsResponse, HospitalAsset, HospitalPatient,
    HospitalStatus, HospitalStatusColor, HospitalAdditionalInfo
)
from data_subjects.requests.hospital_assets_request import HospitalAssetsFilter


class HospitalAssetsService(JournalBaseService[HospitalAssetsResponse, HospitalAssetsFilter]):
    """Сервис для обработки данных активов стационара."""

    @classmethod
    def _transform_data(cls, data: Dict[str, Any], filter_params: HospitalAssetsFilter) -> HospitalAssetsResponse:
        """
        Преобразование данных БГ в формат активов стационара.

        :param data: Данные БГ
        :param filter_params: Параметры фильтрации
        :return: Ответ с активами стационара
        """
        hospital_name = "Коммунальное государственное предприятие на праве хозяйственного ведения “Областная многопрофильная больница города Жезказган” управления здравоохранения области Улытау"
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

            # Определяем статус и цвет
            status = HospitalStatus.WAITING
            status_color = HospitalStatusColor.GREEN

            has_confirm = item.get("hasConfirm", "").lower() == "true"
            out_date = item.get("outDate")

            if out_date:
                status = HospitalStatus.DISCHARGED
                status_color = HospitalStatusColor.GRAY
            elif has_confirm:
                status = HospitalStatus.HOSPITALIZED
                status_color = HospitalStatusColor.BLUE

            additional_info = {
                "treatment_outcome": "Улучшение",
                "discharge_outcome": "Выписан" if out_date else None,
                "hospitalization_period": cls._format_period(item.get("hospitalDate"), out_date),
                "diagnosis": f"{item.get('sick', {}).get('code', '')} {item.get('sick', {}).get('name', '')}",
                "doctor": item.get("directDoctor", ""),
                "executor": "Иванов Алексей Викторович",
                "department": f"№{item.get('bedProfile', {}).get('code', '')}"
            }

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
            hospital_name=hospital_name,
            items=paginated_items,
            total=len(items),
            page=filter_params.page,
            limit=filter_params.limit,
            total_pages=total_pages
        )

    @classmethod
    def _apply_filter(cls, items: list, filter_params: HospitalAssetsFilter) -> list:
        """
        Применение фильтров к списку элементов.

        :param items: Список элементов
        :param filter_params: Параметры фильтрации
        :return: Отфильтрованный список элементов
        """
        filtered_items = []

        date_from = datetime.strptime(filter_params.date_from, "%Y-%m-%d")
        date_to = datetime.strptime(filter_params.date_to, "%Y-%m-%d")

        for item in items:
            reg_date_str = item.get("regDate", "")
            if not reg_date_str:
                continue

            try:
                reg_date = datetime.strptime(reg_date_str.split("T")[0], "%Y-%m-%d")
            except ValueError:
                continue

            if reg_date < date_from or reg_date > date_to:
                continue

            patient_data = item.get("patient", {})
            patient_iin = patient_data.get("personin", "")
            patient_name = patient_data.get("personFullName", "").lower()

            if filter_params.patient_identifier and filter_params.patient_identifier.lower() not in patient_name and filter_params.patient_identifier != patient_iin:
                continue

            department = item.get("bedProfile", {}).get("code", "")
            if filter_params.department and filter_params.department != "all" and department != filter_params.department:
                continue

            if filter_params.status and filter_params.status != HospitalAssetsFilter.ALL:
                has_confirm = item.get("hasConfirm", "").lower() == "true"
                out_date = item.get("outDate")

                if filter_params.status == HospitalAssetsFilter.HOSPITALIZED and not has_confirm:
                    continue
                elif filter_params.status == HospitalAssetsFilter.WAITING and has_confirm:
                    continue
                elif filter_params.status == HospitalAssetsFilter.DISCHARGED and not out_date:
                    continue

            filtered_items.append(item)

        return filtered_items

    @classmethod
    def _apply_sort(cls, items: list, sort_by: str) -> list:
        """
        Применение сортировки к списку элементов.

        :param items: Список элементов
        :param sort_by: Поле для сортировки
        :return: Отсортированный список элементов
        """
        if sort_by == "date_asc":
            return sorted(items, key=lambda x: x.receipt_date)
        elif sort_by == "date_desc":
            return sorted(items, key=lambda x: x.receipt_date, reverse=True)
        elif sort_by == "patient_name_asc":
            return sorted(items, key=lambda x: x.patient.full_name)
        elif sort_by == "patient_name_desc":
            return sorted(items, key=lambda x: x.patient.full_name, reverse=True)

        return items

    @classmethod
    def _apply_pagination(cls, items: list, page: int, limit: int) -> tuple:
        """
        Применение пагинации к списку элементов.

        :param items: Список элементов
        :param page: Номер страницы
        :param limit: Количество элементов на странице
        :return: Кортеж из списка элементов на странице и общего количества страниц
        """
        total_pages = (len(items) + limit - 1) // limit

        start_idx = (page - 1) * limit
        end_idx = start_idx + limit

        return items[start_idx:end_idx], total_pages

    @staticmethod
    def _format_period(start_date: str, end_date: str) -> str:
        """
        Форматирование периода госпитализации.

        :param start_date: Дата начала периода
        :param end_date: Дата окончания периода
        :return: Отформатированный период
        """
        if not start_date:
            return ""

        try:
            formatted_start = datetime.strptime(start_date.split("T")[0], "%Y-%m-%d").strftime("%d.%m.%Y")

            if end_date:
                formatted_end = datetime.strptime(end_date.split("T")[0], "%Y-%m-%d").strftime("%d.%m.%Y")
                return f"С {formatted_start} – По {formatted_end}"
            else:
                return f"С {formatted_start}"
        except ValueError:
            return ""

    @classmethod
    def _get_empty_response(cls, filter_params: HospitalAssetsFilter) -> HospitalAssetsResponse:
        """
        Получение пустого ответа с активами стационара.

        :param filter_params: Параметры фильтрации
        :return: Пустой ответ с активами стационара
        """
        return HospitalAssetsResponse(
            hospital_name="Коммунальное государственное предприятие на праве хозяйственного ведения “Областная многопрофильная больница города Жезказган” управления здравоохранения области Улытау",
            items=[],
            total=0,
            page=filter_params.page,
            limit=filter_params.limit,
            total_pages=0
        )

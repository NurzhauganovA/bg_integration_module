from datetime import datetime
from typing import Dict, Any, List
import re

from services.journal_base_service import JournalBaseService
from data_subjects.responses.newborns_response import (
    NewbornResponse, NewbornAsset, NewbornPatient,
    NewbornStatusColor, NewbornAdditionalInfo, Mother
)
from data_subjects.requests.newborns_request import NewbornFilter


class NewbornsService(JournalBaseService[NewbornResponse, NewbornFilter]):
    """Сервис для обработки данных новорожденных."""

    @classmethod
    def _transform_data(cls, data: Dict[str, Any], filter_params: NewbornFilter) -> NewbornResponse:
        """
        Преобразование данных БГ в формат данных новорожденных.

        :param data: Данные БГ
        :param filter_params: Параметры фильтрации
        :return: Ответ с данными новорожденных
        """
        hospital_name = "Коммунальное государственное предприятие на праве хозяйственного ведения \"Областная многопрофильная больница города Жезказган\" управления здравоохранения области Улытау"
        items = []

        # Получаем элементы направлений из ответа
        referral_items = data.get("referralItems", [])

        # Применяем фильтрацию
        filtered_items = cls._apply_filter(referral_items, filter_params)

        for item in filtered_items:
            # Создаем объект пациента
            patient_data = item.get("patient", {})

            # Извлекаем дополнительную информацию
            additional_info = item.get("addiditonalInformation", "")

            # Информация о матери (пытаемся найти в дополнительной информации)
            mother_name = "Не указано"
            if "мать" in additional_info.lower():
                # Попытка извлечь имя матери после слова "мать"
                mother_match = re.search(r'мать:?\s*([\w\s]+)', additional_info, re.IGNORECASE)
                if mother_match:
                    mother_name = mother_match.group(1).strip()

            # Создаем объект матери
            mother = Mother(
                id=None,
                iin=None,
                full_name=mother_name,
                birth_date=None
            )

            # Извлекаем телефон
            phone_number = None
            phone_match = re.search(r'\+?[78][\d\s-]{10,}', additional_info)
            if phone_match:
                phone_number = phone_match.group(0)

            # Создаем объект пациента
            patient = NewbornPatient(
                id=patient_data.get("id", ""),
                iin=patient_data.get("personin", ""),
                full_name=patient_data.get("personFullName", ""),
                birth_date=patient_data.get("birthDate", "")
            )

            # Формируем дополнительную информацию
            additional_info_dict = {
                "executor": "Иванов Алексей Викторович",  # Пример данных
                "diagnosis": f"{item.get('sick', {}).get('code', '')} {item.get('sick', {}).get('name', '')}",
                "mother": mother,
                "phone": phone_number or "+7 707 888 56 78",  # Пример данных, если не найдено
                "department": f"№{item.get('bedProfile', {}).get('code', '5')}"
            }

            # Создаем актив
            asset = NewbornAsset(
                id=item.get("id", ""),
                number=item.get("protocolNumber", ""),
                receipt_date=item.get("regDate", ""),
                patient=patient,
                status_color=NewbornStatusColor.GREEN,
                additional_info=additional_info_dict
            )

            items.append(asset)

        # Применяем сортировку
        sorted_items = cls._apply_sort(items, filter_params.sort_by)

        # Применяем пагинацию
        paginated_items, total_pages = cls._apply_pagination(
            sorted_items, filter_params.page, filter_params.limit
        )

        return NewbornResponse(
            hospital_name=hospital_name,
            items=paginated_items,
            total=len(items),
            page=filter_params.page,
            limit=filter_params.limit,
            total_pages=total_pages
        )

    @classmethod
    def _apply_filter(cls, items: list, filter_params: NewbornFilter) -> list:
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
            # Получаем дату регистрации
            reg_date_str = item.get("regDate", "")
            if not reg_date_str:
                continue

            try:
                reg_date = datetime.strptime(reg_date_str.split("T")[0], "%Y-%m-%d")
            except ValueError:
                continue

            # Проверяем, входит ли дата в диапазон
            if reg_date < date_from or reg_date > date_to:
                continue

            # Фильтрация по пациенту (новорожденному)
            patient_data = item.get("patient", {})
            patient_iin = patient_data.get("personin", "")
            patient_name = patient_data.get("personFullName", "").lower()

            # Также проверяем дополнительную информацию на наличие имени матери
            additional_info = item.get("addiditonalInformation", "").lower()

            if filter_params.patient_identifier and filter_params.patient_identifier.lower() not in patient_name and filter_params.patient_identifier != patient_iin and filter_params.patient_identifier.lower() not in additional_info:
                continue

            # Фильтрация по департаменту
            department = item.get("bedProfile", {}).get("code", "")
            if filter_params.department and filter_params.department != "all" and department != filter_params.department:
                continue

            # Фильтрация по статусу (активный/выписан)
            if filter_params.status and filter_params.status != NewbornFilter.ALL:
                out_date = item.get("outDate")

                if filter_params.status == NewbornFilter.DISCHARGED and not out_date:
                    continue
                elif filter_params.status == NewbornFilter.ACTIVE and out_date:
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

    @classmethod
    def _get_empty_response(cls, filter_params: NewbornFilter) -> NewbornResponse:
        """
        Получение пустого ответа с данными новорожденных.

        :param filter_params: Параметры фильтрации
        :return: Пустой ответ с данными новорожденных
        """
        return NewbornResponse(
            hospital_name="Коммунальное государственное предприятие на праве хозяйственного ведения \"Областная многопрофильная больница города Жезказган\" управления здравоохранения области Улытау",
            items=[],
            total=0,
            page=filter_params.page,
            limit=filter_params.limit,
            total_pages=0
        )
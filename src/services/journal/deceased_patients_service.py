from datetime import datetime
from typing import Dict, Any, List
import re

from services.journal_base_service import JournalBaseService
from data_subjects.responses.deceased_patients_response import (
    DeceasedResponse, DeceasedAsset, DeceasedPatientModel,
    DeceasedStatusColor, DeceasedAdditionalInfo
)
from data_subjects.requests.deceased_patients_request import DeceasedFilter


class DeceasedPatientsService(JournalBaseService[DeceasedResponse, DeceasedFilter]):
    """Сервис для обработки данных умерших пациентов."""

    @classmethod
    def _transform_data(cls, data: Dict[str, Any], filter_params: DeceasedFilter) -> DeceasedResponse:
        """
        Преобразование данных БГ в формат данных умерших пациентов.

        :param data: Данные БГ
        :param filter_params: Параметры фильтрации
        :return: Ответ с данными умерших пациентов
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

            # Извлекаем телефон и адрес из дополнительной информации
            additional_info = item.get("addiditonalInformation", "")
            address = item.get("address", "г. Алматы ул. Шевченко 195/5 дом 5")  # Пример данных, если не найдено

            # Попытка извлечь номер телефона с использованием регулярного выражения
            phone_number = None
            phone_match = re.search(r'\+?[78][\d\s-]{10,}', additional_info)
            if phone_match:
                phone_number = phone_match.group(0)

            # Определяем пол пациента
            sex_code = patient_data.get("sexIdCode", "")
            sex = "Мужской" if sex_code == "100" else "Женский" if sex_code == "200" else "Не указано"

            # Создаем объект пациента
            patient = DeceasedPatientModel(
                id=patient_data.get("id", ""),
                iin=patient_data.get("personin", ""),
                full_name=patient_data.get("personFullName", ""),
                birth_date=patient_data.get("birthDate", ""),
            )

            # Формируем дополнительную информацию
            additional_info_dict = {
                "phone": phone_number or "+7 707 888 56 78",  # Пример данных, если не найдено
                "address": address,
                "treatment_outcome": "Смерть",
                "discharge_outcome": "Умер",
                "hospitalization_period": cls._format_period(item.get("hospitalDate"), item.get("outDate")),
                "diagnosis": f"{item.get('sick', {}).get('code', '')} {item.get('sick', {}).get('name', '')}",
                "specialist": item.get("directDoctor", "Александр Васильевич Пупкин"),
                "department": f"№{item.get('bedProfile', {}).get('code', '5')}"
            }

            # Создаем актив
            asset = DeceasedAsset(
                id=item.get("id", ""),
                number=item.get("protocolNumber", ""),
                receipt_date=item.get("regDate", ""),
                patient=patient,
                status_color=DeceasedStatusColor.RED,
                additional_info=additional_info_dict
            )

            items.append(asset)

        # Применяем сортировку
        sorted_items = cls._apply_sort(items, filter_params.sort_by)

        # Применяем пагинацию
        paginated_items, total_pages = cls._apply_pagination(
            sorted_items, filter_params.page, filter_params.limit
        )

        return DeceasedResponse(
            hospital_name=hospital_name,
            items=paginated_items,
            total=len(items),
            page=filter_params.page,
            limit=filter_params.limit,
            total_pages=total_pages
        )

    @classmethod
    def _apply_filter(cls, items: list, filter_params: DeceasedFilter) -> list:
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

            # Фильтрация по пациенту
            patient_data = item.get("patient", {})
            patient_iin = patient_data.get("personin", "")
            patient_name = patient_data.get("personFullName", "").lower()

            if filter_params.patient_identifier and filter_params.patient_identifier.lower() not in patient_name and filter_params.patient_identifier != patient_iin:
                continue

            # Фильтрация по департаменту
            department = item.get("bedProfile", {}).get("code", "")
            if filter_params.department and filter_params.department != "all" and department != filter_params.department:
                continue

            # В реальной системе здесь должна быть проверка, что пациент умер
            # Для демонстрации считаем, что все пациенты с определенными условиями умершие
            # Например, если в дополнительной информации есть слово "смерть" или специальный статус

            additional_info = item.get("addiditonalInformation", "").lower()
            if "смерть" in additional_info or "умер" in additional_info:
                filtered_items.append(item)
                continue

            # Для демонстрации добавляем всех пациентов с датой выписки (как будто они умерли)
            if item.get("outDate"):
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
    def _format_period(cls, start_date: str, end_date: str) -> str:
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

    @staticmethod
    def _calculate_age(birth_date: str) -> int:
        """
        Расчет возраста на основе даты рождения.

        :param birth_date: Дата рождения
        :return: Возраст
        """
        if not birth_date:
            return 0

        try:
            birth_date_obj = datetime.strptime(birth_date.split("T")[0], "%Y-%m-%d")
            current_date = datetime.now()

            age = current_date.year - birth_date_obj.year

            # Коррекция возраста, если день рождения еще не наступил в этом году
            if (current_date.month, current_date.day) < (birth_date_obj.month, birth_date_obj.day):
                age -= 1

            return max(0, age)  # Возвраст не может быть отрицательным
        except (ValueError, TypeError):
            return 0

    @classmethod
    def _get_empty_response(cls, filter_params: DeceasedFilter) -> DeceasedResponse:
        """
        Получение пустого ответа с данными умерших пациентов.

        :param filter_params: Параметры фильтрации
        :return: Пустой ответ с данными умерших пациентов
        """
        return DeceasedResponse(
            hospital_name="Коммунальное государственное предприятие на праве хозяйственного ведения \"Областная многопрофильная больница города Жезказган\" управления здравоохранения области Улытау",
            items=[],
            total=0,
            page=filter_params.page,
            limit=filter_params.limit,
            total_pages=0
        )
from datetime import datetime
from typing import Dict, Any, List
import re

from services.journal_base_service import JournalBaseService
from data_subjects.responses.maternity_assets_response import (
    MaternityResponse, MaternityAsset, MaternityPatient,
    MaternityStatusColor, MaternityAdditionalInfo
)
from data_subjects.requests.maternity_assets_request import MaternityFilter


class MaternityAssetsService(JournalBaseService[MaternityResponse, MaternityFilter]):
    """Сервис для обработки данных активов роддома."""

    @classmethod
    def _transform_data(cls, data: Dict[str, Any], filter_params: MaternityFilter) -> MaternityResponse:
        """
        Преобразование данных БГ в формат активов роддома.

        :param data: Данные БГ
        :param filter_params: Параметры фильтрации
        :return: Ответ с активами роддома
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

            # Создаем объект пациента
            patient = MaternityPatient(
                id=patient_data.get("id", ""),
                iin=patient_data.get("personin", ""),
                full_name=patient_data.get("personFullName", ""),
                birth_date=patient_data.get("birthDate", ""),
            )

            # Определяем статус и цвет
            status_color = MaternityStatusColor.GREEN
            treatment_outcome = "Улучшение"
            discharge_outcome = None

            out_date = item.get("outDate")
            if out_date:
                status_color = MaternityStatusColor.GRAY
                discharge_outcome = "Выписан"

            # Формируем дополнительную информацию
            additional_info_dict = {
                "phone": phone_number or "+7 707 888 56 78",  # Пример данных, если не найдено
                "address": address,
                "treatment_outcome": treatment_outcome,
                "discharge_outcome": discharge_outcome,
                "diagnosis": f"{item.get('sick', {}).get('code', '')} {item.get('sick', {}).get('name', '')}",
                "specialist": item.get("directDoctor", "Александр Васильевич Пупкин"),
                "executor": "Иванов Алексей Викторович",  # Пример данных
                "department": f"№{item.get('bedProfile', {}).get('code', '5')}"
            }

            # Создаем актив
            asset = MaternityAsset(
                id=item.get("id", ""),
                number=item.get("protocolNumber", ""),
                receipt_date=item.get("regDate", ""),
                patient=patient,
                status_color=status_color,
                additional_info=additional_info_dict
            )

            items.append(asset)

        # Применяем сортировку
        sorted_items = cls._apply_sort(items, filter_params.sort_by)

        # Применяем пагинацию
        paginated_items, total_pages = cls._apply_pagination(
            sorted_items, filter_params.page, filter_params.limit
        )

        return MaternityResponse(
            hospital_name=hospital_name,
            items=paginated_items,
            total=len(items),
            page=filter_params.page,
            limit=filter_params.limit,
            total_pages=total_pages
        )

    @classmethod
    def _apply_filter(cls, items: list, filter_params: MaternityFilter) -> list:
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

            # Фильтрация по статусу (активный/выписан)
            if filter_params.status and filter_params.status != MaternityFilter.ALL:
                out_date = item.get("outDate")

                if filter_params.status == MaternityFilter.DISCHARGED and not out_date:
                    continue
                elif filter_params.status == MaternityFilter.ACTIVE and out_date:
                    continue

            # В реальной системе здесь должна быть фильтрация по признакам роддома
            # Для демонстрации считаем, что все пациенты женского пола находятся в роддоме

            sex_code = patient_data.get("sexIdCode", "")
            if sex_code == "200":  # Женский пол
                filtered_items.append(item)

            # Также можно проверить диагноз на наличие кодов, связанных с беременностью (например, коды Z32-Z39)
            # Или проверить наличие ключевых слов в диагнозе или дополнительной информации

            diagnosis_code = item.get("sick", {}).get("code", "")
            if diagnosis_code and diagnosis_code.startswith("Z3"):
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
    def _get_empty_response(cls, filter_params: MaternityFilter) -> MaternityResponse:
        """
        Получение пустого ответа с активами роддома.

        :param filter_params: Параметры фильтрации
        :return: Пустой ответ с активами роддома
        """
        return MaternityResponse(
            hospital_name="Коммунальное государственное предприятие на праве хозяйственного ведения \"Областная многопрофильная больница города Жезказган\" управления здравоохранения области Улытау",
            items=[],
            total=0,
            page=filter_params.page,
            limit=filter_params.limit,
            total_pages=0
        )
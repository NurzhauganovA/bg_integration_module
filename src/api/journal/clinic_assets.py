from fastapi import APIRouter, Query
from typing import Optional

from services.journal.clinic_assets_service import ClinicAssetsService
from data_subjects.responses.clinic_assets_response import ClinicResponse
from data_subjects.requests.clinic_assets_request import ClinicFilter, ClinicStatus

router = APIRouter()


@router.get("/clinic-assets", response_model=ClinicResponse, tags=["clinic_assets"])
async def get_clinic_assets(
        patient_identifier: Optional[str] = Query(None, description="ИИН или ФИО пациента"),
        date_from: str = Query(..., description="Дата начала периода (ГГГГ-ММ-ДД)"),
        date_to: str = Query(..., description="Дата окончания периода (ГГГГ-ММ-ДД)"),
        department: Optional[str] = Query("all", description="Участок/отделение"),
        status: Optional[ClinicStatus] = Query(ClinicStatus.ALL, description="Статус актива"),
        delivery_status: Optional[str] = Query(None, description="Статус доставки"),
        sort_by: Optional[str] = Query("date_desc", description="Поле для сортировки"),
        page: Optional[int] = Query(1, description="Номер страницы"),
        limit: Optional[int] = Query(10, description="Количество записей на странице"),
):
    """
    Получение активов поликлиники для пациента в указанном диапазоне дат.

    Этот эндпоинт получает записи о приемах в поликлинике из Бюро госпитализации
    и форматирует их в соответствии с требованиями к активам поликлиники.
    """
    filter_params = ClinicFilter(
        patient_identifier=patient_identifier,
        date_from=date_from,
        date_to=date_to,
        department=department,
        status=status,
        delivery_status=delivery_status,
        sort_by=sort_by,
        page=page,
        limit=limit
    )

    return await ClinicAssetsService.get_data(filter_params)
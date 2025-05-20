from fastapi import APIRouter, Depends, Query
from typing import Optional

from services.journal.hospital_assets_service import HospitalAssetsService
from data_subjects.responses.hospital_assets_response import HospitalAssetsResponse
from data_subjects.requests.hospital_assets_request import HospitalAssetsFilter, HospitalAssetStatus

router = APIRouter()


@router.get("/hospital-assets", response_model=HospitalAssetsResponse, tags=["hospital_assets"])
async def get_hospital_assets(
        patient_identifier: Optional[str] = Query(None, description="ИИН или ФИО пациента"),
        date_from: str = Query(..., description="Дата начала периода (ГГГГ-ММ-ДД)"),
        date_to: str = Query(..., description="Дата окончания периода (ГГГГ-ММ-ДД)"),
        department: Optional[str] = Query("all", description="Участок/отделение"),
        status: Optional[HospitalAssetStatus] = Query(HospitalAssetStatus.ALL, description="Статус актива"),
        delivery_status: Optional[str] = Query(None, description="Статус доставки"),
        sort_by: Optional[str] = Query("date_desc", description="Поле для сортировки"),
        page: Optional[int] = Query(1, description="Номер страницы"),
        limit: Optional[int] = Query(10, description="Количество записей на странице"),
):
    """
    Получение активов стационара для пациента в указанном диапазоне дат.

    Этот эндпоинт получает записи о пациентах в стационаре из Бюро госпитализации
    и форматирует их в соответствии с требованиями к активам стационара.
    """
    filter_params = HospitalAssetsFilter(
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

    return await HospitalAssetsService.get_data(filter_params)
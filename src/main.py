from fastapi import FastAPI, APIRouter

from data_subjects.requests.bg_referrals_request import BGReferralsPayload
from data_subjects.responses.bg_referrals_response import BGReferralsResponse
from handlers.bg_search_referrals_handler import BGReferralsHandler

app = FastAPI(
    title="BG Integration",
    description="BG integration for handling various integration requests",
    version="1.0.0",
    openapi_tags=[
        {
            "name": "bg_integration",
            "description": "BG Integration endpoints"
        }
    ]
)


router = APIRouter()


@router.post("/bg_referrals", tags=["bg_integration"])
async def bg_referrals_endpoint(payload: BGReferralsPayload, response_model=BGReferralsResponse):
    """
    Endpoint для обработки запросов на поиск направлений пациента в БГ.
    """

    handler = BGReferralsHandler()
    result = await handler.handle(payload.dict())
    if result:
        return {"status": 200, "result": result}
    return {"status": 403, "message": result.error_message}


app.include_router(router)

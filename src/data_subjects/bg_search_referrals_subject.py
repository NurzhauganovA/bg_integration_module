from integration_sdk_orkendeu_mis.data_subjects.abstract import AbstractDataSubject

from data_subjects.requests.bg_referrals_request import BGReferralsPayload
from data_subjects.responses.bg_referrals_response import BGReferralsResponse


class BGReferralsSubject(AbstractDataSubject):
    code = "BG_REFERRALS"
    label = "БГ - Поиск направлений пациента"
    payload_schema = BGReferralsPayload
    response_schema = BGReferralsResponse
    allow_cache = True
    cache_key_fields = ["patientIINorFIO", "dateFrom", "dateTo"]

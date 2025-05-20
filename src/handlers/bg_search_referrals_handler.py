from integration_sdk_orkendeu_mis.handlers.abstract import AbstractServiceHandler
from integration_sdk_orkendeu_mis.handlers.mixins.trace_logging import TraceLoggingMixin

from fetchers.bg_search_referrals_fetcher import BGReferralsFetcher
from parsers.bg_search_referrals_parser import BGReferralsParser
from providers.bg_provider import BGProvider
from data_subjects.bg_search_referrals_subject import BGReferralsSubject


class BGReferralsHandler(AbstractServiceHandler, TraceLoggingMixin):
    """
    Обработчик для поиска направлений пациента в БГ.
    """

    fetcher_class = BGReferralsFetcher
    parser_class = BGReferralsParser
    provider_class = BGProvider
    data_subject_class = BGReferralsSubject

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fetcher = self.fetcher_class()
        self.parser = self.parser_class()
        self.provider = self.provider_class()
        self.data_subject = self.data_subject_class()
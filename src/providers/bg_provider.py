from integration_sdk_orkendeu_mis.providers.abstract import AbstractProvider
from integration_sdk_orkendeu_mis.providers.presets.common_params import USERNAME_PARAM, PASSWORD_PARAM


class BGProvider(AbstractProvider):
    code = "BG"
    label = "Бюро госпитализаций"
    params = [USERNAME_PARAM, PASSWORD_PARAM]

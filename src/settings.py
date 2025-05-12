from os import getenv


USE_MOCK = getenv("USE_MOCK", "false").lower() == "true"
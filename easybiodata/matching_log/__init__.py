from easybiodata.core import Service
from easybiodata.matching_log.models import MatchingLog


class MatchingLogService(Service):
    __model__ = MatchingLog

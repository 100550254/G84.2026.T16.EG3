from datetime  import datetime, timezone
from .enterprise_manager import ValidadorFecha

class NumDocsDocument:
    def __init__(self, query_date: str):
        ValidadorFecha.validate_format(query_date)

        self.__query_date = query_date
        self.__report_date = datetime.now(timezone.utc).timestamp()


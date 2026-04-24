from datetime  import datetime, timezone
from .enterprise_management_exception import EnterpriseManagementException
from.project_document import ProjectDocument
from .enterprise_manager import ValidadorFecha
from .attribute import Attribute
from .date import Date

class NumDocsDocument:
    def __init__(self, query_date: str):
        ValidadorFecha.validate_format(query_date)

        self.__query_date = Date(query_date).value
        self.__report_date = datetime.now(timezone.utc).timestamp()
        self.__num_files = 0

    @property
    def value(self):
        return self.__query_date

    @value.setter
    def value(self, query_date):
        self.__query_date=query_date

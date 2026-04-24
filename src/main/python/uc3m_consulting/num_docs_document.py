from datetime  import datetime, timezone
from src.main.python.uc3m_consulting.exception.enterprise_management_exception import EnterpriseManagementException
from.project_document import ProjectDocument
from .enterprise_manager import ValidadorFecha
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

    @property
    def num_files(self):
        return self.__num_files

    def find_docs_in_document(self, d_list):
        self.__num_files = 0
        for el in d_list:
            time_val = el["register_date"]
            doc_date_str = datetime.fromtimestamp(time_val).strftime(
                "%d/%m/%Y")
            if doc_date_str == self.__query_date:
                ProjectDocument.get_docs_from_file(el)
                self.__num_files += 1

        if self.__num_files==0:
            raise EnterpriseManagementException
        return self.__num_files

    def to_json(self):
        return{"Querydate": self.__query_date, "ReportDate":
            self.__report_date,"Numfiles": self.__num_files}
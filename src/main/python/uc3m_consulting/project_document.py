"""Contains the class OrderShipping"""
from datetime import datetime, timezone
import hashlib

class ProjectDocument():
    """Class representing the information required for shipping of an order"""

    def __init__(self, project_id: str, file_name):
        self.__alg = "SHA-256"
        self.__type = "PDF"
        self.__project_id = project_id
        self.__file_name = file_name
        justnow = datetime.now(timezone.utc)
        self.__register_date = datetime.timestamp(justnow)

    def to_json(self):

        return {"alg": self.__alg,
                "type": self.__type,
                "project_id": self.__project_id,
                "file_name": self.__file_name,
                "register_date": self.__register_date,
                "document_signature": self.document_signature}

    def __signature_string(self):
        """Composes the string to be used for generating the key for the date"""
        return "{alg:" + str(self.__alg) +",typ:" + str(self.__type) +",project_id:" + \
               str(self.__project_id) + ",file_name:" + str(self.__file_name) + \
               ",register_date:" + str(self.__register_date) + "}"

    @property
    def project_id(self):
        return self.__project_id

    @project_id.setter
    def project_id(self, value):
        self.__project_id = value

    @property
    def file_name(self):
        return self.__file_name
    @file_name.setter
    def file_name(self, value):
        self.__file_name = value

    @property
    def register_date(self):
        return self.__register_date
    @register_date.setter
    def register_date(self, value):
        self.__register_date = value


    @property
    def document_signature(self):
        """Returns the sha256 signature of the date"""
        return hashlib.sha256(self.__signature_string().encode()).hexdigest()

    @classmethod
    def get_docs_from_file(cls, el):
        from datetime import datetime, timezone
        from freezegun import freeze_time
        from uc3m_consulting.exception.enterprise_management_exception import EnterpriseManagementException

        fecha_obj = datetime.fromtimestamp(el["register_date"],
                                           tz=timezone.utc)

        with freeze_time(fecha_obj):
            p = cls(el["project_id"], el["file_name"])

            if p.document_signature != el["document_signature"]:
                raise EnterpriseManagementException(
                    "Inconsistent document signature")

            return p
import re
from datetime import datetime, timezone
from uc3m_consulting.enterprise_management_exception import EnterpriseManagementException
from.attribute import Attribute

class Date(Attribute):
    """clase para validar la fecha"""

    @staticmethod
    def validate_format(fecha_texto):
        """valida solo el formato de la fecha"""
        regex_fecha = re.compile(r"^(([0-2]\d|3[0-1])(0\d|1[0-2])\d\d\d\d)$")
        resultado_match = regex_fecha.fullmatch(fecha_texto)
        if not resultado_match:
            raise EnterpriseManagementException("Invalid date format")

        try:
            return datetime.strptime(fecha_texto, "%d/%m/%Y").date()
        except ValueError as ex:
            raise EnterpriseManagementException("Invalid date format") from ex
    def validate_starting_date( fecha_texto):
        """validates the  date format  using regex"""
        regex_fecha = re.compile(r"^(([0-2]\d|3[0-1])(0\d|1[0-2])\d\d\d\d)$")
        resultado_match = regex_fecha.fullmatch(fecha_texto)
        if not resultado_match:
            raise EnterpriseManagementException("Invalid date format")

        try:
            fecha_objeto = datetime.strptime(fecha_texto, "%d/%m/%Y").date()
        except ValueError as ex:
            raise EnterpriseManagementException("Invalid date format") from ex

        if fecha_objeto < datetime.now(timezone.utc).date():
            raise EnterpriseManagementException("Project's date must be today or later.")

        if fecha_objeto.year < 2025 or fecha_objeto.year > 2050:
            raise EnterpriseManagementException("Invalid date format")
        return fecha_texto
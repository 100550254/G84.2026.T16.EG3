import json
from uc3m_consulting.enterprise_management_exception import EnterpriseManagementException
from uc3m_consulting.enterprise_manager_config import (TEST_DOCUMENTS_STORE_FILE,
                                                       TEST_NUMDOCS_STORE_FILE)

class DocumentStore:
    """Clase encargada de la persistencia de documentos e informes (Lectura/Escritura)"""

    def __init__(self):
        pass

    def cargar_documentos(self):
        """ Lee y devuelve el contenido del fichero de documentos """
        try:
            with open(TEST_DOCUMENTS_STORE_FILE, "r", encoding="utf-8", newline="") as file:
                return json.load(file)
        except FileNotFoundError as ex:
            raise EnterpriseManagementException("Wrong file  or file path") from ex

    def guardar_informe(self, resultado_json):
        """ Guarda el informe JSON de documentos contados """
        try:
            with open(TEST_NUMDOCS_STORE_FILE, "r", encoding="utf-8", newline="") as file:
                historial_informes = json.load(file)
        except FileNotFoundError:
            historial_informes = []
        except json.JSONDecodeError as ex:
            raise EnterpriseManagementException("JSON Decode Error - Wrong JSON Format") from ex

        historial_informes.append(resultado_json)

        try:
            with open(TEST_NUMDOCS_STORE_FILE, "w", encoding="utf-8", newline="") as file:
                json.dump(historial_informes, file, indent=2)
        except FileNotFoundError as ex:
            raise EnterpriseManagementException("Wrong file  or file path") from ex
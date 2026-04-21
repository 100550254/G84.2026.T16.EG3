import json
from uc3m_consulting.enterprise_management_exception import EnterpriseManagementException
from uc3m_consulting.enterprise_manager_config import PROJECTS_STORE_FILE


class ProjectStore:
    """ Clase encargada de gestionar la persistencia de los proyectos (Lectura/Escritura) """

    def __init__(self):
        pass

    def guardar_proyecto(self, new_project):
        """ Guarda un nuevo proyecto verificando que no esté duplicado """
        lista_proyectos = self.cargar_proyectos()

        for proyecto_item in lista_proyectos:
            if proyecto_item == new_project.to_json():
                raise EnterpriseManagementException("Duplicated project in projects list")

        lista_proyectos.append(new_project.to_json())
        self.escribir_proyectos(lista_proyectos)

    def cargar_proyectos(self):
        """ Lee el fichero de proyectos y devuelve la lista """
        try:
            with open(PROJECTS_STORE_FILE, "r", encoding="utf-8", newline="") as fichero:
                return json.load(fichero)
        except FileNotFoundError:
            return []
        except json.JSONDecodeError as ex:
            raise EnterpriseManagementException("JSON Decode Error - Wrong JSON Format") from ex

    def escribir_proyectos(self, lista_proyectos):
        """ Sobrescribe el fichero de proyectos """
        try:
            with open(PROJECTS_STORE_FILE, "w", encoding="utf-8", newline="") as fichero:
                json.dump(lista_proyectos, fichero, indent=2)
        except FileNotFoundError as ex:
            raise EnterpriseManagementException("Wrong file or file path") from ex
        except json.JSONDecodeError as ex:
            raise EnterpriseManagementException("JSON Decode Error - Wrong JSON Format") from ex

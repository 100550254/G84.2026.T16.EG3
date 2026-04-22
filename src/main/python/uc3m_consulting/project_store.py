import json
from .enterprise_management_exception import EnterpriseManagementException
from .enterprise_manager_config import PROJECTS_STORE_FILE


class ProjectStore:
    """ Clase encargada de gestionar la persistencia de los proyectos (Singleton) """

    _instance = None
    #Patron singleton aplicado (usamos new para no hacer el singleton mas
    # complejo)
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ProjectStore, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if hasattr(self, "_initialized"):
            return
        self._initialized = True

    def guardar_proyecto(self, new_project):
        """ y verifica que no esté duplicado """
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

"""Module """
import re
import json

from datetime import datetime, timezone
from freezegun import freeze_time
from uc3m_consulting.enterprise_project import EnterpriseProject
from uc3m_consulting.enterprise_management_exception import EnterpriseManagementException
from uc3m_consulting.enterprise_manager_config import (PROJECTS_STORE_FILE,
                                                       TEST_DOCUMENTS_STORE_FILE,
                                                       TEST_NUMDOCS_STORE_FILE)
from uc3m_consulting.project_document import ProjectDocument

class EnterpriseManager:
    """Class for providing the methods for managing the orders"""
    def __init__(self):
        pass

    @staticmethod
    def validate_cif(codigo_cif: str):
        """validates a cif number """
        if not isinstance(codigo_cif, str):
            raise EnterpriseManagementException("CIF code must be a string")
        patron_cif = re.compile(r"^[ABCDEFGHJKNPQRSUVW]\d{7}[0-9A-J]$")
        if not patron_cif.fullmatch(codigo_cif):
            raise EnterpriseManagementException("Invalid CIF format")

        return EnterpriseManager._comprobar_digito_control(codigo_cif)

    @staticmethod
    def _comprobar_digito_control(codigo_cif: str):
        letra_inicial = codigo_cif[0]
        digitos_cif = codigo_cif[1:8]
        digito_control_leido = codigo_cif[8]

        suma_impares = 0
        suma_pares = 0

        for i in range(len(digitos_cif)):
            if i % 2 == 0:
                doble = int(digitos_cif[i]) * 2
                if doble > 9:
                    suma_impares = suma_impares + (doble // 10) + (doble % 10)
                else:
                    suma_impares = suma_impares + doble
            else:
                suma_pares = suma_pares + int(digitos_cif[i])

        suma_total = suma_impares + suma_pares
        unidad_suma = suma_total % 10
        valor_control_calculado = 10 - unidad_suma

        if valor_control_calculado == 10:
            valor_control_calculado = 0

        letras_mapeo = "JABCDEFGHI"

        if letra_inicial in ('A', 'B', 'E', 'H'):
            if str(valor_control_calculado) != digito_control_leido:
                raise EnterpriseManagementException("Invalid CIF character control number")
        elif letra_inicial in ('P', 'Q', 'S', 'K'):
            if letras_mapeo[valor_control_calculado] != digito_control_leido:
                raise EnterpriseManagementException("Invalid CIF character control letter")
        else:
            raise EnterpriseManagementException("CIF type not supported")
        return True

    def validate_starting_date(self, fecha_texto):
        """validates the  date format  using regex"""
        regex_fecha = re.compile(r"^(([0-2]\d|3[0-1])\/(0\d|1[0-2])\/\d\d\d\d)$")
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

    #pylint: disable=too-many-arguments, too-many-positional-arguments
    def register_project(self,
                         company_cif: str,
                         project_acronym: str,
                         project_description: str,
                         department: str,
                         date: str,
                         presupuesto: str):
        """registers a new project"""
        self.validate_cif(company_cif)
        self._validar_datos_proyecto(project_acronym, project_description, department)
        self.validate_starting_date(date)
        self._validar_presupuesto(presupuesto)

        new_project = EnterpriseProject(company_cif=company_cif,
                                        project_acronym=project_acronym,
                                        project_description=project_description,
                                        department=department,
                                        starting_date=date,
                                        project_budget=presupuesto)

        return self._guardar_proyecto(new_project)

    def _validar_datos_proyecto(self, project_acronym: str, project_description: str, department: str):
        regex_acronimo = re.compile(r"^[a-zA-Z0-9]{5,10}")
        resultado_acronimo = regex_acronimo.fullmatch(project_acronym)
        if not resultado_acronimo:
            raise EnterpriseManagementException("Invalid acronym")

        regex_descripcion = re.compile(r"^.{10,30}$")
        resultado_descripcion = regex_descripcion.fullmatch(project_description)
        if not resultado_descripcion:
            raise EnterpriseManagementException("Invalid description format")

        regex_departamento = re.compile(r"(HR|FINANCE|LEGAL|LOGISTICS)")
        resultado_departamento = regex_departamento.fullmatch(department)
        if not resultado_departamento:
            raise EnterpriseManagementException("Invalid department")

    def _validar_presupuesto(self, presupuesto: str):
        try:
            presupuesto_float  = float(presupuesto)
        except ValueError as exc:
            raise EnterpriseManagementException("Invalid budget amount") from exc

        presupuesto_str = str(presupuesto_float)
        if '.' in presupuesto_str:
            decimales = len(presupuesto_str.split('.')[1])
            if decimales > 2:
                raise EnterpriseManagementException("Invalid budget amount")

        if presupuesto_float < 50000 or presupuesto_float > 1000000:
            raise EnterpriseManagementException("Invalid budget amount")

    def _guardar_proyecto(self, new_project: EnterpriseProject):
        try:
            with open(PROJECTS_STORE_FILE, "r", encoding="utf-8", newline="") as fichero:
                lista_proyectos = json.load(fichero)
        except FileNotFoundError:
            lista_proyectos = []
        except json.JSONDecodeError as ex:
            raise EnterpriseManagementException("JSON Decode Error - Wrong JSON Format") from ex

        for proyecto_item in lista_proyectos:
            if proyecto_item == new_project.to_json():
                raise EnterpriseManagementException("Duplicated project in projects list")

        lista_proyectos.append(new_project.to_json())

        try:
            with open(PROJECTS_STORE_FILE, "w", encoding="utf-8", newline="") as fichero:
                json.dump(lista_proyectos, fichero, indent=2)
        except FileNotFoundError as ex:
            raise EnterpriseManagementException("Wrong fichero  or fichero path") from ex
        except json.JSONDecodeError as ex:
            raise EnterpriseManagementException("JSON Decode Error - Wrong JSON Format") from ex
        return new_project.project_id

    def find_docs(self, fecha_consulta):
        """
        Generates a JSON report counting valid documents for a specific date.

        Checks cryptographic hashes and timestamps to ensure historical data integrity.
        Saves the output to 'resultado.json'.

        Args:
            fecha_consulta (str): date to query.

        Returns:
            number of documents found if report is successfully generated and saved.

        Raises:
            EnterpriseManagementException: On invalid date, file IO errors,
                missing data, or cryptographic integrity failure.
        """
        regex_fecha = re.compile(r"^(([0-2]\d|3[0-1])\/(0\d|1[0-2])\/\d\d\d\d)$")
        resultado_fecha = regex_fecha.fullmatch(fecha_consulta)
        if not resultado_fecha:
            raise EnterpriseManagementException("Invalid date format")

        try:
            datetime.strptime(fecha_consulta, "%d/%m/%Y").date()
        except ValueError as ex:
            raise EnterpriseManagementException("Invalid date format") from ex

        # open documents
        try:
            with open(TEST_DOCUMENTS_STORE_FILE, "r", encoding="utf-8", newline="") as file:
                lista_documentos = json.load(file)
        except FileNotFoundError as ex:
            raise EnterpriseManagementException("Wrong file  or file path") from ex

        conteo_validos = self._contar_documentos_validos(lista_documentos, fecha_consulta)

        # prepare json text
        ahora_timestamp = datetime.now(timezone.utc).timestamp()
        resultado_json = {
             "Querydate":  fecha_consulta,
             "ReportDate": ahora_timestamp,
             "Numfiles": conteo_validos
        }

        self._guardar_informe(resultado_json)
        return conteo_validos

    def _contar_documentos_validos(self, lista_documentos, fecha_consulta):
        conteo_validos = 0
        # loop to find
        for doc_item in lista_documentos:
            fecha_doc_ts = doc_item["register_date"]

            # string conversion for easy match
            doc_date_str = datetime.fromtimestamp(fecha_doc_ts).strftime("%d/%m/%Y")

            if doc_date_str == fecha_consulta:
                fecha_obj = datetime.fromtimestamp(fecha_doc_ts, tz=timezone.utc)
                with freeze_time(fecha_obj):
                    # check the project id (thanks to freezetime)
                    # if project_id are different then the data has been
                    #manipulated
                    p_doc = ProjectDocument(doc_item["project_id"], doc_item["file_name"])
                    if p_doc.document_signature == doc_item["document_signature"]:
                        conteo_validos = conteo_validos + 1
                    else:
                        raise EnterpriseManagementException("Inconsistent document signature")

        if conteo_validos == 0:
            raise EnterpriseManagementException("No documents found")

        return conteo_validos

    def _guardar_informe(self, resultado_json):
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

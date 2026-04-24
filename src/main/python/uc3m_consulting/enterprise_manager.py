"""Module """
import re

from datetime import datetime, timezone
from freezegun import freeze_time
from uc3m_consulting.enterprise_project import EnterpriseProject
from uc3m_consulting.enterprise_management_exception import EnterpriseManagementException
from uc3m_consulting.enterprise_manager_config import (PROJECTS_STORE_FILE,
                                                       TEST_DOCUMENTS_STORE_FILE,
                                                       TEST_NUMDOCS_STORE_FILE)
from uc3m_consulting.num_docs_document import NumDocsDocument
from uc3m_consulting.project_document import ProjectDocument
from uc3m_consulting.project_store import ProjectStore
from uc3m_consulting.document_store import DocumentStore

class ValidadorCif:
    """clase para la validación del cif"""
    @staticmethod
    def validate_cif(codigo_cif: str):
            if not isinstance(codigo_cif, str):
                raise EnterpriseManagementException("CIF code must be a string")
            patron_cif = re.compile(r"^[ABCDEFGHJKNPQRSUVW]\d{7}[0-9A-J]$")
            if not patron_cif.fullmatch(codigo_cif):
                raise EnterpriseManagementException("Invalid CIF format")

            return ValidadorCif._comprobar_digito_control(codigo_cif)

    @staticmethod
    def _comprobar_digito_control(codigo_cif: str):
            letra_inicial = codigo_cif[0]
            digitos_cif = codigo_cif[1:8]
            digito_control_leido = codigo_cif[8]

            suma_total = ValidadorCif._calcular_suma_cif(digitos_cif)

            unidad_suma = suma_total % 10
            valor_control_calculado = (10 - unidad_suma) % 10

            # Validación final del mapeo
            return ValidadorCif._validar_mapeo_control(letra_inicial,
                                            valor_control_calculado, digito_control_leido)

    @staticmethod
    def _calcular_suma_cif(digitos_cif: str):
            """ Calcula la suma acumulada de los dígitos del CIF """
            suma_impares = 0
            suma_pares = 0
            for i, digito in enumerate(digitos_cif):
                if i % 2 == 0:
                    doble = int(digito) * 2
                    suma_impares += (doble // 10) + (doble % 10) if doble > 9 else doble
                else:
                    suma_pares += int(digito)
            return suma_impares + suma_pares

    @staticmethod
    def _validar_mapeo_control(letra_inicial, valor_control, digito_leido):
            """ Valida que el dígito o letra de control coincida con el tipo de CIF """
            letras_mapeo = "JABCDEFGHI"
            if letra_inicial in ('A', 'B', 'E', 'H'):
                if str(valor_control) != digito_leido:
                    raise EnterpriseManagementException("Invalid CIF character control number")
            elif letra_inicial in ('P', 'Q', 'S', 'K'):
                if letras_mapeo[valor_control] != digito_leido:
                    raise EnterpriseManagementException("Invalid CIF character control letter")
            else:
                raise EnterpriseManagementException("CIF type not supported")
            return True

class ValidadorFecha:
    """clase para validar la fecha"""

    @staticmethod
    def validate_format(fecha_texto):
        """valida solo el formato de la fecha"""
        regex_fecha = re.compile(r"^(([0-2]\d|3[0-1])\/(0\d|1[0-2])\/\d\d\d\d)$")
        resultado_match = regex_fecha.fullmatch(fecha_texto)
        if not resultado_match:
            raise EnterpriseManagementException("Invalid date format")

        try:
            return datetime.strptime(fecha_texto, "%d/%m/%Y").date()
        except ValueError as ex:
            raise EnterpriseManagementException("Invalid date format") from ex
    def validate_starting_date( fecha_texto):
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

class GestionadorProyecto:
    """clase para gestionar y registrar proyectos"""

    def register_project(self,
                         company_cif: str,
                         project_acronym: str,
                         project_description: str,
                         department: str,
                         date: str,
                         presupuesto: str):
        """registers a new project"""
        ValidadorCif.validate_cif(company_cif)
        self._validar_datos_proyecto(project_acronym, project_description, department)
        ValidadorFecha.validate_starting_date(date)
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
        """ Delega la acción de guardar a la clase ProjectStore """
        store = ProjectStore()
        store.guardar_proyecto(new_project)
        return new_project.project_id

class GestionadorDocumentos:
    """clase para gestionar y crear documentos"""

    def find_docs(self, fecha_consulta):
        """ Genera un informe JSON contando los documentos válidos para una fecha específica """
        my_num_docs = NumDocsDocument(fecha_consulta)
        ValidadorFecha.validate_format(fecha_consulta)

        store = DocumentStore()
        lista_documentos = store.cargar_documentos()

        conteo_validos = self._contar_documentos_validos(lista_documentos, fecha_consulta)

        ahora_timestamp = datetime.now(timezone.utc).timestamp()
        resultado_json = {
            "Querydate": fecha_consulta,
            "ReportDate": ahora_timestamp,
            "Numfiles": conteo_validos
        }

        store.guardar_informe(resultado_json)
        return conteo_validos

    def _contar_documentos_validos(self, lista_documentos, fecha_consulta):
        conteo_validos = 0
        for doc_item in lista_documentos:
            fecha_doc_ts = doc_item["register_date"]

            # string conversion for easy match
            doc_date_str = datetime.fromtimestamp(fecha_doc_ts).strftime("%d/%m/%Y")

            if doc_date_str == fecha_consulta:
                ProjectDocument.get_docs_from_file(doc_item)
                conteo_validos += 1

        if conteo_validos == 0:
            raise EnterpriseManagementException("No documents found")

        return conteo_validos






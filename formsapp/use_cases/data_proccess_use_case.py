import logging
import traceback
from typing import Any, Dict, List, Optional, Tuple

from bson import ObjectId
from dateutil import parser

from api.helpers.http_responses import created, error
from api.utils.error_reporter import send_data_process_log_email
from fcea_monitoreo.functions import get_altitude, get_geocode
from fcea_monitoreo.utils import get_collection, insert_document
from formsapp.scripts import formulas
from formsapp.scripts.formsapp_parse import parse_data
from formsapp.scripts.sync.scores_calculation import scores_calculation

logger = logging.getLogger(__name__)


class DataProccessUseCase:
    def __init__(self, raw_data: Dict[str, Any]):
        logger.info(raw_data.keys())
        self.raw_data = raw_data
        self.site_id = raw_data["answer"]["answerId"]
        self._issues: List[str] = []
        self.formsapp_id = None

    def proccess(self):
        """
        Regla:
        - Siempre intentamos guardar RAW.
        - Luego intentamos parsear e insertar site.
        - No detenemos el flujo por errores; acumulamos issues.
        - Al final, si hubo issues, mandamos correo SOLO con el resumen tipo log.
        """

        # 1) RAW: si esto falla, sí regresamos error (no hay nada que recuperar)
        if not self._step("insert_formsapp_raw_data", self._insert_formsapp_raw_data):
            self._flush_issues_email()
            return error(self._issues_text())

        # 2) Parse
        data = self._step_return(
            "parse_data", lambda: parse_data(self.raw_data), default=None)

        # 3) Insert site
        if data is not None:
            self._step("insert_site", lambda: self._insert_site(data))
        else:
            self._warn("insert_site",
                       "No se pudo insertar site porque parse_data falló.")

        # 4) enviar correo si hubo issues
        self._flush_issues_email()

        if self._issues:
            return created(["Procesado concluido con warnings/errores. Se envió un correo con el detalle."])
        return created(["The data has been saved successfully"])

    # -------------------------
    # Steps
    # -------------------------
    def _insert_formsapp_raw_data(self):
        data = dict(self.raw_data)
        data["_id"] = ObjectId()
        inserted_raw_data = insert_document("formsapp_raw_data", data)
        if inserted_raw_data:
            self.formsapp_id = data["_id"]

    def _insert_site(self, data: Dict[str, Any]) -> None:
        mapped: Dict[str, Any] = {}

        # project
        project_id_str = data.get("proyecto")
        project = self._step_return(
            "get_project",
            lambda: get_collection(
                "projects", {"_id": ObjectId(project_id_str)}),
            default=[],
        )
        project_doc = project[0] if project else {}

        mapped["_id"] = ObjectId(self.site_id)
        mapped["project_id"] = ObjectId(
            project_id_str) if project_id_str else None
        mapped["cuenca"] = data.get("cuenca")

        # geocode
        lat = self._step_return(
            "parse_latitud",
            lambda: float(
                data.get("ubicacion_del_sitio_de_monitoreo/latitud")),
            default=None,
        )
        lon = self._step_return(
            "parse_longitud",
            lambda: float(
                data.get("ubicacion_del_sitio_de_monitoreo/longitud")),
            default=None,
        )

        city, state = self._step_return(
            "get_geocode",
            lambda: get_geocode(lat, lon),
            default=("", ""),
        ) if (lat is not None and lon is not None) else ("", "")

        mapped["latitud"] = lat
        mapped["longitud"] = lon
        mapped["ciudad"] = city
        mapped["estado"] = state

        mapped["altitud"] = self._step_return(
            "get_altitude",
            lambda: float(get_altitude(lat, lon)),
            default=None,
        ) if (lat is not None and lon is not None) else None

        # user
        user_id, institution = self._step_return(
            "get_user",
            lambda: self._get_user(data.get("correo_electronico")),
            default=(data.get("correo_electronico"), ""),
        )
        mapped["user_id"] = ObjectId(
            str(user_id)) if self._is_objectid(user_id) else user_id
        mapped["institucion"] = institution

        # campos base
        mapped["brigadistas"] = data.get(
            "nombre_de_las_y_los_integrantes_del_equipo")
        mapped["nombre_sitio"] = (data.get("nombre_del_sitio") or "").strip()
        mapped["codigo_sitio"] = data.get("clave_del_sitio")

        mapped["es_sitio_referencia"] = formulas.get_es_sitio_de_referencia(
            data.get("es_sitio_de_referencia")
        )

        mapped["fecha"] = self._step_return(
            "parse_fecha_del_monitoreo",
            lambda: parser.isoparse(data.get("fecha_del_monitoreo")),
            default=None,
        )

        mapped["temporada"] = data.get("temporada")
        mapped["anio"] = project_doc.get("year")
        mapped["mes"] = project_doc.get("month")

        mapped["fotografia1"] = data.get("fotografia_1")[
            0] if data.get("fotografia_1") else None
        mapped["fotografia2"] = data.get("fotografia_2")[
            0] if data.get("fotografia_2") else None
        mapped["notas"] = data.get("notas_y_observaciones", "")

        # --- SITIO REFERENCIA (CRÍTICO) ---
        # Guardamos nombre por si falla, y resolvemos ID si existe.
        sitio_ref_nombre = (data.get("sitio_de_referencia") or "").strip()
        mapped["sitio_referencia_nombre"] = sitio_ref_nombre

        sitio_ref_id = self._step_return(
            "get_sitio_de_referencias",
            lambda: self._get_sitio_de_referencias(data, project_doc),
            default=None,
        )
        mapped["sitio_referencia_id"] = sitio_ref_id

        # Si tu regla de negocio dice “no puede ser nulo”, aquí lo registramos como ERROR
        if mapped["sitio_referencia_id"] is None:
            self._err(
                "sitio_referencia_id_required",
                f"sitio_referencia_id es None. sitio_de_referencia='{sitio_ref_nombre}'. "
                "No se ejecutará scores_calculation para evitar fallas."
            )

        # ---- resto cálculos ----
        mapped["ph"] = formulas.float_pfq(data, "ph")
        mapped["amonio"] = formulas.float_pfq(data, "nitrogeno_amoniacal")
        mapped["ortofosfatos"] = formulas.float_pfq(data, "ortofosfatos")
        mapped["temperatura_agua"] = formulas.float_pfq(
            data, "temperatura_del_agua")
        mapped["temperatura_ambiental"] = formulas.float_pfq(
            data, "temperatura_ambiental")
        mapped["oxigeno_disuelto"] = formulas.float_pfq(
            data, "oxigeno_disuelto")

        mapped["saturacion"] = formulas.get_saturation(
            mapped["oxigeno_disuelto"],
            mapped["altitud"],
            mapped["temperatura_agua"],
        )

        mapped["turbidez"] = formulas.float_pfq(data, "turbidez")
        mapped["nitratos"] = formulas.float_pfq(data, "nitrogeno_de_nitratos")

        mapped["coliformes_fecales"] = (
            data.get(
                "bacterias_coliformes_totales/coliformes_totales") == "Presencia"
        )
        mapped["coliformes_totales"] = data.get(
            "bacterias_coliformes_totales/coliformes_totales")

        mapped["macroinvertebrados"] = formulas.get_macroinvertabrates(data)
        mapped["calificacion_macroinvertebrados"] = formulas.get_macroinvertebrates_average_score(
            mapped["macroinvertebrados"]
        )

        mapped["calidad_hidromorfologica"] = formulas.get_ch(data)
        mapped["calidad_bosque_ribera"] = formulas.get_qbr(data)
        mapped["secciones"] = formulas.get_sections(data)

        mapped["ancho_cauce"] = formulas.custom_float(
            data, "caudal/ancho_total_del_cauce")
        mapped["distancia_recorrida_objeto"] = formulas.custom_float(
            data, "distancia_total_que_recorre_el_flotador"
        )
        mapped["tiempo_recorrido_objeto"] = formulas.get_tiempo(data)
        mapped["profundidad_orilla"] = formulas.custom_float(
            data, "caudal/profundidad_en_la_orilla")
        mapped["caudal"] = formulas.get_caudal(mapped)

        mapped["macroinvertebrados_no_identificados"] = formulas.boolean(
            data,
            "informacion_adicional/requieres_apoyo_para_identificar_y_clasificar_un_macroinvertebrado",
        )

        mapped["archivos_adjuntos"] = data.get(
            "informacion_adicional/sube_tus_imagenes_aqui", [])

        mapped["create_date"] = self._step_return(
            "parse_createDate",
            lambda: parser.isoparse(self.raw_data["answer"]["createDate"]),
            default=None,
        )
        mapped["formsapp_id"] = str(self.formsapp_id)

        # Insert site
        self._step(
            "insert_document_sites",
            lambda: insert_document(
                "sites",
                mapped,
                {"nombre_sitio": mapped["nombre_sitio"],
                    "project_id": mapped["project_id"]},
            ),
        )

        # Scores SOLO si hay sitio_referencia_id válido (evita el InvalidId que tenías)
        if mapped["sitio_referencia_id"] is not None:
            self._step("scores_calculation",
                       lambda: scores_calculation(self.site_id))
        else:
            self._warn("scores_calculation",
                       "Saltado porque sitio_referencia_id es None.")

    # -------------------------
    # Queries
    # -------------------------
    def _get_user(self, email: str) -> Tuple[Any, str]:
        user = get_collection(
            "users",
            {"email": email, "activated": True, "_deleted": False},
        )
        if not user:
            return email, ""
        return user[0]["_id"], user[0].get("institution", "")

    def _get_sitio_de_referencias(self, data: Dict[str, Any], project: Dict[str, Any]) -> Optional[ObjectId]:
        """
        Regresa ObjectId o None.
        NO regresa string (eso fue lo que originó: ObjectId('Paso Feo')).
        """
        if not isinstance(project, dict) or not {"year", "month"}.issubset(project):
            return None

        nombre = (data.get("sitio_de_referencia") or "").strip()
        if not nombre:
            return None

        sitio = get_collection(
            "sites",
            {
                "nombre_sitio": nombre,
                "anio": project.get("year"),
                "mes": project.get("month"),
                "temporada": data.get("temporada"),
                "es_sitio_referencia": True,
            },
        )
        if not sitio:
            return None

        _id = sitio[0].get("_id")
        return ObjectId(str(_id)) if self._is_objectid(_id) else None

    # -------------------------
    # Step wrappers (LOG + issues)
    # -------------------------
    def _step(self, step: str, fn) -> bool:
        try:
            fn()
            return True
        except Exception as e:
            # IMPORTANTE: exception() imprime traceback SIEMPRE
            logger.exception("Failure at %s (answerId=%s): %s",
                             step, self.site_id, e)
            self._issues.append(self._format_issue(
                "ERROR", step, e, traceback.format_exc()))
            return False

    def _step_return(self, step: str, fn, default=None):
        try:
            return fn()
        except Exception as e:
            logger.exception("Failure at %s (answerId=%s): %s",
                             step, self.site_id, e)
            self._issues.append(self._format_issue(
                "ERROR", step, e, traceback.format_exc()))
            return default

    def _warn(self, step: str, message: str) -> None:
        logger.warning("Warning at %s (answerId=%s): %s",
                       step, self.site_id, message)
        self._issues.append(f"WARNING | {step} | {message}")

    def _err(self, step: str, message: str) -> None:
        logger.error("Error at %s (answerId=%s): %s",
                     step, self.site_id, message)
        self._issues.append(f"ERROR | {step} | {message}")

    def _format_issue(self, level: str, step: str, exc: Exception, tb: str) -> str:
        # deja el traceback al final, pero recortado (últimas 30 líneas)
        tb_lines = (tb or "").splitlines()
        tail = tb_lines[-30:] if len(tb_lines) > 30 else tb_lines
        tail_txt = "\n".join(tail)
        return f"{level} | {step} | {exc}\n{tail_txt}".strip()

    def _issues_text(self) -> str:
        return "\n\n".join([x for x in self._issues if x]).strip()

    def _flush_issues_email(self) -> None:
        if not self._issues:
            return
        send_data_process_log_email(
            answer_id=self.site_id, log_text=self._issues_text())

    def _is_objectid(self, value: Any) -> bool:
        try:
            ObjectId(str(value))
            return True
        except Exception:
            return False

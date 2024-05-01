from fcea_monitoreo.utils import get_collection
from datetime import datetime
import math

PFQ = "parametros_fisicoquimicos"
FLOW = f"{PFQ}/flow"


def _int(data, key):
    """Get int or None if not possible"""
    try:
        return int(data.get(key, ""))
    except ValueError:
        return None


def _float(data, key):
    """Get float or None if not possible"""
    try:
        return float(data.get(key, ""))
    except ValueError:
        return None


def boolean(data, key):
    """Get boolean or None if not possible"""
    if key in data.keys():
        return data.get(key) == "Sí"
    return None


def custom_float(data, key):
    """Get float or None if not possible"""
    try:
        return float(data.get(key, ""))
    except ValueError:
        return None


def get_es_sitio_de_referencia(value):
    """Get if it is a reference site"""
    if value.lower() == "si":
        return True
    else:
        return False


def get_username(value):
    """GEt username"""
    if value == "username not found":
        return None
    return value


def float_pfq(data, key):
    """Get float from parametros fisicos y químicos"""
    return _float(data, key)


def format_date(datetime_str):
    return datetime.strptime(datetime_str, '%Y-%m-%d')


def get_tipo_cuerpo_de_agua(data, key):
    # """Get tipo de cuerpo de agua"""
    # tipo = data.get("datos_generales/Tipo_de_cuerpo", "")
    # mapper = {
    #     "Rio_o_arroyo": "Manantiales, ríos y arroyos",
    #     "Manantial": "Manantiales, ríos y arroyos",
    #     "Lago_o_laguna": "Lagos y lagunas",
    #     "preson": "Presón",
    # }
    # if tipo in mapper.keys():
    #     return mapper[tipo]
    # return tipo
    list_tipo_cuerpo_agua = get_collection(
        'catalogs', {'name': 'Tipo de cuerpos de agua'})
    return list_tipo_cuerpo_agua[0]['values'][data.get(key)]


def get_saturation(dissolved_oxygen, elevation, temperature):
    pressure_atm = 1 * math.exp(-0.000118 * elevation)

    cp_numerator = (
        (math.exp(7.7117 - 1.31403 * math.log(temperature + 45.93)))
        * pressure_atm
        * (
            1
            - math.exp(
                11.8571
                - (3840.7 / (temperature + 273.15))
                - (216961 / ((temperature + 273.15) ** 2))
            )
        )
        / pressure_atm
        * (
            1
            - (
                0.000975
                - (0.00001426 * temperature)
                + (0.00000006436 * (temperature**2))
            )
        )
        / (
            1
            - math.exp(
                11.8571
                - (3840.7 / (temperature + 273.15))
                - 216961 / ((temperature + 273.15) ** 2)
            )
        )
    )
    cp_denominator = 1 - (
        0.000975 - (0.00001426 * temperature) +
        (0.00000006436 * (temperature**2))
    )
    cp = cp_numerator / cp_denominator

    saturation = (100 * dissolved_oxygen) / cp
    return round(saturation, 3)


def get_total_coliforms_text(value):
    return "Presentes" if value else "Ausentes"


def get_catalog_of_macroinvertebrate_scores():
    list_of_macroinvertebrate_scores = get_collection(
        'catalogs', {'name': 'Puntuación de macroinvertebrados'})
    return list_of_macroinvertebrate_scores[0]['values']


def get_macroinvertabrates(data):
    """Get macroinvertabrates"""
    macroinvertabrates = []
    M_PREFIX = "macroinvertebrados_bentonicos"
    groups = []
    for key in data.keys():
        if M_PREFIX in key:
            groups.append(key)
    for group in groups:
        families = data.get(group)
        if not families or not isinstance(families, str):
            continue
        families = families.strip().split(" ")
        for family in families:
            try:
                score = get_macroinvertebrate_score(family)
            except Exception:
                score = None
            macroinvertabrates.append(
                {
                    "familia": family.capitalize(),
                    "puntaje": score,
                }
            )
    return macroinvertabrates


def get_macroinvertebrate_score(family):
    """Get the macroinvertebrate score"""
    macroinvertebrate_scores = get_catalog_of_macroinvertebrate_scores()
    if family.lower() in macroinvertebrate_scores.keys():
        return macroinvertebrate_scores[family.lower()]
    return None


def get_macroinvertebrates_average_score(macroinvertebrate_list):
    """Get valid macroinvertebrates"""
    macroinvertebrate_list_filter_one = list(
        filter(lambda x: x["puntaje"] is not None, macroinvertebrate_list)
    )
    macroinvertebrate_list = list(
        filter(lambda x: x["puntaje"] != "ND",
               macroinvertebrate_list_filter_one)
    )
    if not macroinvertebrate_list:
        return 4.1
    return round(
        sum([x["puntaje"] for x in macroinvertebrate_list]) /
        len(macroinvertebrate_list),
        2,
    )


# def get_ch(data):
#     """Obtener calidad hidromorfologica"""
#     keys = [
#         "parametros_paisajisticos/Calidad_hidromorfologica/alteraciones_humanas/calculation_total",
#         "parametros_paisajisticos/Calidad_hidromorfologica/calculation_total",
#     ]
#     for key in keys:
#         value = _int(data, key)
#         if value:
#             return value
#     return "N/A"


# def get_qbr(data):
#     """Obtener calidad de bosque de ribera"""
#     key_suffix = "calculation_qbr"
#     for key in data.keys():
#         if key_suffix in key:
#             value = _int(data, key)
#             if value:
#                 return value
#     return "N/A"


def get_riverside_vegetation(data):
    """Obtener la vegetacion de ribera"""
    for key in data.keys():
        if "Opcional_Puedes_ano_en_la_zona_de_ribera" in key:
            return data[key]
    return "N/A"


def get_sections(data):
    """Get sections"""
    sections = []
    raw_sections = data.get("ancho_y_profundidad_de_cada_seccion", [])
    for raw_section in raw_sections:
        sections.append(
            {
                "width": _float(raw_section, "ancho_y_profundidad_de_cada_seccion/ancho_de_la_seccion"),
                "depth": _float(raw_section, "ancho_y_profundidad_de_cada_seccion/profundidad_de_la_seccion"),
            }
        )
    return sections


def get_tiempo(data):
    """Obtener el tiempo de recorrido"""
    T_PREFIX = "velocidad_de_corriente"
    groups = []
    for key in data.keys():
        if T_PREFIX in key:
            groups.append(data[key])
    if len(groups) > 0:
        avg = sum(groups)/len(groups)
        return round(avg, 2)
    return None


def get_caudal(data):
    """Caudal calculation"""
    try:
        areas = []
        initial_depth = float(data["profundidad_orilla"])
        sections = data["secciones"]
        for index, section in enumerate(sections):
            width = float(section["width"])
            depth = float(section["depth"])

            if index == 0:
                previous_depth = initial_depth
            else:
                previous_depth = float(sections[index - 1]["depth"])
            section_area = ((previous_depth + depth) * width) / 2
            areas.append(section_area)

        speed = data["distancia_recorrida_objeto"] / \
            data["tiempo_recorrido_objeto"]
        total_area = sum(areas)
        flow = speed * total_area
        return round(flow, 3)
    except Exception:
        return None


def get_not_identified_macros(data):
    """Get images of not identified macroinvertebrates"""
    needs_help = False
    M_SUFFIX = "informacion_adicional/requieres_apoyo_para_identificar_y_clasificar_un_macroinvertebrado"
    M_PREFIX = "macroinvertebrate"
    for key in data.keys():
        if M_SUFFIX in key and data[key] == "Sí":
            needs_help = True
            break
    if not needs_help:
        return []
    raw_elements = []
    for key in data.keys():
        if M_PREFIX in key and isinstance(data[key], list):
            raw_elements = data[key]
            break
    macros = []
    for element_dict in raw_elements:
        macro = {"observations": [], "pictures": []}
        for key, value in element_dict.items():
            if "observaciones" in key.lower():
                macro["observations"].append(value)
            else:
                macro["pictures"].append(value)
        macro["observations"] = ",".join(macro["observations"])
        macros.append(macro)
    return macros


def get_ch(data):
    calculation_total = 0
    for key in data.keys():
        if key.startswith('calidad_de_la_cuenca/'):
            calculation_total += _int(data, key)
    for key in data.keys():
        if key.startswith('caracteristicas_hidrologicas/'):
            calculation_total += _int(data, key)
    for key in data.keys():
        if key.startswith('alteraciones_humanas/'):
            calculation_total += _int(data, key)
    return calculation_total if calculation_total > 0 else "N/A"


def get_qbr(data):
    calculation_qbr = 0
    keys = [
        "grado_de_cobertura_de_la_vegetacion/puntuacion_del_bloque_1",
        "estructura_de_la_vegetacion_en_la_zona_ribera/puntuacion_del_bloque_2",
        "calidad_de_la_vegetacion_de_la_zona_ribera/puntuacion_del_bloque_3",
        "naturalidad_del_cauce_del_rio/puntuacion_del_bloque_4"
    ]
    for key in keys:
        value = _int(data, key)
        if value:
            calculation_qbr += value
    return calculation_qbr if calculation_qbr > 0 else "N/A"

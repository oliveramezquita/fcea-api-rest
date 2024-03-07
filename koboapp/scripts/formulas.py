from datetime import datetime
import math

PFQ = "parametros_fisicoquimicos"
FLOW = f"{PFQ}/flow"


macroinvertebrate_scores = {
    "acari": 4,
    "aeshnidae": 8,
    "amphipoda": 7,
    "astacidae": 5,
    "athericidae": 9,
    "baetidae": 5,
    "belostomatidae": 4,
    "blephariceridae": 9,
    "caenidae": 4,
    "calamoceratidae": 8,
    "calopterygidae": 4,
    "ceratopogonidae": 4,
    "chironomidae": 2,
    "coenagrionidae": 4,
    "corixidae": 4,
    "corydalidae": 6,
    "crambidae": 5,
    "culicidae": 2,
    "dixidae": 4,
    "dolichopodidae": 4,
    "dytiscidae": 4,
    "elmidae": 5,
    "empididae": 4,
    "glossosomatidae": 8,
    "gomphidae": 7,
    "gyrinidae": 4,
    "helicopsychidae": 5,
    "heptageniidae": 9,
    "hirudinea": 3,
    "hydrobiosidae": 9,
    "hydrophilidae": 3,
    "hydropsychidae": 5,
    "hydroptilidae": 6,
    "lepidostomatidae": 9,
    "leptoceridae": 8,
    "leptohyphiidae": 5,
    "leptophlebiidae": 8,
    "lestidae": 7,
    "libellulidae": 6,
    "limnephilidae": 8,
    "naucoridae": 4,
    "nepidae": 4,
    "notonectidae": 4,
    "odontoceridae": 9,
    "oligochaeta": 1,
    "oligoneuriidae": 5,
    "palaemonidae": 5,
    "perlidae": 9,
    "philopotamidae": 7,
    "physidae": 3,
    "planorbidae": 3,
    "platystictidae": 7,
    "polycentropodidae": 6,
    "psephenidae": 7,
    "pseudothelphusidae": 5,
    "psychodidae": 3,
    "ptilodactylidae": 7,
    "scirtidea": 4,
    "simuliidae": 4,
    "staphylinidae": 4,
    "stratiomyidae": 4,
    "syrphidae": 1,
    "tabanidae": 4,
    "tipulidae": 4,
}


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
        return data.get(key) == "1"
    return None


def custom_float(data, key):
    """Get float or None if not possible"""
    try:
        return float(data.get(key, ""))
    except ValueError:
        return None


def get_es_sitio_de_referencia(value):
    """Get if it is a reference site"""
    if value == "si":
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
    return _float(data, f"{PFQ}/{key}")


def format_date(datetime_str):
    return datetime.strptime(datetime_str, '%Y-%m-%d').strftime("%d/%m/%Y")


def get_tipo_cuerpo_de_agua(data):
    """Get tipo de cuerpo de agua"""
    tipo = data.get("datos_generales/Tipo_de_cuerpo", "")
    mapper = {
        "Rio_o_arroyo": "Manantiales, ríos y arroyos",
        "Manantial": "Manantiales, ríos y arroyos",
        "Lago_o_laguna": "Lagos y lagunas",
        "preson": "Presón",
    }
    if tipo in mapper.keys():
        return mapper[tipo]
    return tipo


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


def get_macroinvertabrates(data):
    """Get macroinvertabrates"""
    macroinvertabrates = []
    M_PREFIX = "parametros_biologicos/Macroinvertebrados"
    groups = []
    for key in data.keys():
        if M_PREFIX in key:
            groups.append(key)
    for group in groups:
        families = data.get(group)
        if not families or not isinstance(families, str):
            continue
        if families in ["s_", "no"]:
            continue
        families = families.split(" ")
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

    if family.lower() in macroinvertebrate_scores.keys():
        return macroinvertebrate_scores[family.lower()]
    return None


def get_macroinvertebrates_average_score(macroinvertebrate_list):
    """Get valid macroinvertebrates"""
    macroinvertebrate_list = list(
        filter(lambda x: x["puntaje"] is not None, macroinvertebrate_list)
    )
    if not macroinvertebrate_list:
        return 4.1
    return round(
        sum([x["puntaje"] for x in macroinvertebrate_list])
        / len(macroinvertebrate_list),
        2,
    )


def get_ch(data):
    """Obtener calidad hidromorfologica"""
    keys = [
        "parametros_paisajisticos/Calidad_hidromorfologica/alteraciones_humanas/calculation_total",
        "parametros_paisajisticos/Calidad_hidromorfologica/calculation_total",
    ]
    for key in keys:
        value = _int(data, key)
        if value:
            return value
    return "N/A"


def get_qbr(data):
    """Obtener calidad de bosque de ribera"""
    key_suffix = "calculation_qbr"
    for key in data.keys():
        if key_suffix in key:
            value = _int(data, key)
            if value:
                return value
    return "N/A"


def get_riverside_vegetation(data):
    """Obtener la vegetacion de ribera"""
    for key in data.keys():
        if "Opcional_Puedes_ano_en_la_zona_de_ribera" in key:
            return data[key]
    return "N/A"


def get_sections(data):
    """Get sections"""
    sections = []
    raw_sections = data.get(f"{FLOW}/secciones", [])
    for raw_section in raw_sections:
        sections.append(
            {
                "width": _float(raw_section, f"{FLOW}/secciones/Ancho_seccion"),
                "depth": _float(raw_section, f"{FLOW}/secciones/depth"),
            }
        )
    return sections


def get_tiempo(data):
    """Obtener el tiempo de recorrido"""
    key_suffix = "Tiempo_AB"
    for key in data.keys():
        if key_suffix in key:
            value = _float(data, key)
            if value:
                return value
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
    M_SUFFIX = "_Requieres_apoyo_para_identifi"
    M_PREFIX = "parametros_biologicos/Macroinvertebrados"
    for key in data.keys():
        if M_SUFFIX in key and data[key] == "s_":
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

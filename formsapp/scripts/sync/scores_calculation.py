from fcea_monitoreo.utils import get_collection, update_document
from bson import ObjectId

_colors = get_collection('catalogs', {'name': 'Colores'})
_interpretation = get_collection('catalogs', {'name': 'Evaluación'})


def scores_calculation(site_id):
    site = get_collection('sites', {'_id': ObjectId(site_id)})[0]
    scores = {
        'ph': None,
        'water_temperature': None,
        'saturation': None,
        'turbidity': None,
        'nitrates': None,
        'ammonium': None,
        'orthophosphates': None,
        'macroinvertebrates_rating': calculate_biotic_grade(site['macroinvertebrados']),
        'fecal_coliforms': calculate_coliforms_grade(site['coliformes_fecales']),
        'ch': calculate_ch_grade(site['calidad_hidromorfologica']),
        'cbr': calculate_cbr_grade(site['calidad_bosque_ribera']),
    }
    rfs = get_collection(
        'sites', {'_id': ObjectId(site['sitio_referencia_id'])})
    if rfs:
        scores['ph'] = ph_calculation(site['ph'], rfs[0]['ph'])
        scores['water_temperature'] = water_temperature_calculation(
            site['temperatura_agua'], rfs[0]['temperatura_agua'])
        scores['saturation'] = saturation_calculation(
            site['oxigeno_disuelto'], rfs[0]['oxigeno_disuelto'])
        scores['turbidity'] = turbidity_calculation(
            site['turbidez'], rfs[0]['turbidez'])
        scores['nitrates'] = nitrates_calculation(
            site['nitratos'], rfs[0]['nitratos'])
        scores['ammonium'] = ammonium_calculation(
            site['amonio'], rfs[0]['amonio'])
        scores['orthophosphates'] = orthophosphates_calculation(
            site['ortofosfatos'], rfs[0]['ortofosfatos'])
    scores['total'] = total_score(scores)
    scores['interpretation'] = set_interpretation(scores['total'])
    update_document('sites', {'_id': ObjectId(
        site['_id'])}, {'scores': scores})


def ph_calculation(ph, ph_rfs):
    magnitudes = abs(ph - ph_rfs)
    score = 0
    if magnitudes <= 0.5:
        score = 1
    elif magnitudes <= 1.0:
        score = 2
    elif magnitudes <= 1.5:
        score = 3
    elif magnitudes <= 2.0:
        score = 4
    else:
        score = 5
    return score, set_color(score)


def water_temperature_calculation(temperature, temperature_rfs):
    if temperature < temperature_rfs:
        return 1, set_color(1)
    ratio = temperature_rfs / temperature
    score = 0
    if ratio >= 0.8:
        score = 1
    elif ratio >= 0.6:
        score = 2
    elif ratio >= 0.4:
        score = 3
    elif ratio >= 0.2:
        score = 4
    else:
        score = 5
    return score, set_color(score)


def saturation_calculation(saturation, saturation_rfs):
    change = saturation / saturation_rfs
    score = 0
    if change >= 0.8:
        score = 1
    elif change >= 0.6:
        score = 2
    elif change >= 0.4:
        score = 3
    elif change >= 0.2:
        score = 4
    else:
        score = 5
    return score, set_color(score)


def turbidity_calculation(turbidity, turbidity_rfs):
    change = turbidity - turbidity_rfs
    score = 0
    if change < 5:
        score = 1
    elif change <= 10:
        score = 2
    elif change <= 15:
        score = 3
    elif change <= 20:
        score = 4
    else:
        score = 5
    return score, set_color(score)


def nitrates_calculation(nitrates, nitrates_rfs):
    if nitrates < nitrates_rfs:
        return 1, set_color(1)
    magnitudes = (nitrates - nitrates_rfs) / 0.2
    score = 0
    if magnitudes <= 0:
        score = 1
    elif magnitudes < 1:
        score = 2
    elif magnitudes < 2:
        score = 3
    elif magnitudes < 3:
        score = 4
    else:
        score = 5
    return score, set_color(score)


def ammonium_calculation(ammonium, ammonium_rfs):
    positions_difference = get_positions_difference(ammonium, ammonium_rfs)
    score = 0
    if positions_difference <= 0:
        score = 1
    elif positions_difference <= 1:
        score = 2
    elif positions_difference <= 2:
        score = 3
    elif positions_difference <= 3:
        score = 4
    else:
        score = 5
    return score, set_color(score)


def get_positions_difference(ammonium, ammonium_rfs):
    scales = [0, 0.05, 0.1, 0.25, 0.5, 1.0, 1.5, 2.0]

    reference_position = 0
    position = 0
    for value in scales:
        if ammonium >= value:
            position = position + 1
        if ammonium_rfs >= value:
            reference_position = reference_position + 1

    return position - reference_position


def orthophosphates_calculation(orthophosphates, orthophosphates_rfs):
    if orthophosphates < orthophosphates_rfs:
        return 1, set_color(1)
    magnitudes = (orthophosphates - orthophosphates_rfs) / 0.2
    score = 0
    if magnitudes <= 0:
        score = 1
    elif magnitudes <= 1:
        score = 2
    elif magnitudes <= 2:
        score = 3
    elif magnitudes <= 3:
        score = 4
    else:
        score = 5
    return score, set_color(score)


def macroinvertebrates_average_score(macroinvertebrate_list):
    macroinvertebrate_list = list(
        filter(lambda x: x["puntaje"] is not None and x["puntaje"]
               != "ND", macroinvertebrate_list)
    )
    if not macroinvertebrate_list:
        return 4.1
    return round(
        sum([x["puntaje"] for x in macroinvertebrate_list])
        / len(macroinvertebrate_list),
        2,
    )


def calculate_biotic_grade(macroinvertebrate_list):
    average = macroinvertebrates_average_score(macroinvertebrate_list)
    score = 0
    if average >= 6.1:
        score = 1
    elif average >= 5.1:
        score = 2
    elif average >= 4.1:
        score = 3
    elif average >= 3.1:
        score = 4
    else:
        score = 5
    return score, set_color(score)


def calculate_coliforms_grade(coliforms):
    score = 3
    if not coliforms:
        score = 1
    return score, set_color(score)


def calculate_ch_grade(ch):
    score = 0
    if ch > 100:
        score = 1
    elif ch >= 85:
        score = 2
    elif ch >= 47:
        score = 3
    elif ch >= 13:
        score = 4
    else:
        score = 5
    return score, set_color(score)


def calculate_cbr_grade(cbr):
    score = 0
    if cbr > 95:
        score = 1
    elif cbr >= 75:
        score = 2
    elif cbr >= 55:
        score = 3
    elif cbr >= 30:
        score = 4
    else:
        score = 5
    return score, set_color(score)


def total_score(scores):
    total = 0
    for key in scores.keys():
        if scores[key]:
            total = total + scores[key][0]
        else:
            total = total + 1
    score = 1
    grade = 5
    if total >= 11 and total <= 15:
        grade = 1
        score = 5
    elif total >= 16 and total <= 25:
        grade = 2
        score = 4
    elif total >= 26 and total <= 35:
        score = grade = 3
    elif total >= 36 and total <= 46:
        grade = 4
        score = 2
    return score, grade, set_color(grade), (100-total)


def set_color(score):
    if 'values' in _colors[0]:
        values = _colors[0]['values']
        return values[str(score)]
    return None


def set_interpretation(score):
    if 'values' in _interpretation[0]:
        values = _interpretation[0]['values']
        for i, key in enumerate(values):
            if i + 1 == score[1]:
                return key, values[key]

    return None

import traceback
from formsapp.scripts.formsapp_parse import parse_data
from api.helpers.http_responses import created, error
from formsapp.scripts import formulas
from formsapp.scripts.sync.scores_calculation import scores_calculation
from fcea_monitoreo.utils import get_collection, insert_document
from fcea_monitoreo.functions import get_altitude, get_geocode
from bson import ObjectId
from dateutil import parser


class DataProccessUseCase:
    def __init__(self, raw_data):
        self.raw_data = raw_data
        self.site_id = raw_data['answer']['answerId']

    def proccess(self):
        self._insert_formsapp_raw_data(self.raw_data)
        try:
            data = parse_data(self.raw_data)
            self._insert_site(data)
            return created(['The data has been saved successfully'])
        except Exception:
            return error(traceback.format_exc())

    def _insert_formsapp_raw_data(self, data):
        data['_id'] = ObjectId()
        insert_document('formsapp_raw_data', data)

    def _insert_site(self, data):
        mapped_data = {}
        city, state = get_geocode(
            float(data.get('ubicacion_del_sitio_de_monitoreo/latitud')),
            float(data.get('ubicacion_del_sitio_de_monitoreo/longitud')),
        )
        user_id, institution = self._get_user(data.get('correo_electronico'))
        project = get_collection(
            'projects', {'_id': ObjectId(data.get('proyecto'))})
        mapped_data['_id'] = ObjectId(self.site_id)
        mapped_data['project_id'] = ObjectId(data.get('proyecto'))
        mapped_data['cuenca'] = data.get('cuenca')
        mapped_data['es_sitio_referencia'] = formulas.get_es_sitio_de_referencia(data.get(
            'es_sitio_de_referencia'))
        mapped_data['sitio_referencia_id'] = self._get_sitio_de_referencias(
            data, project[0]['year'], project[0]['month'])
        mapped_data['user_id'] = ObjectId(user_id)
        mapped_data['institucion'] = institution
        mapped_data['brigadistas'] = data.get(
            'nombre_de_las_y_los_integrantes_del_equipo')
        mapped_data['nombre_sitio'] = data.get('nombre_del_sitio').strip()
        mapped_data['codigo_sitio'] = data.get('clave_del_sitio')
        mapped_data['latitud'] = float(
            data.get('ubicacion_del_sitio_de_monitoreo/latitud'))
        mapped_data['longitud'] = float(
            data.get('ubicacion_del_sitio_de_monitoreo/longitud'))
        mapped_data['altitud'] = float(get_altitude(
            mapped_data['latitud'], mapped_data['longitud']))
        mapped_data['estado'] = state
        mapped_data['ciudad'] = city
        mapped_data['tipo_cuerpo_agua'] = formulas.get_tipo_cuerpo_de_agua(
            data, 'selecciona_el_tipo_de_cuerpo_de_agua')
        mapped_data['fecha'] = parser.isoparse(data.get('fecha_del_monitoreo'))
        mapped_data['temporada'] = data.get('temporada')
        mapped_data['anio'] = project[0]['year']
        mapped_data['mes'] = project[0]['month']
        mapped_data['fotografia1'] = data.get(
            'fotografia_1')[0] if data.get('fotografia_1') else None
        mapped_data['fotografia2'] = data.get(
            'fotografia_2')[0] if data.get('fotografia_2') else None
        mapped_data['notas'] = data.get('notas_y_observaciones', '')
        mapped_data['ph'] = formulas.float_pfq(data, 'ph')
        mapped_data['amonio'] = formulas.float_pfq(data, 'nitrogeno_amoniacal')
        mapped_data['ortofosfatos'] = formulas.float_pfq(
            data, 'ortofosfatos')
        mapped_data['temperatura_agua'] = formulas.float_pfq(
            data, 'temperatura_del_agua')
        mapped_data['temperatura_ambiental'] = formulas.float_pfq(
            data, 'temperatura_ambiental')
        mapped_data['oxigeno_disuelto'] = formulas.float_pfq(
            data, 'oxigeno_disuelto')
        mapped_data['saturacion'] = formulas.get_saturation(
            mapped_data['oxigeno_disuelto'],
            mapped_data['altitud'],
            mapped_data['temperatura_agua']
        )
        mapped_data['turbidez'] = formulas.float_pfq(data, 'turbidez')
        mapped_data['nitratos'] = formulas.float_pfq(
            data, 'nitrogeno_de_nitratos')
        mapped_data['coliformes_fecales'] = True if data.get(
            'bacterias_coliformes_totales/coliformes_totales') == "Presencia" else False
        mapped_data['coliformes_totales'] = data.get(
            'bacterias_coliformes_totales/coliformes_totales')
        mapped_data['macroinvertebrados'] = formulas.get_macroinvertabrates(
            data)
        mapped_data['calificacion_macroinvertebrados'] = formulas.get_macroinvertebrates_average_score(
            mapped_data['macroinvertebrados'])
        mapped_data['calidad_hidromorfologica'] = formulas.get_ch(data)
        mapped_data['calidad_bosque_ribera'] = formulas.get_qbr(data)
        mapped_data['secciones'] = formulas.get_sections(data)
        mapped_data['ancho_cauce'] = formulas.custom_float(
            data, "caudal/ancho_total_del_cauce")
        mapped_data['distancia_recorrida_objeto'] = formulas.custom_float(
            data, "distancia_total_que_recorre_el_flotador")
        mapped_data['tiempo_recorrido_objeto'] = formulas.get_tiempo(data)
        mapped_data['profundidad_orilla'] = formulas.custom_float(
            data, "caudal/profundidad_en_la_orilla")
        mapped_data['caudal'] = formulas.get_caudal(mapped_data)
        mapped_data['macroinvertebrados_no_identificados'] = formulas.boolean(
            data, 'informacion_adicional/requieres_apoyo_para_identificar_y_clasificar_un_macroinvertebrado')
        mapped_data['archivos_adjuntos'] = data.get(
            'informacion_adicional/sube_tus_imagenes_aqui', [])
        mapped_data['create_date'] = parser.isoparse(
            self.raw_data['answer']['createDate'])
        insert_document('sites', mapped_data, {
            'nombre_sitio': mapped_data['nombre_sitio'],
            'project_id': mapped_data['project_id']
        })
        scores_calculation(self.site_id)

    def _get_user(self, email):
        user = get_collection('users', {
            'email': email,
            'activated': True,
            '_deleted': False,
        })
        if not user:
            return email
        return user[0]['_id'], user[0]['institution']

    def _get_sitio_de_referencias(self, data, year, month):
        sitio = get_collection(
            'sites', {
                'nombre_sitio': data.get('sitio_de_referencia'),
                'anio': year,
                'mes': month,
                'temporada': data.get('temporada'),
                'es_sitio_referencia': True
            }
        )
        if not sitio:
            return data.get('sitio_de_referencia') if data.get('sitio_de_referencia') != '' else None
        return ObjectId(sitio[0]['_id'])

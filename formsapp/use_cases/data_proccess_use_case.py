from formsapp.scripts.formsapp_parse import parse_data
from api.helpers.http_responses import created, error
from formsapp.scripts import formulas
from fcea_monitoreo.utils import get_collection, insert_document
from fcea_monitoreo.functions import get_altitude
from bson import ObjectId
from dateutil import parser


class DataProccessUseCase:
    def __init__(self, raw_data):
        self.raw_data = raw_data
        self.site_id = ObjectId()

    def proccess(self):
        data = parse_data(self.raw_data)
        try:
            self._insert_formsapp_raw_data(self.raw_data)
            self._insert_site(data)
            return created(['The data has been saved successfully'])
        except Exception as e:
            return error(e.args[0])

    def _insert_formsapp_raw_data(self, data):
        data['_id'] = self.site_id
        insert_document('formsapp_raw_data', data, {'_id': self.site_id})

    def _insert_site(self, data):
        mapped_data = {}
        mapped_data['_id'] = self.site_id
        mapped_data['project'] = self._get_project(data.get('cuenca'))
        mapped_data['es_sitio_de_referencia'] = formulas.get_es_sitio_de_referencia(data.get(
            'es_sitio_de_referencia'))
        mapped_data['sitio_de_referencia'] = self._get_sitio_de_referencias(
            data.get('sitio_de_referencia'))
        mapped_data['usuario'] = self._get_user_id(
            data.get('correo_electronico'))
        mapped_data['brigadistas'] = data.get(
            'nombre_de_las_y_los_integrantes_del_equipo')
        mapped_data['nombre_sitio'] = data.get('nombre_del_sitio')
        mapped_data['codigo_sitio'] = data.get('clave_del_sitio')
        mapped_data['ubicacion'] = data.get('location')
        mapped_data['latitud'] = float(data.get('latitude'))
        mapped_data['longitud'] = float(data.get('longitude'))
        mapped_data['altitud'] = float(get_altitude(
            mapped_data['latitud'], mapped_data['longitud']))
        mapped_data['tipo_de_cuerpo_de_agua'] = data.get(
            'selecciona_el_tipo_de_cuerpo_de_agua')
        mapped_data['fecha'] = parser.isoparse(data.get('fecha_del_monitoreo'))
        mapped_data['temporada'] = data.get('temporada')
        mapped_data['fotografia1'] = data.get(
            'fotografia_1')[0] if data.get('fotografia_1') else None
        mapped_data['fotografia2'] = data.get(
            'fotografia_2')[0] if data.get('fotografia_2') else None
        mapped_data['notas'] = data.get('notas_y_observaciones', '')
        mapped_data['ph'] = formulas.float_pfq(data, 'ph')
        mapped_data['amonio'] = formulas.float_pfq(data, 'nitrogeno_amoniacal')
        mapped_data['ortofosfatos'] = formulas.float_pfq(
            data, 'ortofosfatos')
        mapped_data['temperatura_del_agua'] = formulas.float_pfq(
            data, 'temperatura_del_agua')
        mapped_data['temperatura_ambiental'] = formulas.float_pfq(
            data, 'temperatura_ambiental')
        mapped_data['oxigeno_disuelto'] = formulas.float_pfq(
            data, 'oxigeno_disuelto')
        mapped_data['saturacion'] = formulas.get_saturation(
            mapped_data['oxigeno_disuelto'],
            mapped_data['altitud'],
            mapped_data['temperatura_del_agua']
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
        mapped_data['calidad_de_bosque_de_ribera'] = formulas.get_qbr(data)
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
        insert_document('sites', mapped_data, {
                        'nombre_sitio': mapped_data['nombre_sitio']})

    def _get_project(self, project):
        projects = get_collection('projects', {'name': project})
        if not projects:
            new_project = {
                '_id': ObjectId(),
                'name': project,
                'users': []
            }
            insert_document('projects', new_project, {
                            '_id': new_project['_id']})
            return new_project['_id']
        return projects[0]['_id']

    def _get_user_id(self, email):
        user = get_collection('users', {'email': email})
        if not user:
            return email
        return user[0]['_id']

    def _get_sitio_de_referencias(self, sitio_de_referencia):
        nombre_sitio = get_collection(
            'formsapp_answers', {'nombre_sitio': sitio_de_referencia})
        if not nombre_sitio:
            return sitio_de_referencia if sitio_de_referencia != '' else None
        return nombre_sitio[0]['_id']
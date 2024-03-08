from koboapp.scripts.kobo import kobo_request
from koboapp.scripts.formulas import *
from fcea_api_rest.utils import insert_document
from bson import ObjectId


class GetAssets:
    def execute(self):
        try:
            response = kobo_request(
                path='assets.json'
            )
            data = response.json()['results']
            filtered_data = [
                i for i in data if i['deployment_status'] == 'deployed']
            self.insert_assets_data(filtered_data)

        except Exception as e:
            return e.args

    def insert_assets_data(self, data):
        try:
            mapped_data = {}
            for item in data:
                mapped_data['_id'] = ObjectId()
                mapped_data['name'] = item.get('name')
                mapped_data['submission_count'] = item.get(
                    'deployment__submission_count')
                mapped_data['uid'] = item.get('uid')
                # mapped_data['update'] = False
                mapped_data['status'] = 'not updated'
                insert_document('assets', mapped_data)

        except Exception as e:
            return e.args

    def get_assets_byid(self, asset_uid):
        try:
            response = kobo_request(
                path=f'assets/{asset_uid}/data.json'
            )

            data = response.json()['results']
            self.insert_form_data(data)
            return data

        except Exception as e:
            return e.args

    def insert_form_data(self, data):
        try:
            mapped_data = {}
            for item in data:
                mapped_data['_id'] = item.get('_id')
                mapped_data['nombre_sitio'] = item.get(
                    'datos_generales/Nombre_sitio', '')
                mapped_data['codigo_sitio'] = item.get(
                    'datos_generales/Clave_del_sitio', '')
                mapped_data['brigada'] = item.get(
                    'datos_generales/Nombre_brigadistas', '')
                mapped_data['fecha'] = format_date(
                    item.get('datos_generales/Fecha'))
                mapped_data['tipo_de_cuerpo_de_agua'] = get_tipo_cuerpo_de_agua(
                    item)
                mapped_data['ubicacion'] = item.get(
                    'datos_generales/Ubicacion')
                location = item.get('datos_generales/Ubicacion')
                mapped_data['latitud'] = float(location.split()[0])
                mapped_data['longitud'] = float(location.split()[1])
                mapped_data['altitud'] = float(location.split()[2])
                mapped_data['codigo_formulario'] = item.get(
                    'datos_generales/Clave_sitio', '')
                mapped_data['es_sitio_de_referencia'] = get_es_sitio_de_referencia(
                    item.get('datos_generales/_Es_sitio_de_referencia'))
                mapped_data['nombre_usuario'] = get_username(
                    item.get('username'))
                mapped_data['notas'] = item.get('datos_generales/Notas')
                mapped_data['ph'] = float_pfq(item, 'pH')
                mapped_data['amonio'] = float_pfq(item, 'Amonio')
                mapped_data['ortofosfatos'] = float_pfq(item, 'Fosforo')
                mapped_data['temperatura_del_agua'] = float_pfq(
                    item, 'Temperatura_agua')
                mapped_data['temperatura_ambiental'] = float_pfq(
                    item, 'Temperatura_ambiental')
                mapped_data['oxigeno_disuelto'] = float_pfq(item, 'OD')
                mapped_data['saturacion'] = get_saturation(
                    mapped_data['oxigeno_disuelto'],
                    mapped_data['altitud'],
                    mapped_data['temperatura_del_agua']
                )
                mapped_data['turbidez'] = float_pfq(item, 'Turbidez')
                mapped_data['nitratos'] = float_pfq(item, 'Nitratos')
                mapped_data['coliformes_fecales'] = boolean(
                    item, f'parametros_biologicos/coliformes_fecales/faecal_coliforms')
                mapped_data['coliformes_totales'] = get_total_coliforms_text(
                    boolean(item, f'parametros_biologicos/coliformes_fecales/faecal_coliforms'))
                mapped_data['macroinvertebrados'] = get_macroinvertabrates(
                    item)
                mapped_data['calificacion_macroinvertebrados'] = get_macroinvertebrates_average_score(
                    get_macroinvertabrates(item))
                mapped_data['calidad_hidromorfologica'] = get_ch(item)
                mapped_data['calidad_de_bosque_de_ribera'] = get_qbr(item)
                mapped_data['vegetacion_de_ribera'] = get_riverside_vegetation(
                    item)
                mapped_data['secciones'] = get_sections(item)
                mapped_data['ancho_cauce'] = custom_float(
                    item, f"{FLOW}/Ancho_total_cauce")
                mapped_data['distancia_recorrida_objeto'] = custom_float(
                    item, f"{FLOW}/Distancia_recorrida")
                mapped_data['tiempo_recorrido_objeto'] = get_tiempo(item)
                mapped_data['profundidad_orilla'] = custom_float(
                    item, f"{FLOW}/Profundidad_orilla")
                mapped_data['caudal'] = get_caudal(mapped_data)
                mapped_data['volumen_de_agua'] = float_pfq(
                    item, "group_ii9io63/calculation_volumen_agua")
                mapped_data['macroinvertebrados_no_identificados'] = get_not_identified_macros(
                    item)
                mapped_data['id_formulario'] = item.get('_xform_id_string')
                mapped_data['archivos_adjuntos'] = item.get('_attachments')
                insert_document('submissions', mapped_data)

        except Exception as e:
            print(e.args)
            return e.args

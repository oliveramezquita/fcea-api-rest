from fcea_monitoreo.utils import insert_document, get_collection, update_document
from api.helpers.http_responses import ok, created, bad_request, error, not_found
from api.serializers.basin_serializer import BasinSerializer
from fcea_monitoreo.settings import BASE_URL
from django.core.files.storage import FileSystemStorage
from rest_framework import exceptions
from bson import ObjectId
from PIL import Image
import os


class BasinUseCase:
    def __init__(self, basin_data, basin_id=None):
        self.basin_data = self._querydict_to_dict(basin_data)
        self.basin_id = basin_id

    def create(self):
        self._validate_params()
        if self._insert():
            try:
                return created(['La cuenca ha sido creada correctamente'])
            except Exception as e:
                return error(e.args[0])
        return bad_request('La cuenca ya existe')

    def _validate_params(self):
        if 'name' not in self.basin_data:
            raise exceptions.ValidationError(
                "El nombre de la cuenca es obligatorio"
            )

        if 'institutions' not in self.basin_data:
            self.basin_data['institutions'] = []

    def _insert(self):
        self.basin_data['_id'] = ObjectId()
        self.basin_data['geojson_file'] = self._upload_geojson_file()
        self.basin_data['_deleted'] = False
        return insert_document(
            'basins',
            self.basin_data,
            {
                'name': self.basin_data['name'],
                '_deleted': False,
            }
        )

    def get(self):
        try:
            filters = {'_deleted': False}
            if self.basin_id:
                filters['_id'] = ObjectId(self.basin_id)
                basin = get_collection('basins', filters)
                if not basin:
                    return not_found(
                        f"Ninguna cuenca encontrada con el id: {str(self.basin_id)}"
                    )
                return ok(BasinSerializer(basin[0]).data)
            basins = get_collection('basins', filters)
            return ok(BasinSerializer(basins, many=True).data)
        except Exception as e:
            return error(e.args[0])

    def put(self):
        if '_id' in self.basin_data:
            del self.basin_data['_id']
        basin = get_collection('basins', {
            '_id': ObjectId(self.basin_id),
            '_deleted': False,
        })
        if not basin:
            return not_found(
                f"Ninguna cuenca encontrada con el id: {str(self.basin_id)}"
            )
        try:
            data = self._update()
            return ok(BasinSerializer(data).data)
        except Exception as e:
            return error(e.args[0])

    def _update(self):
        self.basin_data['geojson_file'] = self._upload_geojson_file()
        if not self.basin_data['geojson_file']:
            self._check_geojson_file()
            del self.basin_data['geojson_file']
        return update_document(
            'basins',
            {'_id': ObjectId(self.basin_id)},
            self.basin_data
        )

    def _check_geojson_file(self):
        basin = get_collection('basins', {
            '_id': ObjectId(self.basin_id),
            '_deleted': False,
        })
        if basin and basin[0]['geojson_file']:
            update_document(
                'basins',
                {'_id': ObjectId(self.basin_id)},
                {'geojson_file': None}
            )

    def _upload_geojson_file(self):
        if 'geojson_file' in self.basin_data:
            geojson_file = self.basin_data['geojson_file']
            fs = FileSystemStorage(
                location='media/files', base_url='media/files')
            filename = f'media/files/{geojson_file.name}'
            if os.path.exists(filename):
                os.remove(filename)

            ext = os.path.splitext(geojson_file.name)[1]
            if not ext.lower() in ['.geojson']:
                raise exceptions.ValidationError(
                    "El archivo no tiene el formato GeoJSON"
                )

            filename = fs.save(geojson_file.name, geojson_file)
            uploaded_file_url = fs.url(filename)
            return f"{BASE_URL}/{uploaded_file_url}"
        return None

    def _querydict_to_dict(self, basin_data):
        data = {}
        for key in basin_data.keys():
            v = basin_data.getlist(key)
            if len(v) == 1:
                v = v[0]
            data[key] = v
        return data

    def patch(self):
        if 'name' not in self.basin_data:
            raise exceptions.ValidationError(
                "El nombre de la institución es obligatorio"
            )
        basin = get_collection('basins', {
            '_id': ObjectId(self.basin_id),
            '_deleted': False
        })
        if not basin:
            return not_found(
                f"Ninguna cuenca encontrada con el id: {str(self.basin_id)}"
            )
        if 'delete' in self.basin_data and self.basin_data['delete'] == 'true':
            data = self._delete_institution(
                basin[0], self.basin_data['name'])
            return ok(BasinSerializer(data).data)
        basin[0] = self._check_institution(basin[0], self.basin_data['name'])
        self.basin_data['logo'] = self._upload_logo()
        try:
            basin[0]['institutions'].append(
                {
                    'name': self.basin_data['name'],
                    'url': self.basin_data['url'],
                    'logo': self.basin_data['logo'],
                }
            )
            data = update_document(
                'basins',
                {'_id': ObjectId(self.basin_id)},
                {'institutions': basin[0]['institutions']}
            )
            return ok(BasinSerializer(data).data)
        except Exception as e:
            return error(e.args[0])

    def _upload_logo(self):
        if 'logo' in self.basin_data:
            logo = self.basin_data['logo']
            fs = FileSystemStorage(
                location='media/images', base_url='media/images')
            filename = f'media/images/{logo.name}'
            if os.path.exists(filename):
                os.remove(filename)

            # TODO: Check validation of svg extension
            # if not self._is_valid_image_pillow(filename):
            #     raise exceptions.ValidationError(
            #         "El logotipo debe ser una imagen valida"
            #     )

            filename = fs.save(logo.name, logo)
            uploaded_logo_url = fs.url(filename)
            return f"{BASE_URL}/{uploaded_logo_url}"
        return None

    def _check_institution(self, basin, name_institution):
        index = next((index for (index, i) in enumerate(
            basin['institutions']) if i["name"] == name_institution), None)
        if isinstance(index, int) and index >= 0:
            del basin['institutions'][index]
        return basin

    def _is_valid_image_pillow(self, file_name):
        try:
            with Image.open(file_name) as img:
                img.verify()
                return True
        except (IOError, SyntaxError):
            return False

    def _delete_institution(self, basin, name_institution):
        index = next((index for (index, i) in enumerate(
            basin['institutions']) if i["name"] == name_institution), None)
        if index >= 0:
            del basin['institutions'][index]
            return update_document(
                'basins',
                {'_id': ObjectId(self.basin_id)},
                {'institutions': basin['institutions']}
            )
        return basin

    def delete(self):
        basin = get_collection('basins', {
            '_id': ObjectId(self.basin_id),
            '_deleted': False,
        })
        if not basin:
            return not_found(
                f"Ninguna cuenca encontrada con el id: {str(self.basin_id)}"
            )
        try:
            update_document(
                'basins',
                {'_id': ObjectId(self.basin_id)},
                {'_deleted': True}
            )
            return ok(['Cuenca eliminada exitosamente'])
        except Exception as e:
            return error(e.args[0])

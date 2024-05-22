from api.helpers.http_responses import ok, error, not_found
from fcea_monitoreo.utils import update_document, get_collection
from fcea_monitoreo.settings import BASE_URL
from api.serializers.project_serializer import ProjectSerializer
from api.scripts.send_form_link import send_form_link
from django.http import QueryDict
from django.core.files.storage import FileSystemStorage
from rest_framework import exceptions
from bson import ObjectId
import os


class UpdateProjectUseCase:
    def __init__(self, project_raw_data, project_id):
        self.project_raw_data = project_raw_data
        self.project_id = project_id
        self.geojson_file = None

    def execute(self):
        project = get_collection('projects', {
            '_id': ObjectId(self.project_id)
        })
        if not project:
            return not_found(
                f"No se encontró ningún proyecto con el id: {str(self.project_id)}"
            )
        elif 'geojson_file' in project[0]:
            self.geojson_file = project[0]['geojson_file']
        try:
            if isinstance(self.project_raw_data, QueryDict):
                data = self.upload_query_dict_data()
            else:
                data = self.update(project[0])
            return ok(ProjectSerializer(data).data)
        except Exception as e:
            return error(e.args[0])

    def update(self, project):
        if 'admin_users' in self.project_raw_data:
            for admin_user in self.project_raw_data['admin_users']:
                if 'url_form' in project['rfs_data'] and project['rfs_data']['url_form'] != '':
                    send_form_link(project, 'rfs_data', admin_user)
                if 'url_form' in project['its_data'] and project['its_data']['url_form'] != '':
                    send_form_link(project, 'its_data', admin_user)

        return update_document(
            'projects',
            {'_id': ObjectId(self.project_id)},
            self.project_raw_data
        )

    def upload_query_dict_data(self):
        data = self.querydict_to_dict()
        if 'geojson_file' in data:
            del data['geojson_file']
            self.upload_geojson_file()
        else:
            self.check_geojson_file()
        if 'admin_users' in data:
            data['admin_users'] = data['admin_users'].split(
                ',') if data['admin_users'] != '' else []
        if 'year' in data:
            data['year'] = int(data['year'])
        return update_document(
            'projects',
            {'_id': ObjectId(self.project_id)},
            data
        )

    def querydict_to_dict(self):
        data = {}
        for key in self.project_raw_data.keys():
            v = self.project_raw_data.getlist(key)
            if len(v) == 1:
                v = v[0]
            data[key] = v
        return data

    def upload_geojson_file(self):
        if 'geojson_file' in self.project_raw_data:
            geojson_file = self.project_raw_data['geojson_file']
            fs = FileSystemStorage(
                location='media/files', base_url='media/files')
            filename = f'media/files/{geojson_file.name}'
            if os.path.exists(filename):
                os.remove(filename)

            ext = os.path.splitext(geojson_file.name)[1]
            if not ext.lower() in ['.geojson']:
                raise exceptions.ValidationError(
                    "El archivo no es un GeoJSON"
                )

            filename = fs.save(geojson_file.name, geojson_file)
            uploaded_file_url = fs.url(filename)
            update_document(
                'projects',
                {'_id': ObjectId(self.project_id)},
                {'geojson_file': f"{BASE_URL}/{uploaded_file_url}"}
            )
        return []

    def check_geojson_file(self):
        if self.geojson_file:
            update_document(
                'projects',
                {'_id': ObjectId(self.project_id)},
                {'geojson_file': None}
            )

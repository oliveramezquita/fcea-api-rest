from api.helpers.http_responses import ok, error, not_found
from fcea_monitoreo.utils import update_document, get_collection
from rest_framework import exceptions
from api.scripts.send_form_link import send_form_link
from api.serializers.project_serializer import ProjectSerializer
from bson import ObjectId


class AssignProjectUseCase:
    def __init__(self, project_raw_data, project_id):
        self.project_raw_data = project_raw_data
        self.project_id = project_id
        self.site_type = project_raw_data['site_type']
        self.new_users = []

    def execute(self):
        self.validate_params()
        project = get_collection('projects', {
            '_id': ObjectId(self.project_id)
        })
        if not project:
            return not_found(
                f"No se encontró ningún proyecto con el id: {str(self.project_id)}"
            )
        try:
            data = self.match_projects(project[0])
            # data[self.site_type]['users_url_form'] = self.create_users_url_form(
            #     data)
            self.send_url_form(data)
            # data = self.set_reference_in_interest(data)
            updated_project = self.update(data)
            return ok(ProjectSerializer(updated_project).data)
        except Exception as e:
            return error(e.args[0])

    def validate_params(self):
        # validate requiere fields
        if 'url_form' not in self.project_raw_data[self.site_type]:
            raise exceptions.ValidationError(
                "La URL de forms.app es obligatoria"
            )

        if 'users' not in self.project_raw_data[self.site_type]:
            raise exceptions.ValidationError(
                "El usuario es obligatorio"
            )

    def match_projects(self, project):
        project[self.site_type]['url_form'] = self.project_raw_data[self.site_type]['url_form']
        if 'users' in project[self.site_type] and len(project[self.site_type]['users']) > 0:
            s = set(project[self.site_type]['users'])
            self.new_users = [
                x for x in self.project_raw_data[self.site_type]['users'] if x not in s]
        else:
            self.new_users = self.project_raw_data[self.site_type]['users']
        project[self.site_type]['users'] = self.project_raw_data[self.site_type]['users']

        return project

    def update(self, project):
        if '_id' in project:
            del project['_id']
        return update_document(
            'projects',
            {'_id': ObjectId(self.project_id)},
            project
        )

    def send_url_form(self, project):
        for user in self.new_users:
            send_form_link(project, self.site_type, user)

    # def set_reference_in_interest(self, project):
    #     if self.site_type == 'its_data':
    #         site_reference = get_collection('sites', {
    #             'project_id': ObjectId(project['_id']),
    #             'es_sitio_referencia': True,
    #         })[0]
    #         project['its_data']['rfs_name'] = site_reference['nombre_sitio']

    #     return project

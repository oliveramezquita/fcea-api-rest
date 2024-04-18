from api.helpers.http_responses import ok, error, not_found
from fcea_monitoreo.utils import update_document, get_collection
from api.serializers.project_serializer import ProjectSerializer
from api.scripts.send_form_link import send_form_link
from bson import ObjectId


class UpdateProjectUseCase:
    def __init__(self, project_raw_data, project_id):
        self.project_raw_data = project_raw_data
        self.project_id = project_id

    def execute(self):
        project = get_collection('projects', {
            '_id': ObjectId(self.project_id)
        })
        if not project:
            return not_found(
                f"No se encontró ningún proyecto con el id: {str(self.project_id)}"
            )
        try:
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
            {
                '_id': ObjectId(self.project_id),
            },
            self.project_raw_data
        )

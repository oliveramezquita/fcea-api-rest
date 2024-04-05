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
                f"No project found with id {str(self.project_id)}"
            )
        try:
            self.project_raw_data = self.match_projects(project[0])
            data = send_form_link(self.project_raw_data)
            self.update(data)
            return ok(ProjectSerializer(data).data)
        except Exception as e:
            return error(e.args[0])

    def match_projects(self, project):
        if 'name' in self.project_raw_data:
            project['name'] = self.project_raw_data['name']
        if 'users' in self.project_raw_data:
            project['users'] = self.project_raw_data['users']
        if 'form_link' in self.project_raw_data:
            project['form_link'] = self.project_raw_data['form_link']
        if 'temporada' in self.project_raw_data:
            project['temporada'] = self.project_raw_data['temporada']
        return project

    def update(self, project):
        return update_document(
            'projects',
            {
                '_id': ObjectId(project['_id']),
                'temporada': project['temporada'],
            },
            project
        )

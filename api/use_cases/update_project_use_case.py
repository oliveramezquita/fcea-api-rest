from api.helpers.http_responses import ok, error, not_found
from fcea_monitoreo.utils import update_document, get_collection
from api.serializers.project_serializer import ProjectSerializer
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
            data = self.update()
            return ok(ProjectSerializer(data).data)
        except Exception as e:
            return error(e.args[0])

    def update(self):
        return update_document(
            'projects',
            {
                '_id': ObjectId(self.project_id),
            },
            self.project_raw_data
        )

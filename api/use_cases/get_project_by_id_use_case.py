from fcea_monitoreo.utils import get_collection
from api.helpers.http_responses import error, ok, not_found
from api.serializers.project_serializer import ProjectSerializer
from bson import ObjectId


class GetProjectByIdUseCase:
    def __init__(self, request, project_id):
        self.project_id = project_id

    def execute(self):
        try:
            projects = get_collection('projects', {
                '_id': ObjectId(self.project_id)
            })
            if not projects:
                return not_found(f"No project found with id {str(self.project_id)}")
            return ok(ProjectSerializer(projects[0]).data)

        except Exception as e:
            return error(e.args[0])

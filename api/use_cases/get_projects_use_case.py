from api.helpers.http_responses import ok, error, not_found
from fcea_monitoreo.utils import get_collection
from api.serializers.project_serializer import ProjectSerializer


class GetProjectsUseCase:
    def execute(self):
        try:
            projects = get_collection('projects', {'_deleted': False})
            if len(projects) > 0:
                return ok(ProjectSerializer(projects, many=True).data)
            return ok([])
        except Exception as e:
            return error(e.args[0])

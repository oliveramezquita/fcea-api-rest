from rest_framework import views
from rest_framework.response import Response
from fcea_monitoreo.utils import get_collection
from koboapp.scripts.serializers import ProjectsSerializer, SubmissionSerializer
from koboapp.scripts.sync import sync_projects


class AllProjectsView(views.APIView):

    def get(self, request):
        projects = get_collection('projects', {})
        results = ProjectsSerializer(projects, many=True).data
        return Response(results)


class AllReferenceSitesView(views.APIView):

    def get(self, request):
        filter = {'es_sitio_de_referencia': True}

        # type of body of water
        water_body = self.request.query_params.get('waterbody')
        if water_body != None and water_body != '':
            filter['tipo_de_cuerpo'] = water_body

        # form id
        form_id = self.request.query_params.get('formid')
        if form_id != None and form_id != '':
            filter['id_formulario'] = form_id

        submission = get_collection('submission', filter)
        results = SubmissionSerializer(submission, many=True).data
        return Response(results)


class AllSubmissionView(views.APIView):

    def get(self, request):
        filter = {}

        # type of body of water
        water_body = self.request.query_params.get('waterbody')
        if water_body != None and water_body != '':
            filter['tipo_de_cuerpo'] = water_body

        # form id
        form_id = self.request.query_params.get('formid')
        if form_id != None and form_id != '':
            filter['id_formulario'] = form_id

        submission = get_collection('submission', filter)
        results = SubmissionSerializer(submission, many=True).data
        return Response(results)

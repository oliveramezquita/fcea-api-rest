from fcea_monitoreo.utils import get_collection
from api.helpers.http_responses import not_found, error
from urllib.parse import parse_qs
from django.http import HttpResponse
from bson import ObjectId
from datetime import datetime
import json


class GetSitesUseCase:
    def __init__(self, request):
        params = parse_qs(request.META['QUERY_STRING'])

        # project
        self.project = params['project'][0] if 'project' in params else None
        # state
        self.state = params['state'][0] if 'state' in params else None
        # institution
        self.institution = params['institution'][0] if 'institution' in params else None
        # dates
        self.dates = params['dates'][0] if 'dates' in params else None
        # parameter
        self.parameter = params['parameter'][0] if 'parameter' in params else None
        # site
        self.site = params['site'][0] if 'site' in params else None

    def execute(self):
        try:
            filters = {}
            if self.project:
                filters['project_id'] = ObjectId(self.project)
            if self.state:
                filters['estado'] = self.state
            if self.institution:
                filters['institucion'] = self.institution
            if self.dates:
                filters['fecha'] = self.filter_by_dates()
            if self.parameter:
                filters['parameter'] = self.parameter
            if self.site:
                filters['nombre_sitio'] = self.site
            sites = self.get_sites(filters)
            if len(sites) > 0:
                return HttpResponse(json.dumps(sites), content_type='application/json')
            return not_found("No existen sitios dados de alta hasta el momento")
        except Exception as e:
            return error(e.args[0])

    def filter_by_dates(self):
        dates = self.dates.split(" to ")
        return {'$gte': datetime.strptime(dates[0], '%Y-%m-%d'), '$lt': datetime.strptime(dates[1], '%Y-%m-%d')}

    def get_site_filters(self):
        try:
            projects = self.get_filter_projects()
            sites = get_collection(
                'sites', {'project_id': ObjectId(projects[0]['value'])})
            if sites:
                states = list(set(p['estado'] for p in sites))
                institution = list(set(p['institucion'] for p in sites))
                sites = list(set(p['nombre_sitio'] for p in sites))
                resp = {
                    'default_project': str(projects[0]['value']),
                    'projects': projects,
                    'states': states,
                    'institution': institution,
                    'sites': sites
                }
                return HttpResponse(json.dumps(resp), content_type='application/json')
            return not_found("No existen filtros actualmente")
        except Exception as e:
            return error(e.args[0])

    def get_filter_projects(self):
        projects = get_collection('projects')
        project_list = []
        for project in projects:
            sites = get_collection(
                'sites', {'project_id': ObjectId(project['_id'])})
            if sites:
                project_list.append(
                    {'value': str(project['_id']), 'title': project['name']})
        return project_list

    def get_sites(self, filters):
        sites = get_collection('sites', filters)
        resp_sites = []
        for site in sites:
            del site['create_date']
            site['_id'] = str(site['_id'])
            site['project_id'] = str(site['project_id'])
            site['sitio_referencia_id'] = str(
                site['sitio_referencia_id']) if site['sitio_referencia_id'] else None
            site['reference_site_scores'] = self.get_reference_site_scores(
                site['sitio_referencia_id'])
            site['user_id'] = str(site['user_id'])
            site['fecha'] = site['fecha'].isoformat()
            resp_sites.append(site)
        return resp_sites

    def get_reference_site_scores(self, sitio_referencia_id):
        sitio_referencia = get_collection(
            'sites', {
                '_id': ObjectId(sitio_referencia_id),
                'es_sitio_referencia': True
            })
        if sitio_referencia:
            return {
                'nombre_sitio': sitio_referencia[0]['nombre_sitio'],
                'ph': sitio_referencia[0]['ph'],
                'temperatura_agua': sitio_referencia[0]['temperatura_agua'],
                'temperatura_ambiental': sitio_referencia[0]['temperatura_ambiental'],
                'turbidez': sitio_referencia[0]['turbidez'],
                'nitratos': sitio_referencia[0]['nitratos'],
                'amonio': sitio_referencia[0]['amonio'],
                'ortofosfatos': sitio_referencia[0]['ortofosfatos'],
                'saturacion': sitio_referencia[0]['saturacion'],
                'oxigeno_disuelto': sitio_referencia[0]['oxigeno_disuelto'],
            }
        return None

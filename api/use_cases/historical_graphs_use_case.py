from fcea_monitoreo.utils import get_collection, distinct_collection
from django.http import HttpResponse
from urllib.parse import parse_qs
from bson import ObjectId
import json


class HistoricalGraphsUseCase:
    def __init__(self, request):
        params = parse_qs(request.META['QUERY_STRING'])

        # project
        self.basin = params['project'][0] if 'project' in params else None
        # monitoring period
        self.monitoring_period = str(params['monitoring_period'][0]).split(
        ) if 'monitoring_period' in params else []
        # year
        self.year = self.monitoring_period[1] if len(
            self.monitoring_period) > 0 else None
        # month
        self.month = self.monitoring_period[0] if len(
            self.monitoring_period) > 0 else None
        # season
        self.season = params['season'][0] if 'season' in params else None
        # state
        self.state = params['state'][0] if 'state' in params else None
        # institution
        self.institution = params['institution'][0] if 'institution' in params else None

    def execute(self):
        filters = {}
        if self.basin:
            basin = get_collection(
                'projects', {
                    'name': self.basin,
                    'year': int(self.year),
                    'month': self.month,
                    'season': self.season,
                    '_deleted': False,
                })
            if basin:
                filters['project_id'] = basin[0]['_id']
                if self.state:
                    filters['estado'] = self.state
                if self.institution:
                    filters['institucion'] = self.institution
        list_sites = self.get_sites(filters)
        labels = []
        series = {
            'calidad_general': [],
            'temperatura_agua': [],
            'ph': [],
            'oxigeno_disuelto': [],
            'turbidez': [],
            'nitratos': [],
            'amonio': [],
            'ortofosfatos': [],
            'calidad_bosque_ribera': [],
            'calidad_hidromorfologica': [],
            'calificacion_macroinvertebrados': [],
            'coliformes_totales': [],
            'caudal': []
        }
        months = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
                  'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
        years = distinct_collection('sites', 'anio', {'cuenca': self.basin})
        for ls in list_sites:
            for year in years:
                sites = get_collection(
                    'sites', {'cuenca': self.basin, 'anio': year, 'nombre_sitio': ls})
                # labels
                for month in months:
                    for site in sites:
                        if month == site['mes']:
                            label = f"{site['temporada']} {site['mes']} {site['anio']}"
                            if label not in labels:
                                labels.append(label)
                # series
                for _, (graph, data) in enumerate(series.items()):
                    for site in sites:
                        if not any(s['name'] == site['nombre_sitio'] for s in series[graph]):
                            series[graph].append({
                                'name': site['nombre_sitio'],
                                'type': 'area' if site['es_sitio_referencia'] else 'line',
                                'data': [self.get_value(site, graph)]
                            })
                        else:
                            serie = next(
                                (s for s in series[graph] if s['name'] == site['nombre_sitio']), None)
                            if serie:
                                serie['data'].append(
                                    self.get_value(site, graph))
        data = {
            'labels': labels,
            'series': series,
        }
        return HttpResponse(json.dumps(data), content_type='application/json')

    def get_value(self, site, graph):
        if graph == 'calidad_general':
            return site['scores']['total'][3]
        if graph == 'coliformes_totales':
            return site['scores']['fecal_coliforms'][0]
        return site[graph] if site[graph] else 0

    def get_sites(self, filters):
        sites = get_collection('sites', filters)
        resp_sites = []
        for site in sites:
            resp_sites.append(site['nombre_sitio'])
        return resp_sites

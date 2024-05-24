from fcea_monitoreo.utils import get_collection, distinct_collection
from django.http import HttpResponse
from bson import ObjectId
import json


class HistoricalGraphsUseCase:
    def __init__(self, request, basin):
        self.basin = basin

    def execute(self):
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
        for year in years:
            sites = get_collection(
                'sites', {'cuenca': self.basin, 'anio': year})
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

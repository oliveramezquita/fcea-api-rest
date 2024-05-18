from api.helpers.http_responses import error
from fcea_monitoreo.utils import get_collection
from urllib.parse import parse_qs
from django.http import HttpResponse
import json


class GraphsUseCase:
    def __init__(self, request):
        params = parse_qs(request.META['QUERY_STRING'])
        self.basin = params['basin'][0] if 'basin' in params else None
        self.parameter = params['parameter'][0] if 'parameter' in params else None

    def historical(self):
        series = []
        values = get_collection('sites', {'cuenca': self.basin})
        sites = list(set(v['nombre_sitio'] for v in values))
        # Step 1
        for site in sites:
            series.append({'name': site, 'data': []})
            # Step 2
            periods = list(filter(lambda p: p['nombre_sitio'] == site, values))
            idx = sites.index(site)
            for period in periods:
                series[idx]['data'].append(
                    {'x': f"{period['temporada']} {period['mes']} {period['anio']}", 'y': period['scores']['total'][0]})

        return HttpResponse(json.dumps(series), content_type='application/json')

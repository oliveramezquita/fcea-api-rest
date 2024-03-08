from koboapp.use_cases.get_assets import GetAssets
from django.http import HttpResponse
import os


def assets(request):
    assets = GetAssets()
    assets.execute()

    return HttpResponse("Assets")


def asset_results(request, asset_uid):
    assets = GetAssets()
    assets.get_assets_byid(asset_uid)

    return HttpResponse("Asset Results")

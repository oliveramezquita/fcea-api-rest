from koboapp.use_cases.get_assets import GetAssets
from django.http import HttpResponse


def assets(request):
    assets = GetAssets()
    assets_response = assets.execute()
    print(assets_response)

    return HttpResponse("Assets")


def asset_results(request, asset_uid):
    assets = GetAssets()
    mapped_data = assets.get_assets_byid(asset_uid)
    # print(mapped_data)

    return HttpResponse("Asset Results")

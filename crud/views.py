from django.http import HttpResponse
from koboapp.scripts.sync import sync_projects, sync_submission


def home(request):
    sync_projects()
    sync_submission()
    return HttpResponse("Home")

from django.urls import path
from koboapp import views


urlpatterns = [
    path('assets', views.assets, name='kobo-assets'),
    path('assets/<str:asset_uid>', views.asset_results, name='kobo-asset-results'),
]

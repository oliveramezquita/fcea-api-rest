from django.urls import path
from formsapp import views


urlpatterns = [
    path('data-proccess', views.DataProccessView.as_view(), name="data-proccess"),
    path('get-raw-data/<int:index>',
         views.RawDataView.as_view(), name="get-raw-data"),
]

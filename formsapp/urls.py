from django.urls import path
from formsapp import views


urlpatterns = [
    path('data-proccess', views.DataProccessView.as_view(), name="data-proccess"),
]

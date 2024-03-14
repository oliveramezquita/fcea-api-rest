from django.urls import path
from api import views


urlpatterns = [
    path('answers', views.AnswersView.as_view(), name="answers-view"),
    path('test-data', views.TestDataView.as_view(), name="test-data"),
]

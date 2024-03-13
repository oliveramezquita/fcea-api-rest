from django.urls import path
from api import views


urlpatterns = [
    path('answers', views.AnswersView.as_view(), name="answers-view"),
]

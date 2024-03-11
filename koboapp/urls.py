from django.urls import path
from koboapp import views


urlpatterns = [
    path('projects', views.AllProjectsView.as_view(), name='projects'),
    path('reference-sites', views.AllReferenceSitesView.as_view(),
         name='reference-sites'),
    path('submission', views.AllSubmissionView.as_view(), name='submission')
]

from django.urls import path
from api import views


urlpatterns = [
    path('register/<str:user_id>',
         views.UserRegisterView.as_view(), name='register'),
    path('users', views.UsersView.as_view(), name="users-view"),
    path('user/<str:user_id>', views.UserViewById.as_view(), name='user-view-by-id'),
    path('institutions-list', views.InstitutionsListView.as_view(),
         name="institutions-list-view"),
    path('catalog', views.CatalogView.as_view(), name="catalog_view"),
    path('catalog/<str:catalog_id>',
         views.CatalogViewById.as_view(), name="catalog-view-by-id"),
    path('login', views.LoginView.as_view(), name="login-view"),
    path('forgot-password', views.ForgotPasswordView.as_view(),
         name='forgot-password-view'),
    path('reset-password', views.ResetPasswordView.as_view(),
         name='reset-password-view'),
    path('projects', views.ProjectsView.as_view(), name="projects-view"),
    path('project/<str:project_id>',
         views.ProjectViewById.as_view(), name="project-view-by-id"),
    path('public-sites', views.PublicSitesView.as_view(),
         name="public-sites"),
    path('site-filters', views.SiteFiltersView.as_view(),
         name="site-filters"),
    path('faqs', views.FaqsView.as_view(), name="faqs-view"),
    path('test-data', views.TestDataView.as_view(), name="test-data"),
]

from django.urls import path
from api import views


urlpatterns = [
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
    path('projects', views.ProjectView.as_view(), name="projects-view"),
    path('project/<str:project_id>',
         views.ProjectViewById.as_view(), name="project-view-by-id"),
    path('test-data', views.TestDataView.as_view(), name="test-data"),
    path('encrypt', views.EncryptView.as_view(), name='test-encrypt'),
    path('test-form-email', views.TestEmailFormView.as_view(),
         name="test-form-email"),
    path('test-register-email', views.TestEmailRegisterView.as_view(),
         name="test-register-email"),
    path('test-reset-password-email', views.TestEmailResetPasswordView.as_view(),
         name="test-reset-password-email"),
]

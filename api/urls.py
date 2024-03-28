from django.urls import path
from api import views


urlpatterns = [
    path('answers', views.AnswersView.as_view(), name="answers-view"),
    path('test-data', views.TestDataView.as_view(), name="test-data"),
    path('formsapp', views.TestFormsappView.as_view(), name="test-formsapp"),
    path('users', views.UsersView.as_view(), name="users-view"),
    path('login', views.LoginView.as_view(), name="login-view"),
    path('forgot-password', views.ForgotPasswordView.as_view(),
         name='forgot-password-view'),
    path('reset-password', views.ResetPasswordView.as_view(),
         name='reset-password-view'),
    path('encrypt', views.EncryptView.as_view(), name='test-encrypt')
]

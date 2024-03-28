from rest_framework.views import APIView
from api.use_cases.save_answers_use_case import SaveAnswersUseCase
from api.use_cases.test_formsapp_use_case import TestFormsappUseCase
from api.use_cases.create_user_use_case import CreateUserUseCase
from api.use_cases.update_user_use_case import UpdateUserUseCase
from api.use_cases.login_use_case import LoginUseCase
from api.use_cases.forgot_password_use_case import ForgotPasswordUseCase
from api.use_cases.reset_password_use_case import ResetPasswordUseCase
from api.use_cases.get_users_use_case import GetUsersUseCase
from django.db.transaction import atomic


class AnswersView(APIView):
    def post(self, request):
        with atomic():
            answers_use_case = SaveAnswersUseCase(
                answers_raw_data=request.data)
            return answers_use_case.execute()


class TestDataView(APIView):
    def post(self, request):
        testdata_use_case = SaveAnswersUseCase(answers_raw_data=request.data)
        return testdata_use_case.test_data()


class TestFormsappView(APIView):
    def get(self, request):
        test_formsapp_use_case = TestFormsappUseCase()
        return test_formsapp_use_case.mapped_data()


class UsersView(APIView):
    def get(self, request):
        users_use_case = GetUsersUseCase(request)
        return users_use_case.execute()

    def post(self, request):
        with atomic():
            user_use_case = CreateUserUseCase(user_raw_data=request.data)
            return user_use_case.execute()

    def patch(self, request):
        with atomic():
            user_use_case = UpdateUserUseCase(user_raw_data=request.data)
            return user_use_case.execute()


class LoginView(APIView):
    def post(self, request):
        login_use_case = LoginUseCase(login_raw_data=request.data)
        return login_use_case.execute()


class ForgotPasswordView(APIView):
    def post(self, request):
        forgot_password_use_case = ForgotPasswordUseCase(raw_data=request.data)
        return forgot_password_use_case.execute()


class ResetPasswordView(APIView):
    def post(self, request):
        reset_password_use_case = ResetPasswordUseCase(raw_data=request.data)
        return reset_password_use_case.execute()


class EncryptView(APIView):
    def post(self, request):
        test = TestFormsappUseCase()
        return test.encrypt_test(raw_data=request.data)

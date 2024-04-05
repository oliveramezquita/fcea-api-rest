from rest_framework.views import APIView
from api.use_cases.save_answers_use_case import SaveAnswersUseCase
from api.use_cases.test_formsapp_use_case import TestFormsappUseCase
from api.use_cases.create_user_use_case import CreateUserUseCase
from api.use_cases.register_user_use_case import RegisterUserUseCase
from api.use_cases.update_user_use_case import UpdateUserUseCase
from api.use_cases.login_use_case import LoginUseCase
from api.use_cases.forgot_password_use_case import ForgotPasswordUseCase
from api.use_cases.reset_password_use_case import ResetPasswordUseCase
from api.use_cases.get_users_use_case import GetUsersUseCase
from api.use_cases.get_user_by_id_use_case import GetUserByIdUseCase
from api.use_cases.get_info_from_users_use_case import GetInfoFromUsersUseCase
from api.use_cases.create_catalog_use_case import CreateCatalogUseCase
from api.use_cases.get_catalogs_use_case import GetCatalogsUseCase
from api.use_cases.get_catalog_by_id_use_case import GetCatalogByIdUseCase
from api.use_cases.update_catalog_use_case import UpdateCatalogUseCase
from django.db.transaction import atomic


class AnswersView(APIView):
    def post(self, request):
        answers_use_case = SaveAnswersUseCase(
            answers_raw_data=request.data)
        return answers_use_case.execute()


class TestDataView(APIView):
    def post(self, request):
        testdata_use_case = SaveAnswersUseCase(answers_raw_data=request.data)
        return testdata_use_case.test_data()


class UsersView(APIView):
    def get(self, request):
        use_case = GetUsersUseCase(request)
        return use_case.execute()

    def post(self, request):
        use_case = CreateUserUseCase(user_raw_data=request.data)
        return use_case.execute()

    def patch(self, request):
        use_case = RegisterUserUseCase(user_raw_data=request.data)
        return use_case.execute()


class UserViewById(APIView):
    def get(self, request, user_id):
        use_case = GetUserByIdUseCase(request, user_id)
        return use_case.execute()

    def patch(self, request, user_id):
        with atomic():
            user_case = UpdateUserUseCase(
                user_raw_data=request.data,
                user_id=user_id
            )
            return user_case.execute()

    def delete(self, request, user_id):
        use_case = UpdateUserUseCase(
            user_raw_data={'_deleted': True},
            user_id=user_id
        )
        return use_case.delete()


class InstitutionsListView(APIView):
    def get(self, request):
        use_case = GetInfoFromUsersUseCase()
        return use_case.institutions_list()


class CatalogView(APIView):
    def post(self, request):
        catalog_use_case = CreateCatalogUseCase(catalog_raw_data=request.data)
        return catalog_use_case.execute()

    def get(self, request):
        catalog_use_case = GetCatalogsUseCase()
        return catalog_use_case.execute()


class CatalogViewById(APIView):
    def get(self, request, catalog_id):
        use_case = GetCatalogByIdUseCase(
            request=request, catalog_id=catalog_id)
        return use_case.execute()

    def patch(self, request, catalog_id):
        use_case = UpdateCatalogUseCase(
            catalog_raw_data=request.data, catalog_id=catalog_id)
        return use_case.execute()


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

from rest_framework.views import APIView
from api.use_cases.test_data_use_case import TestDataUseCase
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
from api.use_cases.get_projects_use_case import GetProjectsUseCase
from api.use_cases.get_project_by_id_use_case import GetProjectByIdUseCase
from api.use_cases.update_project_use_case import UpdateProjectUseCase
from api.use_cases.create_project_use_case import CreateProjectUseCase
from api.use_cases.assign_project_use_case import AssignProjectUseCase
from api.use_cases.get_faqs_use_case import GetFaqsUseCase
from api.use_cases.get_sites_use_case import GetSitesUseCase
from api.use_cases.basin_use_case import BasinUseCase
from api.use_cases.historical_graphs_use_case import HistoricalGraphsUseCase
from .middlewares import FceaAuthenticationMiddleware
from django.db.transaction import atomic


class UserRegisterView(APIView):
    def get(self, request, user_id):
        use_case = GetUserByIdUseCase(request, user_id)
        return use_case.not_registered()

    def post(self, request, user_id):
        with atomic():
            use_case = CreateUserUseCase(request.data)
            return use_case.execute()

    def put(self, request, user_id):
        with atomic():
            use_case = RegisterUserUseCase(request.data, user_id)
            return use_case.execute()


class PublicUserView(APIView):
    def get(self, request, user_id):
        use_case = GetUserByIdUseCase(request, user_id)
        return use_case.execute()


class UsersView(APIView):
    authentication_classes = [FceaAuthenticationMiddleware]

    def get(self, request):
        use_case = GetUsersUseCase(request)
        return use_case.execute()


class UserViewById(APIView):
    authentication_classes = [FceaAuthenticationMiddleware]

    def get(self, request, user_id):
        use_case = GetUserByIdUseCase(request, user_id)
        return use_case.execute()

    def patch(self, request, user_id):
        with atomic():
            user_case = UpdateUserUseCase(request.data, user_id)
            return user_case.execute()

    def delete(self, request, user_id):
        use_case = UpdateUserUseCase(
            user_raw_data={'_deleted': True},
            user_id=user_id
        )
        return use_case.delete()


class InstitutionsListView(APIView):
    authentication_classes = [FceaAuthenticationMiddleware]

    def get(self, request):
        use_case = GetInfoFromUsersUseCase()
        return use_case.institutions_list()


class CatalogView(APIView):
    authentication_classes = [FceaAuthenticationMiddleware]

    def post(self, request):
        with atomic():
            catalog_use_case = CreateCatalogUseCase(
                catalog_raw_data=request.data)
            return catalog_use_case.execute()

    def get(self, request):
        catalog_use_case = GetCatalogsUseCase()
        return catalog_use_case.execute()


class CatalogViewById(APIView):
    authentication_classes = [FceaAuthenticationMiddleware]

    def get(self, request, catalog_id):
        use_case = GetCatalogByIdUseCase(
            request=request, catalog_id=catalog_id)
        return use_case.execute()

    def patch(self, request, catalog_id):
        with atomic():
            use_case = UpdateCatalogUseCase(
                catalog_raw_data=request.data, catalog_id=catalog_id)
            return use_case.execute()

    def delete(self, request, catalog_id):
        use_case = UpdateCatalogUseCase(
            catalog_raw_data={'_deleted': True},
            catalog_id=catalog_id
        )
        return use_case.delete()


class ProjectsView(APIView):
    authentication_classes = [FceaAuthenticationMiddleware]

    def get(self, request):
        use_case = GetProjectsUseCase()
        return use_case.execute()

    def post(self, request):
        with atomic():
            use_case = CreateProjectUseCase(request.data)
            return use_case.execute()


class PublicSitesView(APIView):
    def get(self, request):
        use_case = GetSitesUseCase(request)
        return use_case.execute()


class SiteFiltersView(APIView):
    def get(self, request):
        use_case = GetSitesUseCase(request)
        return use_case.get_site_filters()


class ProjectViewById(APIView):
    authentication_classes = [FceaAuthenticationMiddleware]

    def get(self, request, project_id):
        use_case = GetProjectByIdUseCase(
            request=request, project_id=project_id)
        return use_case.execute()

    def put(self, request, project_id):
        with atomic():
            use_case = AssignProjectUseCase(request.data, project_id)
            return use_case.execute()

    def patch(self, request, project_id):
        with atomic():
            use_case = UpdateProjectUseCase(
                project_raw_data=request.data, project_id=project_id)
            return use_case.execute()

    def delete(self, request, project_id):
        use_case = UpdateProjectUseCase(request, project_id)
        return use_case.delete()


class LoginView(APIView):
    def post(self, request):
        login_use_case = LoginUseCase(login_raw_data=request.data)
        return login_use_case.execute()


class ForgotPasswordView(APIView):
    def post(self, request):
        forgot_password_use_case = ForgotPasswordUseCase(raw_data=request.data)
        return forgot_password_use_case.execute()


class ResetPasswordInsideView(APIView):
    def post(self, request):
        reset_password_use_case = ResetPasswordUseCase(raw_data=request.data)
        return reset_password_use_case.reset_password_inside()


class ResetPasswordOutsideView(APIView):
    def post(self, request):
        reset_password_use_case = ResetPasswordUseCase(raw_data=request.data)
        return reset_password_use_case.reset_password_outside()


class BasinsView(APIView):
    authentication_classes = [FceaAuthenticationMiddleware]

    def post(self, request):
        with atomic():
            use_case = BasinUseCase(request.data)
            return use_case.create()

    def get(self, request):
        use_case = BasinUseCase(request.data)
        return use_case.get()


class BasinViewById(APIView):
    authentication_classes = [FceaAuthenticationMiddleware]

    def get(self, request, basin_id):
        use_case = BasinUseCase(basin_data=request.data, basin_id=basin_id)
        return use_case.get()

    def put(self, request, basin_id):
        with atomic():
            use_case = BasinUseCase(basin_data=request.data, basin_id=basin_id)
            return use_case.put()

    def patch(self, request, basin_id):
        with atomic():
            use_case = BasinUseCase(basin_data=request.data, basin_id=basin_id)
            return use_case.patch()

    def delete(self, request, basin_id):
        use_case = BasinUseCase(basin_data=request.data, basin_id=basin_id)
        return use_case.delete()


class FaqsView(APIView):
    def get(self, request):
        use_case = GetFaqsUseCase()
        return use_case.execute()


class HistoricalGraphsView(APIView):
    def get(self, request):
        use_case = HistoricalGraphsUseCase(request)
        return use_case.execute()


class TestDataView(APIView):
    def post(self, request):
        testdata_use_case = TestDataUseCase(raw_data=request.data)
        return testdata_use_case.test_data()

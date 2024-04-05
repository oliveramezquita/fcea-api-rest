from rest_framework.views import APIView
from formsapp.use_cases.data_proccess_use_case import DataProccessUseCase


class DataProccessView(APIView):
    def post(self, request):
        use_case = DataProccessUseCase(raw_data=request.data)
        return use_case.proccess()

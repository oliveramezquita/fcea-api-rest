from rest_framework.views import APIView
from formsapp.use_cases.data_proccess_use_case import DataProccessUseCase
from formsapp.use_cases.get_raw_data_use_case import GetRawDataUseCase
from django.db.transaction import atomic


class DataProccessView(APIView):
    def post(self, request):
        with atomic():
            use_case = DataProccessUseCase(raw_data=request.data)
            return use_case.proccess()


class RawDataView(APIView):
    def get(self, request, index):
        use_case = GetRawDataUseCase(index=index)
        return use_case.execute()

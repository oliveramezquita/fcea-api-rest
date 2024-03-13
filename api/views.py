from rest_framework.views import APIView
from api.use_cases.save_answers_use_case import SaveAnswersUseCase
from django.db.transaction import atomic


class AnswersView(APIView):
    def post(self, request):
        with atomic():
            answers_use_case = SaveAnswersUseCase(
                answers_raw_data=request.data)
            return answers_use_case.execute()

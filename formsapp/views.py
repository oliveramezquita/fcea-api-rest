import logging
import traceback

from django.conf import settings
from django.db.transaction import atomic
from rest_framework.views import APIView

from api.helpers.http_responses import error
from formsapp.use_cases.data_proccess_use_case import DataProccessUseCase
from formsapp.use_cases.get_raw_data_use_case import GetRawDataUseCase
from formsapp.use_cases.get_scores_calculation_use_case import GetScoresCalculationUseCase
from fcea_monitoreo.functions import send_email

logger = logging.getLogger(__name__)


class DataProccessView(APIView):
    def post(self, request):
        # Intentamos obtener answerId desde el payload
        answer_id = (
            (request.data or {}).get("answer", {}).get("answerId")
            or (request.data or {}).get("answerId")
            or "unknown"
        )

        try:
            with atomic():
                use_case = DataProccessUseCase(raw_data=request.data)
                return use_case.proccess()

        except Exception as exc:
            tb = traceback.format_exc()

            # 1) Log local (con traceback)
            logger.error(
                f"Unhandled error in DataProccessView (answerId={answer_id}): {exc}",
                exc_info=True,
            )

            # 2) Correo (no permitas que falle y tumbe la respuesta)
            try:
                admin_email = getattr(settings, "ADMIN_EMAIL", None)
                if admin_email:
                    send_email(
                        template="mail_templated/error_log.html",
                        context={
                            "subject": f"[FCEA] Unhandled error DataProccess (answerId={answer_id})",
                            "answer_id": answer_id,
                            # aquí va SOLO lo útil (traceback)
                            "log_text": tb,
                            # IMPORTANTE: tu send_email usa context['email']
                            "email": admin_email,
                        },
                    )
                else:
                    logger.warning(
                        "ADMIN_EMAIL no está configurado; no se enviará correo.")
            except Exception:
                logger.error(
                    "No se pudo enviar correo de error (fallback).", exc_info=True)

            # 3) Respuesta controlada (evitas el 500 “crudo” de Django)
            return error([f"Fallo en procesamiento (answerId={answer_id}). Se registró en logs y se notificó por correo."])


class RawDataView(APIView):
    def get(self, request, index):
        use_case = GetRawDataUseCase(index=index)
        return use_case.execute()


class ScoreSynchronizationView(APIView):
    def get(self, request):
        use_case = GetScoresCalculationUseCase()
        return use_case.execute()

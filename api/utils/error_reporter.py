from django.conf import settings
from fcea_monitoreo.functions import send_email


def send_data_process_log_email(*, answer_id: str, log_text: str) -> None:
    admin_email = getattr(settings, "ADMIN_EMAIL", None)
    if not admin_email:
        return

    send_email(
        template="mail_templated/error_log.html",
        context={
            "subject": f"[FCEA] DataProccess issues (answerId={answer_id})",
            "email": admin_email,          # <- CLAVE
            "answer_id": answer_id,
            "log_text": log_text,
        },
    )

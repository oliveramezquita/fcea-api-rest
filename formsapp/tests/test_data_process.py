import json
from pathlib import Path
from unittest.mock import patch

from django.test import TestCase, override_settings
from rest_framework.test import APIClient

from api.helpers.http_responses import created


FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"


def load_fixture(name: str) -> dict:
    return json.loads((FIXTURES_DIR / name).read_text(encoding="utf-8"))


class DataProcessTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.client.raise_request_exception = False  # <- clave para poder assert 500
        # si tu proyecto usa slash final, ponlo
        self.url = "/monitoreo/formsapp/data-proccess"

    @patch("formsapp.views.DataProccessUseCase", autospec=True)
    @patch("fcea_monitoreo.functions.send_email", autospec=True)
    def test_ok_no_email(self, mock_send_email, MockUseCase):
        payload = load_fixture("ok.json")

        instance = MockUseCase.return_value
        instance.proccess.return_value = created(["ok"])  # <- NUNCA None

        res = self.client.post(self.url, payload, format="json")

        self.assertIn(res.status_code, (200, 201))
        mock_send_email.assert_not_called()

    @override_settings(ADMIN_EMAIL="admin@test.com")
    @patch("formsapp.use_cases.data_proccess_use_case.send_data_process_log_email", autospec=True)
    @patch("formsapp.use_cases.data_proccess_use_case.scores_calculation", autospec=True)
    @patch("formsapp.use_cases.data_proccess_use_case.parse_data", autospec=True)
    def test_issue_but_finishes_and_sends_email(
        self,
        mock_parse_data,
        mock_scores,
        mock_send_log_email,
    ):
        payload = load_fixture("ok.json")

        # parse ok
        mock_parse_data.return_value = {"dummy": True}

        # scores truena
        mock_scores.side_effect = Exception("scores_calculation failed (test)")

        # Evitamos ejecutar insert_site real
        with patch(
            "formsapp.use_cases.data_proccess_use_case.DataProccessUseCase._insert_site",
            autospec=True
        ) as mock_insert_site:

            def _fake_insert_site(self_uc, _data):
                self_uc._safe("scores_calculation",
                              lambda: mock_scores(self_uc.site_id))

            mock_insert_site.side_effect = _fake_insert_site

            res = self.client.post(self.url, payload, format="json")

        self.assertIn(res.status_code, (200, 201))

        # ✅ Debe haberse llamado el reporter
        self.assertTrue(mock_send_log_email.called)

        _, kwargs = mock_send_log_email.call_args

        self.assertEqual(kwargs["answer_id"], payload["answer"]["answerId"])
        self.assertIn("scores_calculation", kwargs["log_text"])

    @patch("formsapp.views.DataProccessUseCase", autospec=True)
    def test_500_unhandled(self, MockUseCase):
        """
        Caso: error NO controlado: la vista debe devolver 500 (y no explotar el test).
        """
        payload = load_fixture("ok.json")

        instance = MockUseCase.return_value
        instance.proccess.side_effect = Exception("boom")

        res = self.client.post(self.url, payload, format="json")
        self.assertEqual(res.status_code, 500)

from formsapp.scripts.sync.scores_calculation import scores_calculation
from api.helpers.http_responses import ok


class GetScoresCalculationUseCase:
    def execute(self):
        scores_calculation()
        return ok([])

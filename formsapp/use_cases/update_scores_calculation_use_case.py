from formsapp.scripts.sync.scores_calculation import scores_calculation


class UpdateScoresCalculationUseCase:
    def __init__(self, site_id):
        self.site_id = site_id

    def execute(self):
        return scores_calculation(self.site_id)

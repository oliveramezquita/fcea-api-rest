from api.helpers.http_responses import ok, error


class GetInstitutionsUseCase:
    def execute(self):
        try:
            return ok([])
        except Exception as e:
            return error(e.args[0])

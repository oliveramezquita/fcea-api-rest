from api.helpers.http_responses import ok, bad_request


class GetInstitutionsUseCase:
    def execute(self):
        try:
            return ok([])
        except Exception as e:
            return bad_request([e.args])

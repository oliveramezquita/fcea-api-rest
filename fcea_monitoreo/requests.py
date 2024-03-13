from requests import get
from decouple import config


def kobo_request(path):
    kobo_url = "https://kf.kobotoolbox.org/api/v2/"
    url = f'{kobo_url}{path}'
    headers = {
        "Authorization": f"Token {config('KOBO_TOKEN')}"
    }

    response = get(url=url, headers=headers)
    return response

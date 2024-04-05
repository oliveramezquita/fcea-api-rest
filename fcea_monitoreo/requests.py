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


def google_request(lat, lng):
    api_key = config('GOOGLE_API_KEY')
    google_url = "https://maps.googleapis.com/maps/api/elevation/json?locations="
    url = f'{google_url}{lat},{lng}&key={api_key}'
    return get(url=url)

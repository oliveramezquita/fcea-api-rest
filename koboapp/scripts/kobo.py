from requests import get


def kobo_request(path):
    kobo_url = "https://kf.kobotoolbox.org/api/v2/"
    url = f'{kobo_url}{path}'
    headers = {
        "Authorization": "Token 358d87003bfd0cf4fd5ef0f2628b8095c4f6b267"
    }

    response = get(url=url, headers=headers)
    return response

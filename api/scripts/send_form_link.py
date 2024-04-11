from fcea_monitoreo.utils import get_collection
from fcea_monitoreo.functions import send_email
from urllib import parse
from bson import ObjectId


def send_form_link(project, site_type):
    user = get_email_from_user(project[site_type]['users'])
    url_form = parse_url(project, user['email'], site_type)
    send_email(
        template="mail_templated/form.html",
        context={
            'subject': f"Formato de campo digital cuenca: {project['name']}",
            'email': user['email'],
            'user_name': f"{user['name']} {user['last_name']}",
            'project': project['name'],
            'link_href': url_form
        },
    )
    return url_form


def parse_url(project, email, site_type):
    # get base_url
    base_url = project[site_type]['url_form'].split('#')[0]

    # first step: change separator from url
    first_step = project[site_type]['url_form'].replace('#', '?')

    # second step: get params from first step
    second_step = parse.parse_qs(parse.urlparse(first_step).query)

    # last step: get kesy from params
    keys_list = list(second_step.keys())

    params = {}
    if isinstance(project[site_type]['users'], str):
        params[keys_list[0]] = email
    params[keys_list[1]] = project['name']

    return f"{base_url}#{parse.urlencode(params, quote_via=parse.quote)}"


def reference_site_name(project):
    reference_sites = get_collection(
        'sites',
        {
            'project': ObjectId(project['_id']),
            'temporada': project['temporada'],
            'es_sitio_de_referencia': True
        }
    )
    sites_name = []
    for reference_site in reference_sites:
        sites_name.append(reference_site['nombre_sitio'])

    return ', '.join(sites_name)


def get_email_from_user(user_id):
    user = get_collection(
        'users', {'_id': ObjectId(user_id), '_deleted': False})[0]
    return user

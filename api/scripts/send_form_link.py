from fcea_monitoreo.utils import get_collection
from urllib import parse
from bson import ObjectId


def send_form_link(project):
    # Enlace, Users email, Project name & Referece site
    if project['users'] and project['link']:
        for index, user in enumerate(project['users']):
            if user['status'] == 'SENT':
                # TODO: Enviar correo
                project['users'][index]['user_link'] = parse_url(
                    project, user['_id'])
                project['users'][index]['status'] = 'PENDING'
        print(project)


def parse_url(project, user_id):
    # get base_url
    base_url = project['form_link'].split('#')[0]

    # first step: change separator from url
    first_step = project['form_link'].replace('#', '?')

    # second step: get params from first step
    second_step = parse.parse_qs(parse.urlparse(first_step).query)

    # last step: get kesy from params
    keys_list = list(second_step.keys())

    params = {}
    params[keys_list[0]] = get_email_from_user(user_id)
    params[keys_list[1]] = project['name']
    params[keys_list[2]] = reference_site_name(project['_id'])
    return {'_id': user_id, 'status': 'PENDING', 'user_link': f"{base_url}#{parse.urlencode(params)}"}


def reference_site_name(project_id):
    reference_sites = get_collection(
        'sites',
        {'project': ObjectId(project_id), 'es_sitio_de_referencia': True}
    )
    sites_name = []
    for reference_site in reference_sites:
        sites_name.append(reference_site['nombre_sitio'])

    return ', '.join(sites_name)


def get_email_from_user(user_id):
    user = get_collection(
        'users', {'_id': ObjectId(user_id), '_deleted': False})[0]
    return user['email']

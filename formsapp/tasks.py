from formsapp.models import Project, Site


def data_synchronize(data, project_name, site_reference_name):
    project = Project.objects.filter(name=project_name).first()
    site_reference = Site.objects.filter(site_name=site_reference_name).first()

    Site.objects.create(
        project=project,
        site_reference=site_reference,
        reference_site_status=1 if data.get('es_sitio_referencia') else 0,
        brigadiers=data.get('brigadistas'),
        site_name=data.get('nombre_sitio'),
        site_code=data.get('codigo_sitio'),
        latitude=data.get('latitud'),
        longitude=data.get('longitud'),
        altitude=data.get('altitud'),
        state=data.get('estado'),
        city=data.get('ciudad'),
        type_body_water=data.get('tipo_cuerpo_agua'),
        date=data.get('fecha'),
        season=data.get('temporada'),
        photo_1=data.get('fotografia1'),
        photo_2=data.get('fotografia2'),
        notes=data.get('notas', None),
        ph=data.get('ph', None),
        amonio=data.get('amonio', None),
        ortofosfatos=data.get('ortofosfatos', None),
        water_temperature=data.get('temperatura_agua', None),
        environmental_temperature=data.get('temperatura_ambiental', None),
        dissolved_oxygen=data.get('oxigeno_disuelto', None),
        saturation=data.get('saturacion', None),
        turbidity=data.get('turbidez', None),
        nitrates=data.get('nitratos', None),
        fecal_coliforms_status=1 if data.get('coliformes_fecales') else 0,
        total_coliforms=data.get('coliformes_totales', None),
        macroinvertebrates=data.get('macroinvertebrados', []),
        macroinvertebrates_rating=data.get(
            'calificacion_macroinvertebrados', None),
        hydromorphological_quality=data.get('calidad_hidromorfologica', None),
        riparian_forest_quality=data.get('calidad_bosque_ribera', None),
        sections=data.get('secciones', []),
        channel_width=data.get('ancho_cauce', None),
        object_distance_traveled=data.get('distancia_recorrida_objeto', None),
        object_travel_time=data.get('tiempo_recorrido_objeto', None),
        shore_depth=data.get('profundidad_orilla', None),
        volume=data.get('caudal', None),
        unidentified_macroinvertebrates_status=1 if data.get(
            'macroinvertebrados_no_identificados') else 0,
        attached_files=data.get('archivos_adjuntos', []),
    )

from django.db import models


class customFloatField(models.Field):
    def db_type(self, connection):
        return 'float'


class Project(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    season = models.CharField(max_length=50)

    class Meta:
        db_table = "projects"


class Site(models.Model):
    id = models.AutoField(primary_key=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    site_reference = models.ForeignKey(
        "self", on_delete=models.CASCADE, null=True, blank=True)
    reference_site_status = models.BooleanField(default=0)
    brigadiers = models.CharField(max_length=255)
    site_name = models.CharField(max_length=100)
    site_code = models.CharField(max_length=50)
    latitude = customFloatField()
    longitude = customFloatField()
    altitude = customFloatField()
    state = models.CharField(max_length=100, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    type_body_water = models.CharField(max_length=50)
    date = models.DateTimeField()
    season = models.CharField(max_length=50)
    photo_1 = models.TextField()
    photo_2 = models.TextField()
    notes = models.TextField(null=True, blank=True)
    ph = customFloatField(null=True)
    amonio = customFloatField(null=True)
    ortofosfatos = customFloatField(null=True)
    water_temperature = customFloatField(null=True)
    environmental_temperature = customFloatField(null=True)
    dissolved_oxygen = customFloatField(null=True)
    saturation = customFloatField(null=True)
    turbidity = customFloatField(null=True)
    nitrates = customFloatField(null=True)
    fecal_coliforms_status = models.BooleanField(default=0)
    total_coliforms = models.CharField(max_length=50, null=True, blank=True)
    macroinvertebrates = models.JSONField(null=True)
    macroinvertebrates_rating = customFloatField(null=True)
    hydromorphological_quality = customFloatField(null=True)
    riparian_forest_quality = customFloatField(null=True)
    sections = models.JSONField(null=True)
    channel_width = customFloatField(null=True)
    object_distance_traveled = customFloatField(null=True)
    object_travel_time = customFloatField(null=True)
    shore_depth = customFloatField(null=True)
    volume = customFloatField(null=True)
    unidentified_macroinvertebrates_status = models.BooleanField(default=0)
    attached_files = models.JSONField(null=True)

    def is_reference_site(self):
        return bool(self.reference_site_status)

    def fecal_coliforms(self):
        return bool(self.fecal_coliforms_status)

    def unidentified_macroinvertebrates(self):
        return bool(self.unidentified_macroinvertebrates_status)

    class Meta:
        db_table = "sites"


class Synchronization(models.Model):
    id = models.AutoField(primary_key=True)
    site_id = models.CharField(max_length=50)
    scores_status = models.BooleanField(default=0)

    def scores(self):
        return bool(self.scores_status)

    class Meta:
        db_table = "synchronization"

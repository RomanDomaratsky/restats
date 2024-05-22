from django.db import models


class KyivApartment(models.Model):
    flat_id = models.IntegerField(blank=True, null=True)
    area_total = models.DecimalField(max_digits=4, decimal_places=1, blank=True, null=True)
    built_year = models.IntegerField(blank=True, null=True)
    currency = models.TextField(blank=True, null=True)
    district = models.TextField(blank=True, null=True)
    micro_district = models.TextField(blank=True, null=True)
    street = models.TextField(blank=True, null=True)
    house_number = models.TextField(blank=True, null=True)
    publication_date = models.DateField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    city = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    room_count = models.IntegerField(blank=True, null=True)
    floor = models.IntegerField(blank=True, null=True)
    insertion_date = models.DateField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'kyiv_apartments'

    def __str__(self):
        return f"{self.city} - {self.price} on {self.publication_date}"

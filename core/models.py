from django.db import models


class TimePeriod(models.Model):
    name = models.CharField(max_length=255)
    start_date_mya = models.IntegerField()
    end_date_mya = models.IntegerField()
    description = models.TextField(blank=True)

    def __str__(self):
        return str(self.name)


class OrganSystem(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    def __str__(self):
        return str(self.name)


class Organ(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    systems = models.ManyToManyField(OrganSystem, related_name="organs", blank=True)
    species = models.ForeignKey(
        "Species", related_name="organs", on_delete=models.CASCADE
    )

    def __str__(self):
        return str(self.name)


class Continent(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    def __str__(self):
        return str(self.name)


class Biome(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    def __str__(self):
        return str(self.name)


INORGANIC_ENERGY_SOURCE_CHOICES = {
    "chemo": "chemo",
    "sunlight": "sunlight",
}


class Species(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    genesis_mya = models.IntegerField()
    extinction_mya = models.IntegerField()
    lifetime_years = models.PositiveIntegerField()
    preys_upon = models.ManyToManyField("self", blank=True)
    inorganic_energy_source = models.CharField(
        max_length=16, choices=INORGANIC_ENERGY_SOURCE_CHOICES, null=True, blank=True
    )
    continent = models.ForeignKey(
        Continent, on_delete=models.SET_NULL, null=True, related_name="species"
    )
    biome = models.ForeignKey(
        Biome, on_delete=models.SET_NULL, null=True, related_name="species"
    )
    ancestor = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="descendants",
    )

    def _time_periods_overlap(self, other_species):
        return (
            self.genesis_mya <= other_species.extinction_mya
            and other_species.genesis_mya <= self.extinction_mya
        )

    def __str__(self):
        return str(self.name)

    class Meta:
        verbose_name_plural = "Species"

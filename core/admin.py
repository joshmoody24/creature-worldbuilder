from django.contrib import admin

from django.contrib import admin
from django import forms
from django.core.exceptions import ValidationError
from .models import TimePeriod, OrganSystem, Organ, Continent, Biome, Species


@admin.register(TimePeriod)
class TimePeriodAdmin(admin.ModelAdmin):
    list_display = ("name", "start_date_mya", "end_date_mya")
    search_fields = ("name",)
    ordering = ("-start_date_mya",)


@admin.register(OrganSystem)
class OrganSystemAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(Continent)
class ContinentAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(Biome)
class BiomeAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


class OrganInline(admin.TabularInline):
    model = Organ
    extra = 1


class SpeciesForm(forms.ModelForm):
    class Meta:
        model = Species
        fields = "__all__"

    def clean(self):
        cleaned_data = super().clean()
        instance = self.instance
        preys_upon = cleaned_data.get("preys_upon", [])

        # Perform the validation on the preys_upon data
        for prey in preys_upon:
            if not instance._time_periods_overlap(prey):
                raise ValidationError(
                    f"{instance.name} cannot prey upon {prey.name} as their time periods do not overlap."
                )

        return cleaned_data


@admin.register(Species)
class SpeciesAdmin(admin.ModelAdmin):
    form = SpeciesForm
    list_display = (
        "name",
        "genesis_mya",
        "extinction_mya",
        "lifetime_years",
        "continent",
        "biome",
        "ancestor",
    )
    search_fields = ("name", "description")
    list_filter = ("inorganic_energy_source", "continent", "biome")
    filter_horizontal = ("preys_upon",)
    autocomplete_fields = ("ancestor",)
    inlines = [OrganInline]

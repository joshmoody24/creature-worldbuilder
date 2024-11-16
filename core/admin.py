from django.contrib import admin

from django.contrib import admin
from django import forms
from django.core.exceptions import ValidationError
from .models import TimePeriod, OrganSystem, Organ, Region, Biome, Species


@admin.register(TimePeriod)
class TimePeriodAdmin(admin.ModelAdmin):
    list_display = ("name", "start_date_mya", "end_date_mya")
    search_fields = ("name",)
    ordering = ("-start_date_mya",)


@admin.register(OrganSystem)
class OrganSystemAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
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
    list_display = (
        "name",
        "genesis_date_mya",
        "extinction_date_mya",
        "lifetime_years",
        "region",
        "biome",
        "ancestor",
    )
    search_fields = ("name", "description")
    list_filter = ("inorganic_energy_source", "region", "biome")
    filter_horizontal = ("preys_upon",)
    autocomplete_fields = ("ancestor",)

    def get_form(self, request, obj=None, **kwargs):
        """
        Choose the form based on whether the object is being created or updated.
        """
        if obj is None:  # Object is being created
            class SpeciesCreationForm(forms.ModelForm):
                class Meta:
                    model = Species
                    fields = ["name", "ancestor"]

            self.form = SpeciesCreationForm
        else:  # Object is being updated
            self.form = SpeciesForm
        return super().get_form(request, obj, **kwargs)

    def get_inlines(self, request, obj):
        """
        Show inlines only when editing an existing species.
        """
        if obj:  # Only show inlines if the object exists (i.e., not during creation)
            return [OrganInline]
        return []

    def save_model(self, request, obj, form, change):
        """
        Handle deep copying of settings and organs from the ancestor species when creating a new species.
        """
        is_new = obj.pk is None  # Check if this is a new object

        # Ensure that required fields are set for creation
        if is_new and obj.ancestor:
            ancestor = obj.ancestor

            # Copy essential fields from the ancestor
            obj.description = ancestor.description
            obj.genesis_date_mya = ancestor.genesis_date_mya
            obj.extinction_date_mya = ancestor.extinction_date_mya
            obj.lifetime_years = ancestor.lifetime_years  # Ensure this field is set
            obj.inorganic_energy_source = ancestor.inorganic_energy_source
            obj.region = ancestor.region
            obj.biome = ancestor.biome

        # Save the species instance first
        super().save_model(request, obj, form, change)

        if is_new and obj.ancestor:
            # Copy the `preys_upon` Many-to-Many field
            obj.preys_upon.set(ancestor.preys_upon.all())

            # Deep copy organs
            ancestor_organs = ancestor.organs.prefetch_related("systems").all()

            new_organs = []
            system_mappings = {}
            for organ in ancestor_organs:
                new_organ = Organ(
                    name=organ.name,
                    description=organ.description,
                    species=obj,
                )
                new_organs.append(new_organ)

            # Bulk create new organs
            Organ.objects.bulk_create(new_organs)

            # Set organ systems for the new organs
            for new_organ, original_organ in zip(new_organs, ancestor_organs):
                system_mappings[new_organ] = list(original_organ.systems.all())

            for organ, systems in system_mappings.items():
                organ.systems.set(systems)

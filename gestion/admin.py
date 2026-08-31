from django.contrib import admin

from .models import Animal, Crop, Harvest, Incubator, Notification, Plot, Poultry, Season, UserProfile


@admin.register(Season)
class SeasonAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_date', 'end_date', 'description')
    search_fields = ('name', 'description')
    list_filter = ('start_date', 'end_date')


@admin.register(Plot)
class PlotAdmin(admin.ModelAdmin):
    list_display = ('name', 'area', 'location', 'soil_type')
    search_fields = ('name', 'location', 'soil_type')
    list_filter = ('soil_type',)


@admin.register(Crop)
class CropAdmin(admin.ModelAdmin):
    list_display = ('name', 'crop_type', 'planting_date', 'expected_harvest_date', 'status', 'season')
    search_fields = ('name', 'crop_type', 'status')
    list_filter = ('status', 'season')
    actions = ['mark_as_harvested']

    def mark_as_harvested(self, request, queryset):
        queryset.update(status='Récolté')

    mark_as_harvested.short_description = 'Marquer comme récolté'


@admin.register(Harvest)
class HarvestAdmin(admin.ModelAdmin):
    list_display = ('crop', 'harvest_date', 'quantity')
    search_fields = ('crop__name', 'notes')
    list_filter = ('harvest_date',)


@admin.register(Animal)
class AnimalAdmin(admin.ModelAdmin):
    list_display = ('name', 'number', 'species', 'breed', 'health_status')
    search_fields = ('name', 'number', 'breed')
    list_filter = ('species', 'health_status')


@admin.register(Poultry)
class PoultryAdmin(admin.ModelAdmin):
    list_display = ('species', 'entries', 'exits', 'deaths', 'egg_production')
    search_fields = ('species', 'notes')
    list_filter = ('species',)


@admin.register(Incubator)
class IncubatorAdmin(admin.ModelAdmin):
    list_display = ('eggs_count', 'incubation_date', 'hatch_date', 'status')
    search_fields = ('status', 'notes')
    list_filter = ('status', 'incubation_date')


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'notification_type', 'is_read', 'created_at')
    list_filter = ('notification_type', 'is_read')
    search_fields = ('title', 'message')


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'is_active', 'phone')
    list_filter = ('role', 'is_active')
    search_fields = ('user__username', 'phone')

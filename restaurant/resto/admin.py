from django.contrib import admin

# Register your models here.
from resto import models

# admin.site.register(models.MenuItem)
admin.site.register(models.TimeSlot)
admin.site.register(models.Reservation)
admin.site.register(models.Order)
# admin.site.register(models.Section)
admin.site.register(models.Table)
admin.site.register(models.CoinTransaction)

from .models import Section, MenuItem

@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']

@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ['name', 'section', 'price', 'is_available']
    list_filter = ['section', 'is_available']
    search_fields = ['name']
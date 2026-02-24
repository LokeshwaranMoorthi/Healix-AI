from django.contrib import admin
from .models import PrescriptionRecord

@admin.register(PrescriptionRecord)
class PrescriptionAdmin(admin.ModelAdmin):
    list_display = ('id', 'created_at')
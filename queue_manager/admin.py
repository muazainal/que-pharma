from django.contrib import admin
from .models import PharmacistProfile, PrescriptionTicket

@admin.register(PrescriptionTicket)
class PrescriptionTicketAdmin(admin.ModelAdmin):
    list_display = ('queue_number', 'patient_name', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('patient_name', 'queue_number')

@admin.register(PharmacistProfile)
class PharmacistProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'employee_id')
    search_fields = ('user__username', 'employee_id')

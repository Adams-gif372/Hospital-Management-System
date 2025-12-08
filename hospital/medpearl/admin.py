from django.contrib import admin
from .models import Doctor, Patient, Appointment
# Register your models here.
@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ('name', 'speciality')
    search_fields = ('name', 'speciality')

@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ('user', 'address', 'contact')
    search_fields = ('user__username', 'address', 'contact')

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('patient', 'doctor', 'date', 'status')
    list_filter = ('status', 'doctor')
    search_fields = ('patient__user__username', 'doctor__name', 'symptoms')
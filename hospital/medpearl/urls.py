from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name="home"),
    path('about/', views.about, name="about"),
    path('contact/', views.contact, name="contact"),
    path('doctors/', views.doctors, name="doctors"),
    path('doctors/<int:doctor_id>/', views.doctor_profile, name='doctor_profile'),
    path('register/', views.patient_register, name='register'),
    path('login/', views.patient_login, name='login'),
    path('logout/', views.patient_logout, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('book-appointment/', views.book_appointment, name='book_appointment'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('payment/<int:appointment_id>/', views.initiate_payment, name="initiate_payment"),
    path("mpesa/callback/", views.mpesa_callback, name="mpesa_callback"),
    path("appointment/<int:appointment_id>/accept/", views.accept_appointment, name="accept_appointment"),
]
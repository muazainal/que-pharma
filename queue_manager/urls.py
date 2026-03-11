from django.urls import path
from . import views

urlpatterns = [
    path('', views.patient_portal, name='patient_portal'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('track/<uuid:ticket_id>/', views.track_ticket, name='track_ticket'),
    
    # APIs
    path('api/tickets/', views.api_ticket_list, name='api_ticket_list'),
    path('api/check-status/<uuid:ticket_id>/', views.api_check_status, name='api_check_status'),
    path('api/create-ticket/', views.api_create_ticket, name='api_create_ticket'),
    path('api/update-status/<uuid:ticket_id>/', views.api_update_status, name='api_update_status'),
    path('api/update-contact/<uuid:ticket_id>/', views.api_update_contact, name='api_update_contact'),
    path('api/lookup-ticket/', views.api_lookup_ticket, name='api_lookup_ticket'),
    path('api/qr/<uuid:ticket_id>/', views.generate_qr, name='generate_qr'),
]

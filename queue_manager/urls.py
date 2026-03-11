"""
Que-Pharma URL Configuration
Maps URL paths to their corresponding view functions.
Organized into Public Pages, Support/Auth Pages, and Data APIs.
"""

from django.urls import path
from . import views

urlpatterns = [
    # -------------------------------------------------------------------------
    # PUBLIC PAGES: For Patients
    # -------------------------------------------------------------------------
    path('', views.patient_portal, name='patient_portal'),
    path('track/<uuid:ticket_id>/', views.track_ticket, name='track_ticket'),
    
    # -------------------------------------------------------------------------
    # STAFF PORTAL: For Pharmacists (Management & Authentication)
    # -------------------------------------------------------------------------
    path('dashboard/', views.dashboard, name='dashboard'),
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # -------------------------------------------------------------------------
    # REAL-TIME APIs: For dynamic frontend interactions
    # -------------------------------------------------------------------------
    
    # Global ticket operations
    path('api/tickets/', views.api_ticket_list, name='api_ticket_list'),
    path('api/create-ticket/', views.api_create_ticket, name='api_create_ticket'),
    path('api/lookup-ticket/', views.api_lookup_ticket, name='api_lookup_ticket'),
    
    # Single ticket operations (Identification via UUID)
    path('api/check-status/<uuid:ticket_id>/', views.api_check_status, name='api_check_status'),
    path('api/update-status/<uuid:ticket_id>/', views.api_update_status, name='api_update_status'),
    path('api/update-contact/<uuid:ticket_id>/', views.api_update_contact, name='api_update_contact'),
    
    # Utilities: QR Generation for tracking mobilization
    path('api/qr/<uuid:ticket_id>/', views.generate_qr, name='generate_qr'),
]

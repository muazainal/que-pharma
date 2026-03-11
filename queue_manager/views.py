"""
Que-Pharma Application Views
Handles routing logic for both the Patient Portal and Pharmacist Dashboard.
Includes a suite of JSON APIs for real-time frontend interaction.
"""

import json
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from django.conf import settings
from .models import PrescriptionTicket, PharmacistProfile
from .utils import produce_qr_code

# -----------------------------------------------------------------------------
# PUBLIC PORTAL VIEWS (Patients)
# -----------------------------------------------------------------------------

def patient_portal(request):
    """Renders the main entry point where patients can look up their tickets."""
    return render(request, 'patient_portal.html')

def track_ticket(request, ticket_id):
    """
    Renders the individual tracking page for a specific prescription.
    Patients use this to monitor real-time status updates.
    """
    ticket = get_object_or_404(PrescriptionTicket, id=ticket_id)
    return render(request, 'patient_status.html', {'ticket': ticket})

# -----------------------------------------------------------------------------
# AUTHENTICATION VIEWS (Pharmacists)
# -----------------------------------------------------------------------------

def signup_view(request):
    """
    Handles secure pharmacist registration.
    Requires a master Pharmacy Secret Key and a unique Employee ID for accountability.
    """
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        pharma_secret = request.POST.get('pharma_secret')
        employee_id = request.POST.get('employee_id')
        
        # Security Guard: Only authorized personnel with the master key can join
        if pharma_secret != settings.PHARMACY_REGISTRATION_KEY:
            messages.error(request, 'Invalid Pharmacy Secret Key.')
            return render(request, 'registration/signup.html', {'form': form})
        
        # ID Validation: Prevent duplicate staff identifiers
        if PharmacistProfile.objects.filter(employee_id=employee_id).exists():
            messages.error(request, 'This Employee ID is already registered.')
            return render(request, 'registration/signup.html', {'form': form})
            
        if form.is_valid():
            user = form.save()
            # Link the new Employee ID to the user's staff profile
            profile = user.profile
            profile.employee_id = employee_id
            profile.save()
            
            login(request, user)
            return redirect('dashboard')
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})

def login_view(request):
    """Standard secure login for existing pharmacists."""
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('dashboard')
    else:
        form = AuthenticationForm()
    return render(request, 'registration/login.html', {'form': form})

def logout_view(request):
    """Terminating the staff session and redirecting to the login gate."""
    logout(request)
    return redirect('login')

# -----------------------------------------------------------------------------
# MANAGEMENT VIEWS (Pharmacist Dashboard)
# -----------------------------------------------------------------------------

@login_required
def dashboard(request):
    """The central command hub for pharmacists to manage the prescription queue."""
    return render(request, 'dashboard.html')

# -----------------------------------------------------------------------------
# JSON API ENDPOINTS (Real-time interactions)
# -----------------------------------------------------------------------------

def api_ticket_list(request):
    """Returns a list of all active (non-collected) tickets for the dashboard."""
    tickets = PrescriptionTicket.objects.exclude(status='Collected').order_by('created_at')
    data = []
    for t in tickets:
        # Determine the name and ID of the pharmacist who last touched the ticket
        pharmacist_name = 'Unknown'
        target_user = t.updated_by or t.created_by
        if target_user:
            pharmacist_name = target_user.username
            if hasattr(target_user, 'profile'):
                pharmacist_name = f"{target_user.username} ({target_user.profile.employee_id})"

        data.append({
            'id': str(t.id),
            'queue_number': t.queue_number,
            'patient_name': t.patient_name,
            'phone_number': t.phone_number,
            'status': t.status,
            'created_at': t.created_at.strftime('%H:%M:%S'),
            'pharmacist': pharmacist_name
        })
    return JsonResponse({'tickets': data})

def api_check_status(request, ticket_id):
    """Lightweight polling endpoint for patient tracking pages."""
    ticket = get_object_or_404(PrescriptionTicket, id=ticket_id)
    return JsonResponse({
        'id': str(ticket.id),
        'status': ticket.status,
        'patient_name': ticket.patient_name,
        'queue_number': ticket.queue_number,
    })

@csrf_exempt
def api_create_ticket(request):
    """Staff API: Creates a new prescription entry and assigns a queue number."""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            # Find the next sequential queue number
            last_ticket = PrescriptionTicket.objects.order_by('-queue_number').first()
            queue_num = (last_ticket.queue_number + 1) if last_ticket else 1
            
            ticket = PrescriptionTicket.objects.create(
                queue_number=queue_num,
                patient_name=data.get('patient_name'),
                phone_number=data.get('phone_number', ''),
                created_by=request.user if request.user.is_authenticated else None
            )
            return JsonResponse({'status': 'success', 'id': str(ticket.id)})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error'}, status=400)

@csrf_exempt
def api_update_status(request, ticket_id):
    """Staff API: Transition a ticket between 'Preparing', 'Ready', and 'Collected'."""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            ticket = get_object_or_404(PrescriptionTicket, id=ticket_id)
            ticket.status = data.get('status')
            if request.user.is_authenticated:
                ticket.updated_by = request.user
            ticket.save()
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error'}, status=400)

@csrf_exempt
def api_lookup_ticket(request):
    """Patient API: Searches for active tickets by phone number."""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            phone = data.get('phone_number')
            # Look for recent active tickets associated with this phone number
            ticket = PrescriptionTicket.objects.filter(phone_number__icontains=phone).exclude(status='Collected').order_by('-created_at').first()
            if ticket:
                return JsonResponse({'status': 'success', 'id': str(ticket.id)})
            return JsonResponse({'status': 'not_found'}, status=404)
        except Exception as e:
            return JsonResponse({'status': 'error'}, status=400)
    return JsonResponse({'status': 'error'}, status=400)

@csrf_exempt
def api_update_contact(request, ticket_id):
    """Patient API: Allows patients to voluntarily link their phone number to an existing ticket."""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            ticket = get_object_or_404(PrescriptionTicket, id=ticket_id)
            ticket.phone_number = data.get('phone_number')
            ticket.save()
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error'}, status=400)
    return JsonResponse({'status': 'error'}, status=400)

def generate_qr(request, ticket_id):
    """Utility View: Generates a QR code image that redirects to the ticket's tracking page."""
    ticket = get_object_or_404(PrescriptionTicket, id=ticket_id)
    track_url = request.build_absolute_uri(f'/track/{ticket.id}/')
    qr_image_data = produce_qr_code(track_url)
    return HttpResponse(qr_image_data, content_type="image/png")

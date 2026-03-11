import json
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import PrescriptionTicket
from .utils import produce_qr_code

def patient_portal(request):
    return render(request, 'patient_portal.html')

@login_required
def dashboard(request):
    return render(request, 'dashboard.html')

def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})

def login_view(request):
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
    logout(request)
    return redirect('login')

def track_ticket(request, ticket_id):
    ticket = get_object_or_404(PrescriptionTicket, id=ticket_id)
    return render(request, 'patient_status.html', {'ticket': ticket})

def api_ticket_list(request):
    tickets = PrescriptionTicket.objects.exclude(status='Collected').order_by('created_at')
    data = []
    for t in tickets:
        data.append({
            'id': str(t.id),
            'queue_number': t.queue_number,
            'patient_name': t.patient_name,
            'phone_number': t.phone_number, # Added phone number here
            'status': t.status,
            'created_at': t.created_at.strftime('%H:%M:%S'),
            'pharmacist': t.updated_by.username if t.updated_by else (t.created_by.username if t.created_by else 'Unknown')
        })
    return JsonResponse({'tickets': data})

def api_check_status(request, ticket_id):
    ticket = get_object_or_404(PrescriptionTicket, id=ticket_id)
    return JsonResponse({
        'id': str(ticket.id),
        'status': ticket.status,
        'patient_name': ticket.patient_name,
        'queue_number': ticket.queue_number,
    })

@csrf_exempt
def api_create_ticket(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
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
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            phone = data.get('phone_number')
            ticket = PrescriptionTicket.objects.filter(phone_number__icontains=phone).exclude(status='Collected').order_by('-created_at').first()
            if ticket:
                return JsonResponse({'status': 'success', 'id': str(ticket.id)})
            return JsonResponse({'status': 'not_found'}, status=404)
        except Exception as e:
            return JsonResponse({'status': 'error'}, status=400)
    return JsonResponse({'status': 'error'}, status=400)

@csrf_exempt
def api_update_contact(request, ticket_id):
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
    ticket = get_object_or_404(PrescriptionTicket, id=ticket_id)
    track_url = request.build_absolute_uri(f'/track/{ticket.id}/')
    qr_image_data = produce_qr_code(track_url)
    return HttpResponse(qr_image_data, content_type="image/png")

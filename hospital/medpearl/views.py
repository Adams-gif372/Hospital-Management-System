from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from .models import Doctor, Patient, Appointment, Payment
from .forms import PatientRegisterForm, AppointmentForm
from django.http import JsonResponse
from .mpesa import stk_push
from django.views.decorators.csrf import csrf_exempt
import json
from .forms import MeetingLinkForm
import uuid
# Create your views here.
def is_admin(user):
    return user.is_superuser

def home(request):
    images = ["hospital_1.jpg", "hospital_2.jpg"]
    return render(request, "hospital/home.html", {"images": images})

def about(request):
    images = ["hospital_1.jpg", "hospital_2.jpg"]
    return render(request, "hospital/about.html", {"images": images})

def contact(request):
    return render(request, "hospital/contact.html")

def doctors(request):
    doctors = Doctor.objects.all()
    return render(request, "hospital/doctors.html", {"doctors": doctors})

def doctor_profile(request, doctor_id):
    doctor = get_object_or_404(Doctor, id=doctor_id)
    return render(request, "hospital/doctor_profile.html", {"doctor": doctor})

def patient_register(request):
    if request.method == "POST":
        form = PatientRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            address = form.cleaned_data["address"]
            contact = form.cleaned_data["contact"]
            Patient.objects.create(user=user, address=address, contact=contact)
            login(request, user)
            return redirect("dashboard")
    else:
        form = PatientRegisterForm()
    return render(request, "hospital/patient_register.html", {"form": form})

def patient_login(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect("dashboard")
    else:
        form = AuthenticationForm()
    return render(request, "hospital/patient_login.html", {"form": form})

@login_required
def patient_logout(request):
    logout(request)
    return redirect("home")

@login_required
def dashboard(request):
    patient = Patient.objects.get(user=request.user)
    appointments = Appointment.objects.filter(patient=patient)
    return render(request, "hospital/dashboard.html", {"appointments": appointments})

@login_required
def book_appointment(request):
    patient = Patient.objects.get(user=request.user)
    if request.method == "POST":
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appt = form.save(commit=False)
            appt.patient = patient
            appt.status = "Pending"
            appt.save()
            return redirect("dashboard")
    else:
        form = AppointmentForm()
    return render(request, "hospital/book_appointment.html", {"form": form})

@user_passes_test(is_admin)
def admin_dashboard(request):
    appointments = Appointment.objects.all()
    patients = Patient.objects.all()
    if request.method == "POST":
        appt_id = request.POST.get("appt_id")
        status = request.POST.get("status")
        appt = Appointment.objects.get(id=appt_id)
        appt.status = status
        appt.save()
    return render(request, "hospital/admin_dashboard.html", {"appointments": appointments, "patients": patients})

def initiate_payment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)

    if request.method == "POST":
        phone = request.POST.get("phone")
        amount = request.POST.get("amount")

        response = stk_push(
            phone_number=phone,
            amount=amount,
            account_reference=f"APT-{appointment.id}",
            transaction_desc="Appointment Payment"
        )

        return JsonResponse(response)

    return JsonResponse({"error": "Invalid request"}, status=400)

@csrf_exempt
def mpesa_callback(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body.decode('utf-8'))
            callback = data["Body"]["stkCallback"]

            result_code = callback["ResultCode"]
            checkout_request_id = callback["CheckoutRequestID"]

            # If transaction failed, return success to Safaricom
            if result_code != 0:
                return JsonResponse({"ResultCode": 0, "ResultDesc": "Accepted"})

            # Transaction successful
            metadata_items = callback["CallbackMetadata"]["Item"]

            amount = next(item["Value"] for item in metadata_items if item["Name"] == "Amount")
            receipt_number = next(item["Value"] for item in metadata_items if item["Name"] == "MpesaReceiptNumber")
            phone = next(item["Value"] for item in metadata_items if item["Name"] == "PhoneNumber")
            account_reference = next(item["Value"] for item in metadata_items if item["Name"] == "AccountReference")

            # Extract appointment ID from AccountReference "APT-12"
            appointment_id = int(str(account_reference).split("-")[-1])
            appointment = Appointment.objects.get(id=appointment_id)

            # Save Payment
            Payment.objects.create(
                appointment=appointment,
                phone=phone,
                amount=amount,
                mpesa_receipt=receipt_number
            )

            # Mark appointment as Paid
            appointment.payment_status = "Paid"
            appointment.save()

            return JsonResponse({"ResultCode": 0, "ResultDesc": "Success"})

        except Exception as e:
            print("Callback error:", e)
            return JsonResponse({"ResultCode": 1, "ResultDesc": "Error"})

    return JsonResponse({"ResultCode": 1, "ResultDesc": "Invalid Method"})

def generate_meet_link():
    # Generates a random Google Meet style link
    return f"https://meet.google.com/{uuid.uuid4().hex[:3]}-{uuid.uuid4().hex[:4]}-{uuid.uuid4().hex[:3]}"


def accept_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)

    if request.method == "POST":
        form = MeetingLinkForm(request.POST, instance=appointment)
        if form.is_valid():
            appointment.status = "Accepted"
            form.save()  # saves meet_link field
            return redirect("admin_dashboard")

    else:
        # Auto-generate Google Meet link if blank
        if not appointment.meet_link:
            appointment.meet_link = generate_meet_link()
            appointment.save()

        form = MeetingLinkForm(instance=appointment)

    return render(request, "hospital/add_meeting_link.html", {
        "form": form,
        "appointment": appointment
    })
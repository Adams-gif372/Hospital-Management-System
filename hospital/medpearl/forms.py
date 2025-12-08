from django import forms
from django.contrib.auth.models import User
from .models import Appointment

class PatientRegisterForm(forms.ModelForm):
    address = forms.CharField(max_length=255)
    contact = forms.CharField(max_length=20)
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ["username", "email", "password", "address", "contact"]

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user

class AppointmentForm(forms.ModelForm):
     date = forms.DateTimeField(
        widget=forms.DateTimeInput(
            attrs={'class': 'form-control', 'type': 'datetime-local'}
        ),
        input_formats=['%Y-%m-%dT%H:%M'],
        label="Appointment Date and Time"
    )

     class Meta:
        model = Appointment
        fields = ["doctor", "date", "symptoms"]
        widgets = {
            'doctor': forms.Select(attrs={'class': 'form-control'}),
            'symptoms': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class MeetingLinkForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['meet_link']
        widgets = {
            'meet_link': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://meet.google.com/your-meet-code'
            })
        }
from django import forms
from django.utils import timezone

from .models import (
    TrialBooking,
    DandiyaRegistration,
)


# =========================================================
# TRIAL BOOKING FORM
# =========================================================

class TrialBookingForm(forms.ModelForm):

    class Meta:
        model = TrialBooking

        fields = [
            "name",
            "phone",
            "email",
            "dance_class",
            "preferred_date",
            "message",
        ]

        widgets = {
            "name": forms.TextInput(
                attrs={
                    "placeholder": "Your Name",
                    "class": "form-control",
                }
            ),

            "phone": forms.TextInput(
                attrs={
                    "placeholder": "Phone Number",
                    "class": "form-control",
                    "inputmode": "numeric",
                    "maxlength": "10",
                }
            ),

            "email": forms.EmailInput(
                attrs={
                    "placeholder": "Email Address",
                    "class": "form-control",
                }
            ),

            "dance_class": forms.Select(
                attrs={
                    "class": "form-control",
                }
            ),

            "preferred_date": forms.DateInput(
                attrs={
                    "type": "date",
                    "class": "form-control",
                }
            ),

            "message": forms.Textarea(
                attrs={
                    "placeholder": "Anything you would like us to know?",
                    "rows": 4,
                    "class": "form-control",
                }
            ),
        }

    def clean_phone(self):
        phone = self.cleaned_data.get("phone", "").strip()

        if not phone.isdigit():
            raise forms.ValidationError(
                "Please enter a valid phone number."
            )

        if len(phone) != 10:
            raise forms.ValidationError(
                "Phone number must contain exactly 10 digits."
            )

        return phone

    def clean_preferred_date(self):
        preferred_date = self.cleaned_data.get(
            "preferred_date"
        )

        if (
            preferred_date is not None
            and preferred_date < timezone.localdate()
        ):
            raise forms.ValidationError(
                "Please choose today or a future date."
            )

        return preferred_date


# =========================================================
# DANDIYA REGISTRATION FORM
# =========================================================

class DandiyaRegistrationForm(forms.ModelForm):

    class Meta:
        model = DandiyaRegistration

        fields = [
            "dandiya_pass",
            "name",
            "phone",
            "email",
            "age",
            "number_of_participants",
            "message",
        ]

        widgets = {

            "dandiya_pass": forms.Select(
                attrs={
                    "class": "form-control",
                }
            ),

            "name": forms.TextInput(
                attrs={
                    "placeholder": "Your Name",
                    "class": "form-control",
                }
            ),

            "phone": forms.TextInput(
                attrs={
                    "placeholder": "Phone Number",
                    "class": "form-control",
                    "inputmode": "numeric",
                    "maxlength": "10",
                }
            ),

            "email": forms.EmailInput(
                attrs={
                    "placeholder": "Email Address",
                    "class": "form-control",
                }
            ),

            "age": forms.NumberInput(
                attrs={
                    "placeholder": "Age",
                    "class": "form-control",
                    "min": 1,
                }
            ),

            "number_of_participants": forms.NumberInput(
                attrs={
                    "placeholder": "Number of Participants",
                    "class": "form-control",
                    "min": 1,
                    "max": 100,
                }
            ),

            "message": forms.Textarea(
                attrs={
                    "placeholder": "Any special request or message?",
                    "rows": 4,
                    "class": "form-control",
                }
            ),
        }

    def __init__(self, *args, event=None, **kwargs):
        super().__init__(*args, **kwargs)

        if event is not None:
            self.fields["dandiya_pass"].queryset = (
                event.passes.filter(is_active=True)
            )
        else:
            self.fields["dandiya_pass"].queryset = (
                self.fields["dandiya_pass"]
                .queryset
                .filter(is_active=True)
            )

    def clean_phone(self):
        phone = self.cleaned_data.get("phone", "").strip()

        if not phone.isdigit():
            raise forms.ValidationError(
                "Please enter a valid phone number."
            )

        if len(phone) != 10:
            raise forms.ValidationError(
                "Phone number must contain exactly 10 digits."
            )

        return phone

    def clean_age(self):
        age = self.cleaned_data.get("age")

        if age is not None and (age < 3 or age > 100):
            raise forms.ValidationError(
                "Please enter a valid age between 3 and 100."
            )

        return age

    def clean_number_of_participants(self):
        number = self.cleaned_data.get(
            "number_of_participants"
        )

        if number < 1 or number > 100:
            raise forms.ValidationError(
                "Participants must be between 1 and 100."
            )

        return number


# =========================================================
# DANDIYA CHECK-IN FORM
# =========================================================

class DandiyaCheckInForm(forms.Form):

    entry_code = forms.CharField(
        max_length=50,
        label="Entry Code",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Enter Entry Code",
                "autocomplete": "off",
                "autocapitalize": "characters",
            }
        ),
    )

    def clean_entry_code(self):
        entry_code = self.cleaned_data.get(
            "entry_code",
            "",
        ).strip().upper()

        if not entry_code:
            raise forms.ValidationError(
                "Please enter an entry code."
            )

        return entry_code
from django import forms

class OTPLoginForm(forms.Form):
    phone = forms.CharField(max_length=15, label="Phone Number")
    otp = forms.CharField(max_length=6, label="OTP", required=False)

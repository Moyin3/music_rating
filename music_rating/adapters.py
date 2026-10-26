from allauth.account.adapter import DefaultAccountAdapter
from allauth.core.internal.httpkit import render_url
from django.conf import settings

class MyAccountAdapter(DefaultAccountAdapter):
    def get_email_confirmation_url(self, request, emailconfirmation):
        return render_url(request, settings.ACCOUNT_EMAIL_CONFIRMATION_URL, key = emailconfirmation.key)
    def clean_email(self, email):
        email = super().clean_email(email)
        return email.lower()
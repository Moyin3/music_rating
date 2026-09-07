from allauth.account.adapter import DefaultAccountAdapter
from allauth.core.internal.httpkit import render_url

class MyAccountAdapter(DefaultAccountAdapter):
    def get_email_confirmation_url(self, request, emailconfirmation):
        return render_url(request, "http://127.0.0.1:5173/verify-email/{key}", key = emailconfirmation.key)
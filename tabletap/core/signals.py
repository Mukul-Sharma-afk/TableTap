from allauth.account.signals import user_signed_up
from django.dispatch import receiver
from django.shortcuts import redirect

@receiver(user_signed_up)
def complete_registration(sender, request, user, **kwargs):
    # If user came from Google then redirect them to registration step page
    request.session['social_signup'] = True

@receiver(user_signed_up)
def handle_social_signup(sender, request, user, **kwargs):
    request.session['social_signup'] = True


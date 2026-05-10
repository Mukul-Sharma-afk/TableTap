from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.shortcuts import redirect

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def get_login_redirect_url(self, request):
        user = request.user
        if not user.first_name or not BusinessStaff.objects.filter(user=user).exists():
            return '/tabletap/complete-registration/'
        return '/tabletap/dashboard/'

# api/services.py
from django.conf import settings
from django.core.exceptions import ValidationError
from urllib.parse import urlencode
import requests
from django.shortcuts import redirect

GOOGLE_ACCESS_TOKEN_OBTAIN_URL = 'https://oauth2.googleapis.com/token'
GOOGLE_USER_INFO_URL = 'https://www.googleapis.com/oauth2/v3/userinfo'

def google_get_access_token(code: str, redirect_uri: str) -> str:
    data = {
        'code': code,
        'client_id': settings.GOOGLE_OAUTH2_CLIENT_ID,
        'client_secret': settings.GOOGLE_OAUTH2_CLIENT_SECRET,
        'redirect_uri': redirect_uri,
        'grant_type': 'authorization_code'
    }

    response = requests.post(GOOGLE_ACCESS_TOKEN_OBTAIN_URL, data=data)
    if not response.ok:
        raise ValidationError('Could not get access token from Google.')
    
    access_token = response.json()['access_token']
    return access_token

def google_get_user_info(access_token: str):
    response = requests.get(GOOGLE_USER_INFO_URL, params={'access_token': access_token})
    if not response.ok:
        raise ValidationError('Could not get user info from Google.')
    
    return response.json()

def get_user_data(validated_data):
    redirect_uri = f"{settings.BASE_API_URL}/api/auth/login/google/"
    code = validated_data.get('code')
    error = validated_data.get('error')

    if error or not code:
        params = urlencode({'error': error})
        return redirect(f'{settings.BASE_APP_URL}/login?{params}')
    
    access_token = google_get_access_token(code=code, redirect_uri=redirect_uri)
    user_data = google_get_user_info(access_token=access_token)

    return {
        'email': user_data['email'],
        'first_name': user_data.get('given_name'),
        'last_name': user_data.get('family_name'),
    }

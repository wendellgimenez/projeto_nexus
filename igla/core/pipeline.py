from django.contrib.auth.models import User
from django.shortcuts import redirect
from django.contrib import messages
from social_core.pipeline.partial import partial
from social_django.utils import load_strategy

@partial
def check_existing_email(backend, details, response, user=None, *args, **kwargs):
    request = kwargs.get('request')
    if user:
        return {'user': user}

    email = details.get('email')
    if email:
        try:
            existing_user = User.objects.get(email=email)
            return {'user': existing_user}
        except User.DoesNotExist:
            # Limpar sessão do OAuth2 para permitir nova tentativa de login
            load_strategy(request).session.flush()

            messages.error(request, 'Este email não está cadastrado no sistema. Por favor, solicite ao administrador para cadastrar seu email.')
            return redirect('login')

    messages.error(request, 'Não foi possível autenticar com este email.')
    load_strategy(request).session.flush()  # Limpar sessão também aqui
    return redirect('login')
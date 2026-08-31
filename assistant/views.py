import json
from datetime import datetime
import os

from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET, require_POST


SESSION_HISTORY_LIMIT = 20


def _get_provider_settings():
    return {
        'provider': os.getenv('AGROSSEDAM_AI_PROVIDER', 'mock').strip().lower(),
        'api_key': os.getenv('AGROSSEDAM_AI_API_KEY', ''),
        'model': os.getenv('AGROSSEDAM_AI_MODEL', 'default'),
    }


def _build_response(message):
    text = (message or '').strip()
    if not text:
        return 'Je peux vous aider sur l’agriculture, l’élevage, les cultures, les saisons, les récoltes, les couveuses et l’utilisation de AgroSedam.'
    return text


def _generate_assistant_reply(user_message, history):
    provider_settings = _get_provider_settings()
    cleaned = (user_message or '').strip().lower()

    if provider_settings['provider'] in {'openai', 'gemini', 'ollama', 'mistral', 'deepseek'} and provider_settings['api_key']:
        return _build_response(
            "Connexion au fournisseur IA configuré prête. Le modèle utilisé est " + provider_settings['model'] + "."
        )

    if any(word in cleaned for word in ['culture', 'cultures', 'semence', 'engrais', 'recolte', 'saison']):
        return _build_response(
            "Pour une culture, commencez par créer une saison, ajoutez ensuite une parcelle puis enregistrez la culture depuis le tableau de bord."
        )

    if any(word in cleaned for word in ['animal', 'animaux', 'maladie', 'vaccin', 'vaccins', 'alimentation', 'élevage', 'elevage']):
        return _build_response(
            "Pour l’élevage, vous pouvez enregistrer les animaux, suivre leur état de santé, planifier les vaccins et noter les traitements."
        )

    if any(word in cleaned for word in ['volaille', 'volailles', 'oeuf', 'œuf', 'oeufs', 'œufs']):
        return _build_response(
            "Pour la filière volailles, vous pouvez suivre les entrées, sorties, mortalités et la production d’œufs dans la rubrique Aviculture."
        )

    if any(word in cleaned for word in ['couveuse', 'couveuses', 'incubation']):
        return _build_response(
            "Pour une couveuse, créez un enregistrement avec la capacité, la température, l’humidité et les œufs à incubés, puis suivez l’évolution jusqu’à l’éclosion."
        )

    if any(word in cleaned for word in ['parcelle', 'parcelles', 'saison', 'créer', 'ajouter']):
        return _build_response(
            "Vous pouvez ajouter une saison, une parcelle, puis une culture depuis les menus dédiés. Le tableau de bord centralise ensuite les principales informations."
        )

    if any(word in cleaned for word in ['tableau de bord', 'dashboard', 'utilisation', 'aide', 'comment']):
        return _build_response(
            "Je peux vous guider pas à pas : ajouter une culture, enregistrer un animal, créer une saison, gérer une couveuse, consulter le tableau de bord ou réinitialiser votre mot de passe."
        )

    if any(word in cleaned for word in ['meteo', 'météo', 'weather']):
        return _build_response(
            "Si vous configurez une clé API météo, je pourrai vous fournir des prévisions adaptées à votre zone agricole."
        )

    if any(word in cleaned for word in ['agrosedam', 'application', 'profil', 'mot de passe', 'utilisateur', 'compte']):
        return _build_response(
            "AgroSedam est votre plateforme de gestion agropastorale. Vous pouvez gérer les cultures, les parcelles, les animaux, les volailles, les couveuses et consulter votre tableau de bord depuis une interface moderne."
        )

    if any(word in cleaned for word in ['bonjour', 'salut', 'bonsoir', 'hello', 'hi']):
        return _build_response(
            "Bonjour ! Je suis AgroSedam AI, votre assistante dédiée à la gestion agricole et d’élevage. Comment puis-je vous aider aujourd’hui ?"
        )

    return _build_response(
        "Je peux vous aider sur l’agriculture, l’élevage, les cultures, les saisons, les récoltes, les couveuses et l’utilisation d’AgroSedam. Posez-moi une question précise et je vous répondrai clairement."
    )


@require_GET
def assistant_home(request):
    return render(request, 'assistant/home.html')


@require_GET
def assistant_chat(request):
    return render(request, 'assistant/chat.html')


@require_POST
def assistant_api(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentification requise.'}, status=401)

    payload = json.loads(request.body.decode('utf-8') or '{}')
    message = (payload.get('message') or '').strip()
    if not message:
        return JsonResponse({'error': 'Message vide.'}, status=400)

    history = payload.get('history') or []
    if isinstance(history, list):
        history = history[-SESSION_HISTORY_LIMIT:]
    else:
        history = []

    reply = _generate_assistant_reply(message, history)
    current_time = datetime.now().strftime('%H:%M')
    return JsonResponse({
        'reply': reply,
        'timestamp': current_time,
        'provider': _get_provider_settings()['provider'],
    })


@require_GET
def assistant_history(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentification requise.'}, status=401)
    return JsonResponse({'history': []})

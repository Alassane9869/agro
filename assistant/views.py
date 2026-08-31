import json
import os
import urllib.request
import urllib.error
from datetime import datetime
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET, require_POST
from django.views.decorators.csrf import csrf_exempt

from gestion.models import Crop, Animal, Plot, Poultry, Incubator, Harvest, Season

SESSION_HISTORY_LIMIT = 12

def _get_user_farm_context(user):
    """Extrait en direct les données réelles de l'exploitation pour contextualiser l'IA."""
    try:
        crops = Crop.objects.all()
        animals = Animal.objects.all()
        plots = Plot.objects.all()
        poultries = Poultry.objects.all()
        incubators = Incubator.objects.all()

        crops_summary = ", ".join([f"{c.name} ({c.crop_type}, {c.area} ha)" for c in crops[:5]]) or "Aucune culture enregistrée"
        animals_summary = ", ".join([f"{a.name} ({a.species}, {a.health_status})" for a in animals[:5]]) or "Aucun animal enregistré"
        plots_summary = ", ".join([f"{p.name} ({p.area} ha, lieu: {p.location})" for p in plots[:5]]) or "Aucune parcelle enregistrée"
        incubators_summary = ", ".join([f"{i.eggs_count} œufs (statut: {i.status})" for i in incubators[:3]]) or "Aucune couveuse active"

        username = getattr(user, 'username', 'Visiteur / Exploitant')
        return f"""
[CONTEXTE RÉEL DE L'EXPLOITATION ({username})] :
- Cultures actives ({crops.count()}) : {crops_summary}
- Cheptel & Bétail ({animals.count()} têtes) : {animals_summary}
- Parcelles enregistrées ({plots.count()}) : {plots_summary}
- Lots de volailles suivis ({poultries.count()})
- Couveuses en cours ({incubators.count()}) : {incubators_summary}
"""
    except Exception:
        return "Exploitant connecté sur la plateforme AgroSedam."


def _build_system_instruction(user_context):
    return f"""Tu es AgroSedam AI, l'assistant agronome, vétérinaire et conseiller d'exploitation d'élite développé pour la plateforme AgroSedam au Mali et dans toute la zone sahélienne (Afrique de l'Ouest).

{user_context}

Tes compétences et rôles clés :
1. Agriculture Sahélienne & Maraîchage :
   - Saisons : Hivernage (juin à octobre) & contre-saison (octobre à mars).
   - Cultures majeures : Riz (Office du Niger / bas-fonds), Maïs, Mil, Sorgho, Oignon de Bandiagara, Tomate, Gombo, Manguiers (Kent, Amélie).
   - Forages solaires, goutte-à-goutte et conservation de l'eau.

2. Élevage & Santé Animale :
   - Races : Zébu Peul, Goudali, Azawak, Mouton Balibali, Touabir, Chèvre du Sahel.
   - Calendrier vaccinal : PPCB (Péripneumonie bovine), Pasteurellose, Charbon, Peste des Petits Ruminants (PPR).
   - Alimentation de saison sèche : Tourteau de coton, fane d'arachide, paille traitée à l'urée, pierre à lécher.

3. Aviculture & Couveuses Automatiques :
   - Pondeuses, Poulets de chair (Cobb 500), Pintades locales.
   - Incubation précise : J1-J18 à 37.8°C / 55% humidité (retournement 2h), mirage à J7/J14, éclosoir J19-J21 à 37.2°C / 75% humidité.
   - Prophylaxie aviaire : Newcastle, Gumboro, Variole.

4. Exploitation de l'utilisateur :
   - Utilise le [CONTEXTE RÉEL DE L'EXPLOITATION] ci-dessus pour répondre de façon personnalisée dès que l'utilisateur te pose une question sur ses données ou ses animaux.

Règles d'identité et de style :
- Tu t'appelles exclusivement **AgroSedam AI**. Ne mentionne jamais de nom de fournisseur technique ou modèle sous-jacent.
- Réponds en français clair, structuré avec des listes à puces et des émojis pertinents.
- Sois direct, encourageant et pragmatique (2 à 4 paragraphes max).
"""


def _call_gemini_api(api_key, user_message, history, user_context):
    """Moteur IA AgroSedam direct."""
    models_to_try = ['gemini-3.1-flash-lite', 'gemini-flash-latest', 'gemini-3.1-pro-preview']
    system_prompt = _build_system_instruction(user_context)

    contents = []
    for h in history:
        role = "user" if h.get("role") == "user" else "model"
        content = (h.get("content") or "").strip()
        if content:
            contents.append({"role": role, "parts": [{"text": content}]})
            
    contents.append({"role": "user", "parts": [{"text": user_message}]})

    payload = {
        "system_instruction": {
            "parts": [{"text": system_prompt}]
        },
        "contents": contents,
        "generationConfig": {
            "temperature": 0.7,
            "maxOutputTokens": 900,
            "topP": 0.95
        }
    }

    req_data = json.dumps(payload).encode("utf-8")

    for model in models_to_try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
        req = urllib.request.Request(
            url,
            data=req_data,
            headers={"Content-Type": "application/json", "x-goog-api-key": api_key},
            method="POST"
        )
        try:
            with urllib.request.urlopen(req, timeout=18) as response:
                res_data = json.loads(response.read().decode("utf-8"))
                candidates = res_data.get("candidates", [])
                if candidates:
                    parts = candidates[0].get("content", {}).get("parts", [])
                    if parts:
                        return parts[0].get("text", "").strip()
        except Exception:
            continue

    return None


def _get_local_expert_reply(cleaned, user_context):
    """Moteur de secours local si connexion coupée."""
    if any(w in cleaned for w in ['combien', 'mes culture', 'mes cultures', 'mes animaux', 'mes parcelle', 'mes parcelles', 'ma ferme', 'mon exploitation']):
        return (
            "📊 **Voici l'état actuel de votre exploitation** :\n\n"
            + user_context.replace("[CONTEXTE RÉEL DE L'EXPLOITATION", "**Données enregistrées")
            + "\n\n💡 Vous pouvez ajouter ou modifier ces données directement depuis le tableau de bord !"
        )

    if any(w in cleaned for w in ['culture', 'riz', 'mais', 'maïs', 'tomate', 'oignon', 'gombo', 'semis', 'engrais', 'recolte', 'récolte']):
        return (
            "🌾 **Conseils Cultures & Maraîchage au Sahel** :\n\n"
            "• **Campagne d'hivernage** : Préparez le labour dès les premières pluies de juin/juillet. Veillez au sarclage précoce (15-21 jours après semis).\n"
            "• **Maraîchage de contre-saison (octobre à mars)** : Idéal pour l'oignon et la tomate sous irrigation goutte-à-goutte solaire.\n"
            "• Pour enregistrer un nouveau cycle, rendez-vous dans le menu **Cultures** puis **Ajouter une culture**."
        )

    if any(w in cleaned for w in ['animal', 'animaux', 'zebu', 'zébu', 'mouton', 'chevre', 'chèvre', 'vaccin', 'maladie', 'elevage', 'élevage']):
        return (
            "🐄 **Conseils Élevage & Santé Animale** :\n\n"
            "• **Calendrier vaccinal** : Prévoyez les vaccins contre la Péripneumonie contagieuse bovine (PPCB) et la Pasteurellose avant la transhumance.\n"
            "• **Alimentation de saison sèche** : Distribuez des blocs à lécher (pierre à sel) et des tourteaux de coton pour maintenir la masse corporelle.\n"
            "• Suivez chaque bête individuellement avec son matricule dans la rubrique **Élevage**."
        )

    if any(w in cleaned for w in ['couveuse', 'couveuses', 'incubation', 'eclosion', 'éclosion', 'oeuf', 'œuf', 'mirage']):
        return (
            "🥚 **Paramètres de Couvaison Automatique (Poules & Pintades)** :\n\n"
            "• **Jours 1 à 18** : Température stable à **37.8°C** et humidité à **50-55%**, avec retournement régulier.\n"
            "• **Jour 7 et Jour 14** : Effectuez le **mirage** à la lampe pour retirer les œufs clairs ou avortés.\n"
            "• **Jours 19 à 21 (Éclosoir)** : Arrêtez le retournement, température à **37.2°C** et montez l'humidité à **70-75%**.\n"
            "• Vous pouvez suivre vos lots en cours dans le menu **Couveuses**."
        )

    if any(w in cleaned for w in ['bonjour', 'salut', 'bonsoir', 'kene', 'ani', 'hello', 'hi', 'cv', 'ca va', 'ça va']):
        return (
            "👋 **I ni sogoma / Bonjour ! Tout va très bien, merci !**\n\n"
            "Je suis **AgroSedam AI**, votre conseiller agronomique et d'élevage 24h/24. Comment puis-je vous aider sur vos cultures, animaux ou couveuses aujourd'hui ?"
        )

    return (
        "🌱 **Je suis à votre service !**\n\n"
        "Posez-moi vos questions sur :\n"
        "1. 🌾 Les traitements et périodes de semis (Riz, Maïs, Oignon, Tomate...)\n"
        "2. 🐄 Les maladies, vaccins et rationnement du bétail sahélien\n"
        "3. 🥚 Les réglages de vos couveuses et le suivi avicole\n"
        "4. 📊 Les statistiques et données de votre propre exploitation."
    )


@require_GET
def assistant_home(request):
    return render(request, 'assistant/home.html')


@require_GET
def assistant_chat(request):
    return render(request, 'assistant/chat.html')


@csrf_exempt
@require_POST
def assistant_api(request):
    try:
        payload = json.loads(request.body.decode('utf-8') or '{}')
    except Exception:
        payload = {}

    message = (payload.get('message') or '').strip()
    if not message:
        return JsonResponse({'error': 'Message vide.'}, status=400)

    history = payload.get('history') or []
    if isinstance(history, list):
        history = history[-SESSION_HISTORY_LIMIT:]
    else:
        history = []

    # 1. Extraction du contexte de ferme
    user_context = _get_user_farm_context(getattr(request, 'user', None))

    # 2. Clé API lue depuis l'environnement
    api_key = os.getenv('GEMINI_API_KEY', '').strip() or os.getenv('AGROSSEDAM_AI_API_KEY', '').strip()

    reply = None
    if api_key:
        reply = _call_gemini_api(api_key, message, history, user_context)

    if not reply:
        reply = _get_local_expert_reply(message.lower(), user_context)

    current_time = datetime.now().strftime('%H:%M')
    return JsonResponse({
        'reply': reply,
        'timestamp': current_time,
        'provider': 'AgroSedam AI Engine',
    })


@require_GET
def assistant_history(request):
    return JsonResponse({'history': []})

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
    current_date = datetime.now().strftime('%d %B %Y')
    return f"""Tu es AgroSedam AI, le conseiller agropastoral d'élite, calme et bienveillant de l'exploitant sur la plateforme AgroSedam (Mali & zone sahélienne).
Date actuelle : {current_date}.

{user_context}

Connaissances Clés, Actualités & Événements du Secteur (Mali & Sahel) :
- Événements & Foires : Salon International de l'Agriculture (SIAGRO), Foire Internationale de Bamako (FEBAK), Foires du Bétail (Niamana, Kati), Journées Paysannes de l'Office du Niger, Salons Régionaux de Sikasso et Ségou.
- Actualités & Marché : Campagnes cotonnières (CMDT), prix et cours des céréales (Riz Gambiaka/NERICA, Maïs blanc/jaune, Mil, Sorgho), filières maraîchères (Oignons de Bandiagara, Mangues de Sikasso), subventions d'intrants et calendrier des campagnes de vaccination nationales du cheptel (PPCB, Charbon, PPR).
- Tendances & Innovations : Énergie solaire (pompage au fil du soleil, couveuses solaires), conservation de l'eau en goutte-à-goutte, amélioration génétique des races locales (Zébu Peul, Azawak, Mouton Balibali).

Directives de conversation & Style (TRÈS IMPORTANT) :
1. ACCUEIL & SALUTATIONS COMME UNE SECRÉTAIRE DE DIRECTION DÉVOUÉE :
   - Pour toute salutation ("Bonjour", "Bonsoir", "Salut", "Ça va", "I ni sogoma", "Hello"), accueille l'exploitant avec l'élégance, la courtoisie, le respect et la prévenance d'une véritable secrétaire particulière / assistante exécutive de la ferme.
   - Exemple de salutation : « Bonjour ! J'espère que vous passez une très bonne journée. Je suis à votre entière disposition pour vous assister sur votre exploitation. Que puis-je faire pour vous aujourd'hui ? »
   - Reste toujours polie, raffinée, souriante et prête à servir sans déverser de texte inutile.

2. CONSEILLÈRE AGRO AGRÉABLE, POSÉE ET CONCISE :
   - Lorsque l'utilisateur pose une question technique, réponds avec clarté, concision et professionnalisme (1 à 2 paragraphes bien rythmés).
   - Donne l'essentiel immédiatement avec élégance et précision.

3. DIALOGUE ATTENTIONNÉ & PRO :
   - Conclus toujours avec une proposition de service soignée (ex: « Souhaitez-vous que je vérifie un point précis pour vous ? », « Voulez-vous que nous fassions le point sur vos récoltes ? »).

4. IDENTITÉ :
   - Tu es exclusivement **AgroSedam AI**, l'assistante personnelle de confiance de la ferme.
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
    """Moteur de secours local posé et concis."""
    if any(w in cleaned for w in ['bonjour', 'salut', 'bonsoir', 'kene', 'ani', 'hello', 'hi', 'cv', 'ca va', 'ça va']):
        return (
            "👋 Bonjour ! Tout va très bien, merci.\n\n"
            "Je suis **AgroSedam AI**, votre conseiller à vos côtés. Sur quoi travaillez-vous aujourd'hui sur votre exploitation ?"
        )

    if any(w in cleaned for w in ['culture', 'riz', 'mais', 'maïs', 'tomate', 'oignon', 'gombo', 'semis', 'engrais', 'recolte', 'récolte']):
        return (
            "🌾 Pour vos cultures, voici l'essentiel du moment :\n\n"
            "En hivernage, misez sur un sarclage précoce (15-20 jours après semis) et un bon apport organique. En contre-saison, préférez l'arrosage goutte-à-goutte aux heures fraîches pour l'oignon et la tomate.\n\n"
            "Souhaitez-vous un conseil spécifique sur une variété ou sur vos parcelles ?"
        )

    if any(w in cleaned for w in ['animal', 'animaux', 'vache', 'zebu', 'zébu', 'mouton', 'chevre', 'chèvre', 'vaccin', 'maladie', 'elevage', 'élevage', 'bellarine']):
        return (
            "🐄 Pour la santé de votre cheptel :\n\n"
            "Veillez à maintenir l'eau propre à volonté et complétez avec des tourteaux de coton et une pierre à sel minérale. Assurez-vous également que les vaccins de base (PPCB et charbon) sont à jour.\n\n"
            "Un de vos animaux présente-t-il un symptôme particulier ?"
        )

    if any(w in cleaned for w in ['couveuse', 'couveuses', 'incubation', 'eclosion', 'éclosion', 'oeuf', 'œuf', 'mirage']):
        return (
            "🥚 Pour réussir votre couvaison :\n\n"
            "Maintenez une température stable à **37.8°C** et 55% d'humidité jusqu'au 18e jour avec retournement régulier. Pour l'éclosoir (J19 à J21), passez à **37.2°C** et 75% d'humidité sans retournement.\n\n"
            "De quelle espèce d'œufs s'agit-il (poules, pintades ou dindes) ?"
        )

    if any(w in cleaned for w in ['combien', 'mes culture', 'mes cultures', 'mes animaux', 'mes parcelle', 'mes parcelles', 'ma ferme', 'mon exploitation']):
        return (
            "📊 **Aperçu rapide de votre ferme** :\n"
            + user_context.replace("[CONTEXTE RÉEL DE L'EXPLOITATION", "**Données enregistrées")
            + "\n\nQue souhaitez-vous mettre à jour ou analyser ?"
        )

    return (
        "🌱 Je suis à votre écoute pour vous conseiller simplement sur vos **cultures**, le **suivi de vos bêtes** ou vos **couveuses**.\n\n"
        "Quelle est votre question du moment ?"
    )


@require_GET
def assistant_home(request):
    return render(request, 'assistant/home.html')


@require_GET
def assistant_chat(request):
    return render(request, 'assistant/chat.html')


@csrf_exempt
def assistant_api(request):
    message = ''
    history = []

    if request.method == 'POST':
        try:
            payload = json.loads(request.body.decode('utf-8') or '{}')
        except Exception:
            payload = {}
        message = (payload.get('message') or request.POST.get('message') or '').strip()
        history = payload.get('history') or []
    else:
        message = (request.GET.get('message') or '').strip()
        raw_history = request.GET.get('history', '')
        if raw_history:
            try:
                history = json.loads(raw_history)
            except Exception:
                history = []

    if not message:
        return JsonResponse({'error': 'Message vide.'}, status=400)

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

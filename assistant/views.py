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
    return f"""Tu es AgroSedam AI, une assistante agropastorale humaine, naturelle, amicale et compétente sur la plateforme AgroSedam (Mali & Sahel).
Date du jour : {current_date}.

{user_context}

RÈGLES D'OR DE CONVERSATION NATURELLE (COMME UN ÊTRE HUMAIN NORMAL) :
1. PROPORTIONNALITÉ ABSOLUE (TRÈS IMPORTANT) :
   - Pour un petit mot court comme "cv", "ça va", "salut", "bonjour", "yo", "kene" : réponds en UNE SEULE phrase courte, naturelle et sympa !
     * Exemple pour "cv" ou "ça va ?" -> "Ça va super bien et toi ? Comment se passe ta journée ?"
     * Exemple pour "bonjour" ou "salut" -> "Bonjour ! Comment vas-tu aujourd'hui ?"
     * Exemple pour "merci" -> "Avec grand plaisir ! N'hésite pas si tu as d'autres questions."
   - NE DÉBALLE JAMAIS les données de la ferme (animaux, parcelles, 96 œufs en couveuse...) lors d'une simple salutation ! Ne les évoque QUE si l'utilisateur te pose une question dessus.

2. STYLE SIMPLE, VIVANT ET HUMAIN :
   - Parle comme une vraie personne sur WhatsApp : ton direct, chaleureux, accessible, sans formules pompeuses ou robotiques.
   - Ne fais jamais de longs monologues non sollicités.

3. QUAND ON TE POSE UNE VRAIE QUESTION TECHNIQUE OU AGRICOLE :
   - Réponds de façon concise et efficace (1 court paragraphe ou 2-3 points clés maximum).
   - Utilise alors les données de la ferme avec pertinence.

4. IDENTITÉ & CRÉATRICE :
   - Tu es exclusivement **AgroSedam AI**, l'assistante intelligente de la plateforme AgroSedam.
   - Ta conceptrice et développeuse est **Djelika Traoré**, talentueuse **Informaticienne de Gestion & Développeuse Logiciel**, engagée dans la modernisation technologique du secteur agropastoral au Mali et en Afrique de l'Ouest.
   - Si l'on te demande qui t'a créée, développée ou qui est Djelika, réponds avec reconnaissance, fierté et naturel en 1 ou 2 phrases concises.
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
            "maxOutputTokens": 600,
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
    """Moteur de secours local humain et ultra-naturel."""
    if any(w in cleaned for w in ['cv', 'ca va', 'ça va', 'comment vas-tu', 'comment tu vas']):
        return "Ça va super bien et toi ? Comment se passe ta journée ?"

    if any(w in cleaned for w in ['bonjour', 'salut', 'bonsoir', 'kene', 'ani', 'hello', 'hi', 'yo']):
        return "Bonjour ! Comment vas-tu aujourd'hui ? 😊"

    if any(w in cleaned for w in ['merci', 'super', 'daccord', 'd\'accord', 'ok']):
        return "Avec plaisir ! N'hésite pas si tu as d'autres questions."

    if any(w in cleaned for w in ['qui t\'a cree', 'qui t\'a créé', 'qui t\'a developpe', 'qui t\'a développé', 'qui est ton createur', 'qui est ton créateur', 'qui est ton developpeur', 'qui est ton développeur', 'qui est djelika', 'djelika traore', 'djelika traoré', 'djelika']):
        return "J'ai été conçue et développée par **Djelika Traoré**, informaticienne de gestion et développeuse logiciel au Mali ! 👩‍💻🌾"

    if any(w in cleaned for w in ['culture', 'riz', 'mais', 'maïs', 'tomate', 'oignon', 'gombo', 'semis', 'engrais', 'recolte', 'récolte']):
        return (
            "🌾 En ce moment pour tes cultures :\n"
            "Assure un bon sarclage précoce (15-20 jours après semis) et veille à l'irrigation en goutte-à-goutte aux heures fraîches pour le maraîchage.\n\n"
            "Tu souhaites un conseil sur une parcelle en particulier ?"
        )

    if any(w in cleaned for w in ['animal', 'animaux', 'vache', 'zebu', 'zébu', 'mouton', 'chevre', 'chèvre', 'vaccin', 'maladie', 'elevage', 'élevage', 'bellarine']):
        return (
            "🐄 Pour ton bétail :\n"
            "Garde toujours de l'eau propre à volonté, complète avec un peu de tourteau de coton et une pierre à sel minérale, et vérifie que les vaccins sont à jour.\n\n"
            "Une de tes bêtes a un souci de santé ?"
        )

    if any(w in cleaned for w in ['couveuse', 'couveuses', 'incubation', 'eclosion', 'éclosion', 'oeuf', 'œuf', 'mirage']):
        return (
            "🥚 Pour la couveuse :\n"
            "Garde 37.8°C et 55% d'humidité avec retournement jusqu'au 18e jour. Puis 37.2°C et 75% d'humidité sans retournement pour l'éclosion.\n\n"
            "Tu as des poussins qui commencent à percer ?"
        )

    if any(w in cleaned for w in ['combien', 'mes culture', 'mes cultures', 'mes animaux', 'mes parcelle', 'mes parcelles', 'ma ferme', 'mon exploitation']):
        return (
            "📊 **Voici l'état actuel de ton exploitation** :\n"
            + user_context.replace("[CONTEXTE RÉEL DE L'EXPLOITATION", "**Données")
            + "\n\nTu veux modifier ou ajouter quelque chose ?"
        )

    return (
        "🌱 Je suis là pour t'aider sur tes cultures, tes bêtes ou tes couveuses.\n\n"
        "Dis-moi, quelle est ta question ?"
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

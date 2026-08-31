import json
import os
import urllib.request
import urllib.error
from datetime import datetime
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET, require_POST

from gestion.models import Culture, Animal, Parcelle, Volaille, Couveuse, Recolte

SESSION_HISTORY_LIMIT = 12

def _get_user_farm_context(user):
    """Extrait en direct les données réelles de l'exploitation de l'utilisateur pour contextualiser l'IA."""
    if not user.is_authenticated:
        return "Utilisateur anonyme."

    try:
        cultures = Culture.objects.filter(user=user)
        animaux = Animal.objects.filter(user=user)
        parcelles = Parcelle.objects.filter(user=user)
        volailles = Volaille.objects.filter(user=user)
        couveuses = Couveuse.objects.filter(user=user)

        crops_summary = ", ".join([f"{c.name} ({c.crop_type}, {c.area} ha)" for c in cultures[:5]]) or "Aucune culture"
        animals_summary = ", ".join([f"{a.name} ({a.species}, {a.health_status})" for a in animaux[:5]]) or "Aucun animal"
        plots_summary = ", ".join([f"{p.name} ({p.area} ha, {p.location})" for p in parcelles[:5]]) or "Aucune parcelle"
        incubators_summary = ", ".join([f"{i.eggs_count} œufs (statut: {i.status})" for i in couveuses[:3]]) or "Aucune incubation"

        return f"""
[CONTEXTE RÉEL DE L'EXPLOITATION DE L'UTILISATEUR ({user.username})] :
- Cultures actives ({cultures.count()}) : {crops_summary}
- Cheptel & Bétail ({animaux.count()} têtes) : {animals_summary}
- Parcelles enregistrées ({parcelles.count()}) : {plots_summary}
- Effectifs Volailles ({volailles.count()} lots enregistrés)
- Couveuses en cours ({couveuses.count()}) : {incubators_summary}
"""
    except Exception as e:
        return f"Exploitant : {user.username}."


def _build_system_instruction(user_context):
    return f"""Tu es AgroSedam AI, l'assistant agronome, vétérinaire et conseiller d'exploitation d'élite de la plateforme AgroSedam au Mali et dans toute la zone sahélienne (Afrique de l'Ouest).

{user_context}

Tes compétences et rôles clés :
1. Agriculture Sahélienne & Maraîchage :
   - Hivernage (juin à octobre) & contre-saison (octobre à mars).
   - Cultures majeures : Riz (Office du Niger / submersion / bas-fonds), Maïs, Mil, Sorgho, Oignon de Bandiagara, Tomate, Gombo, Manguiers (Kent, Amélie).
   - Gestion de l'eau : Forages solaires, château d'eau, goutte-à-goutte, paillage et économie d'eau.

2. Élevage & Santé Animale :
   - Races locales : Zébu Peul, Goudali, Azawak, Mouton Balibali, Touabir, Chèvre du Sahel.
   - Rationnement : Paille traitée à l'urée, fane d'arachide, tourteau de coton, compléments minéraux (pierre à lécher).
   - Prophylaxie & Vaccins : Péripneumonie bovine (PPCB), Pasteurellose, Charbon symptomatique, Peste des Petits Ruminants (PPR).

3. Aviculture & Couveuses Automatiques :
   - Pondeuses et Poulets de chair (Cobb 500), Pintades locales.
   - Calendrier de couvaison : J1 à J18 à 37.8°C / 55% humidité (retournement 2h), mirage à J7/J14, éclosoir J19-J21 à 37.2°C / 75% humidité.
   - Vaccins aviaires : Newcastle (HB1 / La Sota), Gumboro, Variole aviaire.

4. Accompagnement sur AgroSedam :
   - Si l'utilisateur demande des infos sur sa ferme, sers-toi du [CONTEXTE RÉEL DE L'EXPLOITATION] ci-dessus pour lui répondre avec précision !
   - Aide-le à naviguer : ajouter une récolte, enregistrer un animal, modifier une parcelle.

Règles de style :
- Réponds toujours en français professionnel, chaleureux, bien structuré avec des listes à puces et des émojis pertinents.
- Reste concis et pragmatique (2 à 4 paragraphes max) pour être facilement lisible sur smartphone au champ.
"""


def _call_gemini_api(api_key, user_message, history, user_context):
    """Appel direct à l'API Google Gemini avec system instruction et contexte de ferme."""
    model = os.getenv('GEMINI_MODEL', 'gemini-1.5-flash').strip()
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    
    system_prompt = _build_system_instruction(user_context)

    # Conversion de l'historique au format Gemini
    contents = []
    for h in history:
        role = "user" if h.get("role") == "user" else "model"
        content = (h.get("content") or "").strip()
        if content:
            contents.append({"role": role, "parts": [{"text": content}]})
            
    # Message courant
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

    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            res_data = json.loads(response.read().decode("utf-8"))
            candidates = res_data.get("candidates", [])
            if candidates:
                parts = candidates[0].get("content", {}).get("parts", [])
                if parts:
                    return parts[0].get("text", "").strip()
    except urllib.error.HTTPError as e:
        error_msg = e.read().decode("utf-8")
        print(f"[AgroSedam Gemini API Error {e.code}] : {error_msg}")
        return None
    except Exception as e:
        print(f"[AgroSedam Gemini Exception] : {e}")
        return None

    return None


def _get_local_expert_reply(cleaned, user_context):
    """Moteur agronomique de secours en cas d'absence de clé API."""
    if any(w in cleaned for w in ['combien', 'mes culture', 'mes animaux', 'mes parcelle', 'ma ferme', 'mon exploitation']):
        return (
            "📊 **Voici l'état actuel de votre exploitation** :\n\n"
            + user_context.replace("[CONTEXTE RÉEL DE L'EXPLOITATION DE L'UTILISATEUR", "**Détails de votre compte")
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

    if any(w in cleaned for w in ['bonjour', 'salut', 'bonsoir', 'kene', 'ani', 'hello', 'hi']):
        return (
            "👋 **I ni sogoma / Bonjour !**\n\n"
            "Je suis **AgroSedam AI**, votre conseiller agronomique et vétérinaire. Comment puis-je vous aider sur vos parcelles, troupeaux ou couveuses aujourd'hui ?"
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


@require_POST
def assistant_api(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentification requise pour discuter avec l’assistant.'}, status=401)

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

    # 1. Extraction du contexte réel de la ferme de l'utilisateur
    user_context = _get_user_farm_context(request.user)

    # 2. Clé API Gemini
    gemini_key = os.getenv('GEMINI_API_KEY', '').strip() or os.getenv('AGROSSEDAM_AI_API_KEY', '').strip()

    reply = None
    provider_name = 'AgroSedam Sahel Expert (Local)'

    if gemini_key:
        reply = _call_gemini_api(gemini_key, message, history, user_context)
        if reply:
            provider_name = f"Google Gemini ({os.getenv('GEMINI_MODEL', 'gemini-1.5-flash')})"

    # Fallback si pas de clé ou erreur réseau
    if not reply:
        reply = _get_local_expert_reply(message.lower(), user_context)

    current_time = datetime.now().strftime('%H:%M')
    return JsonResponse({
        'reply': reply,
        'timestamp': current_time,
        'provider': provider_name,
    })


@require_GET
def assistant_history(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentification requise.'}, status=401)
    return JsonResponse({'history': []})

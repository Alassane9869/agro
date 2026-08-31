document.addEventListener('DOMContentLoaded', () => {
  const widget = document.getElementById('assistant-widget');
  if (!widget) return;

  const toggle = document.getElementById('assistant-toggle');
  const panel = document.getElementById('assistant-panel');
  const messagesBox = document.getElementById('assistant-messages');
  const form = document.getElementById('assistant-form');
  const input = document.getElementById('assistant-input');
  const suggestions = document.querySelectorAll('[data-suggestion]');
  const clearBtn = document.getElementById('assistant-clear');
  const closeBtn = document.getElementById('assistant-close');
  const voiceBtn = document.getElementById('assistant-voice');

  const typingIndicator = document.createElement('div');
  typingIndicator.className = 'assistant-bubble assistant assistant-typing';
  typingIndicator.innerHTML = '<i class="fas fa-sparkles fa-spin me-2 text-emerald"></i><strong>AgroSedam AI</strong> réfléchit...';

  const state = {
    history: [],
    isListening: false,
    recognition: null,
    speakingUtterance: null
  };

  function formatMarkdown(text) {
    if (!text) return '';
    return text
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.*?)\*/g, '<em>$1</em>')
      .replace(/^• (.*$)/gim, '<div class="assistant-bullet d-flex align-items-start gap-2 my-1"><i class="fas fa-check text-emerald mt-1"></i><span>$1</span></div>')
      .replace(/^- (.*$)/gim, '<div class="assistant-bullet d-flex align-items-start gap-2 my-1"><i class="fas fa-check text-emerald mt-1"></i><span>$1</span></div>')
      .replace(/\n\n/g, '<br>')
      .replace(/\n/g, '<br>');
  }

  // Moteur Expert Agro local autonome (Fallback intelligent garanti 100% sans coupure)
  function getLocalExpertReply(userMsg) {
    const msg = userMsg.toLowerCase().trim();
    
    if (msg.includes('bonjour') || msg.includes('salut') || msg.includes('kene') || msg.includes('ani') || msg.includes('hello') || msg.includes('cv') || msg.includes('ca va') || msg.includes('ça va')) {
      return "👋 **I ni sogoma / Bonjour ! Tout va très bien, merci !**\n\nJe suis **AgroSedam AI**, votre conseiller agronomique et d'élevage 24h/24. Comment puis-je vous aider sur vos cultures, vos animaux ou vos couveuses aujourd'hui ?";
    }
    
    if (msg.includes('culture') || msg.includes('riz') || msg.includes('mais') || msg.includes('maïs') || msg.includes('tomate') || msg.includes('oignon') || msg.includes('gombo') || msg.includes('semis') || msg.includes('engrais') || msg.includes('recolte') || msg.includes('récolte')) {
      return "🌾 **Conseils Maraîchage & Grandes Cultures (Mali & Sahel)** :\n\n• **Campagne d'hivernage (Juin - Octobre)** : Privilégiez le riz (variétés NERICA / Gambiaka), le maïs et le mil. Effectuez le premier sarclage 15 à 21 jours après le semis.\n• **Contre-saison froide (Octobre - Mars)** : Période optimale pour les oignons de Bandiagara, tomates et piments sous irrigation goutte-à-goutte.\n• Consultez la rubrique **Cultures** pour ajouter ou suivre vos parcelles en temps réel.";
    }
    
    if (msg.includes('animal') || msg.includes('animaux') || msg.includes('vache') || msg.includes('bov') || msg.includes('zebu') || msg.includes('zébu') || msg.includes('mouton') || msg.includes('chevre') || msg.includes('chèvre') || msg.includes('vaccin') || msg.includes('maladie') || msg.includes('elevage') || msg.includes('élevage') || msg.includes('bellarine')) {
      return "🐄 **Conseils Élevage & Santé Animale au Sahel** :\n\n• **Prévention vaccinale** : Veillez aux rappels contre la Péripneumonie contagieuse bovine (PPCB), la Pasteurellose et le Charbon.\n• **Complémentation de saison sèche** : Distribuez des tourteaux de coton, des fanes d'arachide et disposez une pierre à lécher riche en minéraux.\n• Retrouvez vos bêtes enregistrées dans l'onglet **Élevage** pour suivre leur poids et matricule.";
    }
    
    if (msg.includes('couveuse') || msg.includes('incubation') || msg.includes('eclosion') || msg.includes('éclosion') || msg.includes('oeuf') || msg.includes('œuf') || msg.includes('mirage') || msg.includes('volaille') || msg.includes('poule') || msg.includes('poussin')) {
      return "🥚 **Paramètres d'Incubation & Couveuses Automatiques** :\n\n• **Jours 1 à 18** : Température constante à **37.8°C**, humidité à **50-55%** et retournement automatique toutes les 2 heures.\n• **Mirage (J7 et J14)** : Mire les œufs à la lampe pour retirer les œufs clairs ou non embryonnés.\n• **Jours 19 à 21 (Éclosoir)** : Arrêtez le retournement, baissez à **37.2°C** et augmentez l'humidité à **70-75%**.";
    }

    if (msg.includes('combien') || msg.includes('ferme') || msg.includes('exploitation') || msg.includes('parcelle') || msg.includes('donnée')) {
      return "📊 **Suivi de votre Exploitation AgroSedam** :\n\nVotre exploitation est synchronisée en temps réel sur votre tableau de bord. Vous pouvez suivre l'évolution de vos parcelles, troupeaux, pontes et récoltes depuis les modules dédiés !";
    }

    return "🌱 **AgroSedam AI à votre service !**\n\nPosez-moi vos questions précises sur :\n1. 🌾 **Cultures & Maraîchage** (Semis, arrosage, engrais, récolte)\n2. 🐄 **Santé Animale & Rations** (Vaccins, tourteau de coton, compléments)\n3. 🥚 **Couveuses & Aviculture** (Température, mirage, éclosion)\n\nQue souhaitez-vous savoir ?";
  }

  // Initialisation de la Reconnaissance Vocale (Web Speech API)
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (SpeechRecognition) {
    state.recognition = new SpeechRecognition();
    state.recognition.lang = 'fr-FR';
    state.recognition.interimResults = false;
    state.recognition.maxAlternatives = 1;

    state.recognition.onresult = (event) => {
      const speechResult = event.results[0][0].transcript;
      if (input) {
        input.value = speechResult;
        form.requestSubmit();
      }
    };

    state.recognition.onspeechend = () => {
      stopVoiceListening();
    };

    state.recognition.onerror = (event) => {
      console.warn('Erreur vocale:', event.error);
      stopVoiceListening();
    };

    state.recognition.onend = () => {
      stopVoiceListening();
    };
  }

  function startVoiceListening() {
    if (!state.recognition) {
      alert('La reconnaissance vocale n’est pas supportée sur ce navigateur.');
      return;
    }
    try {
      state.recognition.start();
      state.isListening = true;
      if (voiceBtn) {
        voiceBtn.classList.add('listening');
        voiceBtn.innerHTML = '<i class="fas fa-stop"></i>';
        voiceBtn.setAttribute('title', 'Arrêter l’écoute');
      }
      if (input) input.setAttribute('placeholder', '🎙️ Je vous écoute, parlez...');
    } catch (err) {
      console.warn('Recognition start error:', err);
    }
  }

  function stopVoiceListening() {
    if (state.recognition && state.isListening) {
      try { state.recognition.stop(); } catch(e) {}
    }
    state.isListening = false;
    if (voiceBtn) {
      voiceBtn.classList.remove('listening');
      voiceBtn.innerHTML = '<i class="fas fa-microphone"></i>';
      voiceBtn.setAttribute('title', 'Parler à l’assistant');
    }
    if (input) input.setAttribute('placeholder', 'Posez une question ou dictez...');
  }

  function speakText(rawText) {
    if (!('speechSynthesis' in window)) return;
    window.speechSynthesis.cancel();
    const cleanText = rawText.replace(/[*•#]/g, '');
    const utterance = new SpeechSynthesisUtterance(cleanText);
    utterance.lang = 'fr-FR';
    utterance.rate = 1.0;
    utterance.pitch = 1.0;
    window.speechSynthesis.speak(utterance);
  }

  function addMessage(text, role, timestamp = new Date().toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' })) {
    const bubble = document.createElement('div');
    bubble.className = `assistant-bubble ${role}`;
    
    let speakButtonHtml = '';
    if (role === 'assistant' && 'speechSynthesis' in window) {
      speakButtonHtml = `<button type="button" class="assistant-speak-btn mt-2" title="Écouter la réponse"><i class="fas fa-volume-high me-1"></i> Écouter</button>`;
    }

    const formattedHtml = role === 'assistant' ? formatMarkdown(text) : text;
    bubble.innerHTML = `<div>${formattedHtml}</div>${speakButtonHtml}<div class="assistant-meta">${timestamp}</div>`;
    
    if (role === 'assistant') {
      const speakBtn = bubble.querySelector('.assistant-speak-btn');
      if (speakBtn) {
        speakBtn.addEventListener('click', () => speakText(text));
      }
    }

    messagesBox.appendChild(bubble);
    messagesBox.scrollTop = messagesBox.scrollHeight;
  }

  function pushHistory(text, role) {
    state.history.push({ role, content: text });
    if (state.history.length > 12) {
      state.history = state.history.slice(-12);
    }
  }

  function addTypingIndicator() {
    messagesBox.appendChild(typingIndicator);
    messagesBox.scrollTop = messagesBox.scrollHeight;
  }

  function removeTypingIndicator() {
    typingIndicator.remove();
  }

  function openChat() {
    panel.classList.add('open');
    toggle?.classList.add('active');
    setTimeout(() => input?.focus(), 250);
  }

  function closeChat() {
    panel.classList.remove('open');
    toggle?.classList.remove('active');
    stopVoiceListening();
    if ('speechSynthesis' in window) window.speechSynthesis.cancel();
  }

  toggle?.addEventListener('click', (e) => {
    e.preventDefault();
    panel.classList.contains('open') ? closeChat() : openChat();
  });

  closeBtn?.addEventListener('click', (e) => {
    e.preventDefault();
    closeChat();
  });

  clearBtn?.addEventListener('click', (e) => {
    e.preventDefault();
    messagesBox.innerHTML = '';
    state.history = [];
    addMessage('Conversation effacée. Je suis prêt pour vos nouvelles questions agronomiques.', 'assistant');
  });

  if (voiceBtn) {
    voiceBtn.addEventListener('click', (e) => {
      e.preventDefault();
      state.isListening ? stopVoiceListening() : startVoiceListening();
    });
  }

  suggestions.forEach((btn) => {
    btn.addEventListener('click', () => {
      if (input) {
        input.value = btn.dataset.suggestion;
        input.focus();
        form.requestSubmit();
      }
    });
  });

  form?.addEventListener('submit', async (event) => {
    event.preventDefault();
    const message = input.value.trim();
    if (!message) return;

    addMessage(message, 'user');
    pushHistory(message, 'user');
    input.value = '';
    addTypingIndicator();

    try {
      const response = await fetch('/assistant/api/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': document.querySelector('meta[name="csrf-token"]')?.getAttribute('content') || ''
        },
        body: JSON.stringify({ message, history: state.history })
      });

      if (!response.ok) {
        throw new Error(`HTTP_${response.status}`);
      }

      const data = await response.json();
      removeTypingIndicator();
      
      const replyText = data.reply || getLocalExpertReply(message);
      const currentTime = data.timestamp || new Date().toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' });
      addMessage(replyText, 'assistant', currentTime);
      pushHistory(replyText, 'assistant');
    } catch (error) {
      removeTypingIndicator();
      console.info('Mode autonome AgroSedam activé:', error.message);
      // Réponse immédiate et intelligente même en cas de pare-feu WAF ou coupure
      const fallbackReply = getLocalExpertReply(message);
      const currentTime = new Date().toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' });
      addMessage(fallbackReply, 'assistant', currentTime);
      pushHistory(fallbackReply, 'assistant');
    }
  });
});

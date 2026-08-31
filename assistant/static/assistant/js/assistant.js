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

      const data = await response.json();
      removeTypingIndicator();
      if (response.ok) {
        const replyText = data.reply || 'Je n’ai pas pu traiter votre demande.';
        addMessage(replyText, 'assistant', data.timestamp || new Date().toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' }));
        pushHistory(replyText, 'assistant');
      } else {
        addMessage(data.error || 'Erreur lors de la communication avec l’assistant.', 'assistant');
      }
    } catch (error) {
      removeTypingIndicator();
      addMessage('Le service AgroSedam AI est momentanément inaccessible. Vérifiez votre connexion.', 'assistant');
    }
  });
});

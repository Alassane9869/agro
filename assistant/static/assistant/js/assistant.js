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
  const minimizeBtn = document.getElementById('assistant-minimize');
  const closeBtn = document.getElementById('assistant-close');
  const typingIndicator = document.createElement('div');
  typingIndicator.className = 'assistant-bubble assistant assistant-typing';
  typingIndicator.innerHTML = 'L’assistante écrit...';

  const state = {
    history: []
  };

  function addMessage(text, role, timestamp = new Date().toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' })) {
    const bubble = document.createElement('div');
    bubble.className = `assistant-bubble ${role}`;
    bubble.innerHTML = `<div>${text}</div><div class="assistant-meta">${timestamp}</div>`;
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
    input.focus();
  }

  function closeChat() {
    panel.classList.remove('open');
  }

  toggle.addEventListener('click', () => {
    panel.classList.contains('open') ? closeChat() : openChat();
  });

  minimizeBtn.addEventListener('click', () => {
    panel.classList.remove('open');
  });

  closeBtn.addEventListener('click', () => {
    panel.classList.remove('open');
  });

  clearBtn.addEventListener('click', () => {
    messagesBox.innerHTML = '';
    state.history = [];
    addMessage('Conversation effacée. Je suis prêt à recommencer.', 'assistant');
  });

  suggestions.forEach((btn) => {
    btn.addEventListener('click', () => {
      input.value = btn.dataset.suggestion;
      input.focus();
      form.requestSubmit();
    });
  });

  form.addEventListener('submit', async (event) => {
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
          'X-CSRFToken': document.querySelector('meta[name="csrf-token"]').getAttribute('content') || ''
        },
        body: JSON.stringify({ message, history: state.history })
      });

      const data = await response.json();
      removeTypingIndicator();
      if (response.ok) {
        addMessage(data.reply, 'assistant', data.timestamp || new Date().toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' }));
        pushHistory(data.reply, 'assistant');
      } else {
        addMessage(data.error || 'Impossible de contacter l’assistant.', 'assistant');
      }
    } catch (error) {
      removeTypingIndicator();
      addMessage('Le service est momentanément indisponible. Réessayez plus tard.', 'assistant');
    }
  });
});

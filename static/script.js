/* Chat Widget & Global Scripts */

(function() {
  'use strict';

  var toggle = document.getElementById('chat-toggle');
  var panel = document.getElementById('chat-panel');
  var close = document.getElementById('chat-close');
  var input = document.getElementById('chat-input');
  var send = document.getElementById('chat-send');
  var messages = document.getElementById('chat-messages');

  if (!toggle || !panel || !messages) return;

  var WELCOME = "Hi! I'm your Dishcovery food assistant. Ask me about cuisines, dishes or diets. Or use Find Food to search restaurants near you!";

  function showPanel() {
    panel.classList.remove('hidden');
    input.focus();
  }

  function hidePanel() {
    panel.classList.add('hidden');
  }

  function addMessage(text, isUser) {
    var div = document.createElement('div');
    div.className = 'chat-msg' + (isUser ? ' chat-msg-user' : '');
    var p = document.createElement('p');
    p.textContent = text;
    div.appendChild(p);
    messages.appendChild(div);
    messages.scrollTop = messages.scrollHeight;
  }

  function sendMessage() {
    var text = (input.value || '').trim();
    if (!text) return;

    addMessage(text, true);
    input.value = '';
    input.disabled = true;
    send.disabled = true;

    fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: text })
    })
      .then(function(r) { return r.json(); })
      .then(function(data) {
        addMessage(data.reply || 'Something went wrong.', false);
      })
      .catch(function() {
        addMessage('Could not reach the server. Please try again.', false);
      })
      .finally(function() {
        input.disabled = false;
        send.disabled = false;
        input.focus();
      });
  }

  function initChat() {
    if (messages.children.length === 0) {
      addMessage(WELCOME, false);
    }
  }

  toggle.addEventListener('click', function() {
    if (panel.classList.contains('hidden')) {
      showPanel();
      initChat();
    } else {
      hidePanel();
    }
  });

  if (close) close.addEventListener('click', hidePanel);

  if (send) send.addEventListener('click', sendMessage);

  if (input) {
    input.addEventListener('keypress', function(e) {
      if (e.key === 'Enter') sendMessage();
    });
  }
})();

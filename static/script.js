/* Chat Widget & Global Scripts */

(function() {
  'use strict';

  var toggle = document.getElementById('chat-toggle');
  var panel = document.getElementById('chat-panel');
  var close = document.getElementById('chat-close');
  var input = document.getElementById('chat-input');
  var send = document.getElementById('chat-send');
  var messages = document.getElementById('chat-messages');
  var pendingBotMessage = null;
  var typingStartTime = 0;

  if (!toggle || !panel || !messages) return;

  var WELCOME = "Hi! I'm your Dishcovery food assistant. Ask me about cuisines, dishes, diets or places near you. Say things like 'cheap sushi near me' and I'll suggest nearby restaurants using your location.";

  function showPanel() {
    panel.classList.remove('hidden');
    input.focus();
  }

  function hidePanel() {
    panel.classList.add('hidden');
  }

  function addMessage(text, isUser, isHtml, extraClass) {
    var div = document.createElement('div');
    var cls = 'chat-msg' + (isUser ? ' chat-msg-user' : '');
    if (extraClass) {
      cls += ' ' + extraClass;
    }
    div.className = cls;
    var p = document.createElement('p');
    if (isHtml) {
      p.innerHTML = text;
    } else {
      p.textContent = text;
    }
    div.appendChild(p);
    messages.appendChild(div);
    messages.scrollTop = messages.scrollHeight;
    return div;
  }

  function sendMessage() {
    var text = (input.value || '').trim();
    if (!text) return;

    addMessage(text, true, false);
    input.value = '';
    input.disabled = true;
    send.disabled = true;

    // Show typing bubble immediately; keep at least 2 seconds before swapping to reply.
    typingStartTime = Date.now();
    pendingBotMessage = addMessage('Typing...', false, false, 'chat-msg-typing');

    function doSend(lat, lng) {
      var payload = { message: text };
      if (typeof lat === 'number' && typeof lng === 'number') {
        payload.lat = lat;
        payload.lng = lng;
      }
      
      var thisTypingBubble = pendingBotMessage;

      fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      })
        .then(function(r) {
          return r.json().then(function(data) {
            if (!r.ok) {
              var msg = r.status === 429 ? (data.reply || 'Too many messages. Please wait a minute and try again.') : (data.reply || 'Something went wrong.');
              if (thisTypingBubble && thisTypingBubble.parentNode) {
                thisTypingBubble.parentNode.removeChild(thisTypingBubble);
              }
              pendingBotMessage = null;
              addMessage(msg, false, false);
              throw new Error('request failed');
            }
            return data;
          });
        })
        .then(function(data) {
          var reply = data.reply || 'Something went wrong.';
          var elapsed = Date.now() - typingStartTime;
          var update = function() {
            if (thisTypingBubble && thisTypingBubble.parentNode) {
              thisTypingBubble.parentNode.removeChild(thisTypingBubble);
            }
            pendingBotMessage = null;
            addMessage(reply, false, true);
          };
          if (elapsed < 2000) {
            setTimeout(update, 2000 - elapsed);
          } else {
            update();
          }
        })
        .catch(function(err) {
          if (err && err.message === 'request failed') return;
          var msg = 'Could not reach the server. Please try again.';
          var elapsed = Date.now() - typingStartTime;
          var update = function() {
            if (thisTypingBubble && thisTypingBubble.parentNode) {
              thisTypingBubble.parentNode.removeChild(thisTypingBubble);
            }
            pendingBotMessage = null;
            addMessage(msg, false, false);
          };
          if (elapsed < 2000) {
            setTimeout(update, 2000 - elapsed);
          } else {
            update();
          }
        })
        .finally(function() {
          input.disabled = false;
          send.disabled = false;
          input.focus();
        });
    }

    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        function(pos) {
          doSend(pos.coords.latitude, pos.coords.longitude);
        },
        function() {
          doSend();
        },
        { timeout: 7000 }
      );
    } else {
      doSend();
    }
  }

  function initChat() {
    if (messages.children.length === 0) {
      addMessage(WELCOME, false, false);
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

  document.querySelectorAll('.chat-chip').forEach(function(btn) {
    btn.addEventListener('click', function() {
      var msg = this.getAttribute('data-message');
      if (msg) {
        input.value = msg;
        sendMessage();
      }
    });
  });

  var clearBtn = document.getElementById('chat-clear');
  if (clearBtn) {
    clearBtn.addEventListener('click', function() {
      messages.innerHTML = '';
      addMessage(WELCOME, false, false);
    });
  }
})();

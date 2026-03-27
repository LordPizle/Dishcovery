/* Chat Widget & Global Scripts */

(function() {
  'use strict';

  var toggle = document.getElementById('chat-toggle');
  var panel = document.getElementById('chat-panel');
  var chatHeader = panel ? panel.querySelector('.chat-header') : null;
  var close = document.getElementById('chat-close');
  var fullscreenBtn = document.getElementById('chat-fullscreen');
  var input = document.getElementById('chat-input');
  var send = document.getElementById('chat-send');
  var messages = document.getElementById('chat-messages');
  var pendingBotMessage = null;
  var typingStartTime = 0;
  var savedBeforeFullscreen = null;

  if (!toggle || !panel || !messages) return;

  var WELCOME = "Hi! I'm your Dishcovery food assistant. Ask me about cuisines, dishes, diets or places near you. Say things like 'cheap sushi near me' and I'll suggest nearby restaurants using your location.";

  function updateFullscreenButton() {
    if (!fullscreenBtn) return;
    var enabled = panel.classList.contains('is-fullscreen');
    fullscreenBtn.textContent = enabled ? '🗗' : '⤢';
    fullscreenBtn.setAttribute('aria-label', enabled ? 'Exit fullscreen' : 'Enter fullscreen');
  }

  function clearPanelPositionStyles() {
    panel.style.position = '';
    panel.style.left = '';
    panel.style.top = '';
    panel.style.right = '';
    panel.style.bottom = '';
    panel.style.width = '';
    panel.style.transform = '';
    panel.classList.remove('chat-panel--user-placed');
  }

  function enterFullscreenLayout() {
    // Save floating position/size so we can restore after exiting fullscreen.
    savedBeforeFullscreen = {
      userPlaced: panel.classList.contains('chat-panel--user-placed'),
      left: panel.style.left,
      top: panel.style.top,
      width: panel.style.width,
      position: panel.style.position,
      transform: panel.style.transform
    };
    panel.classList.remove('chat-panel--user-placed');
    panel.style.left = '';
    panel.style.top = '';
    panel.style.right = '';
    panel.style.bottom = '';
    panel.style.width = '';
    panel.style.transform = '';
    panel.style.position = '';
    panel.classList.add('is-fullscreen');
  }

  function exitFullscreenLayout() {
    panel.classList.remove('is-fullscreen');
    updateFullscreenButton();
    if (!savedBeforeFullscreen) return;
    var s = savedBeforeFullscreen;
    savedBeforeFullscreen = null;
    if (s.userPlaced) {
      panel.classList.add('chat-panel--user-placed');
      panel.style.position = s.position || 'fixed';
      panel.style.left = s.left;
      panel.style.top = s.top;
      panel.style.width = s.width;
      panel.style.transform = s.transform;
    } else if (panel.style.left && panel.style.top) {
      panel.classList.add('chat-panel--user-placed');
      panel.style.position = 'fixed';
      panel.style.transform = '';
    } else {
      clearPanelPositionStyles();
    }
  }

  function showPanel() {
    panel.classList.remove('hidden');
    input.focus();
  }

  function hidePanel() {
    var wasFs = panel.classList.contains('is-fullscreen');
    panel.classList.add('hidden');
    if (wasFs) {
      exitFullscreenLayout();
    } else {
      savedBeforeFullscreen = null;
    }
    panel.classList.remove('is-dragging');
    updateFullscreenButton();
  }

  function toggleFullscreen() {
    if (!panel || panel.classList.contains('hidden')) return;
    if (panel.classList.contains('is-fullscreen')) {
      exitFullscreenLayout();
    } else {
      enterFullscreenLayout();
      updateFullscreenButton();
    }
  }

  function isHeaderControlTarget(el) {
    return el && el.closest && el.closest('.chat-header-actions');
  }

  function beginHeaderDrag(e) {
    if (panel.classList.contains('hidden')) return;
    if (isHeaderControlTarget(e.target)) return;
    if (e.button != null && e.button !== 0) return;

    var isFs = panel.classList.contains('is-fullscreen');
    var rect = panel.getBoundingClientRect();
    var offsetX = e.clientX - rect.left;
    var offsetY = e.clientY - rect.top;

    if (isFs) {
      // Convert fullscreen panel to fixed pixel box before dragging.
      panel.style.transform = 'none';
      panel.style.position = 'fixed';
      panel.style.left = rect.left + 'px';
      panel.style.top = rect.top + 'px';
      panel.style.width = rect.width + 'px';
    } else if (!panel.classList.contains('chat-panel--user-placed')) {
      panel.classList.add('chat-panel--user-placed');
      panel.style.position = 'fixed';
      panel.style.left = rect.left + 'px';
      panel.style.top = rect.top + 'px';
      panel.style.right = 'auto';
      panel.style.bottom = 'auto';
      panel.style.width = rect.width + 'px';
    }

    panel.classList.add('is-dragging');

    function onMove(ev) {
      var pw = panel.offsetWidth;
      var ph = panel.offsetHeight;
      var left = ev.clientX - offsetX;
      var top = ev.clientY - offsetY;
      // Keep panel fully visible while dragging.
      left = Math.max(0, Math.min(left, window.innerWidth - pw));
      top = Math.max(0, Math.min(top, window.innerHeight - ph));
      panel.style.left = left + 'px';
      panel.style.top = top + 'px';
    }

    function onUp() {
      document.removeEventListener('pointermove', onMove);
      document.removeEventListener('pointerup', onUp);
      document.removeEventListener('pointercancel', onUp);
      panel.classList.remove('is-dragging');
      if (chatHeader && e.pointerId != null) {
        try {
          chatHeader.releasePointerCapture(e.pointerId);
        } catch (err) {}
      }
    }

    if (chatHeader && e.pointerId != null) {
      try {
        chatHeader.setPointerCapture(e.pointerId);
      } catch (err) {}
    }
    document.addEventListener('pointermove', onMove);
    document.addEventListener('pointerup', onUp);
    document.addEventListener('pointercancel', onUp);

    e.preventDefault();
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

  if (chatHeader) chatHeader.addEventListener('pointerdown', beginHeaderDrag);

  window.addEventListener('resize', function() {
    if (panel.classList.contains('hidden') || !panel.classList.contains('chat-panel--user-placed')) return;
    var pw = panel.offsetWidth;
    var ph = panel.offsetHeight;
    var left = parseFloat(panel.style.left, 10);
    var top = parseFloat(panel.style.top, 10);
    if (isNaN(left)) left = 0;
    if (isNaN(top)) top = 0;
    // Re-clamp position after viewport size changes.
    left = Math.max(0, Math.min(left, window.innerWidth - pw));
    top = Math.max(0, Math.min(top, window.innerHeight - ph));
    panel.style.left = left + 'px';
    panel.style.top = top + 'px';
  });

  if (close) close.addEventListener('click', hidePanel);
  if (fullscreenBtn) fullscreenBtn.addEventListener('click', toggleFullscreen);

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

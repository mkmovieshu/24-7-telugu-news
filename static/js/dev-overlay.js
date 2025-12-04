// static/js/dev-overlay.js
(function(){
  if (window.__DEV_OVERLAY_LOADED) return;
  window.__DEV_OVERLAY_LOADED = true;

  const css = `
  #dev-overlay { position:fixed; right:10px; bottom:10px; width:320px; max-height:45vh; overflow:auto;
    background:rgba(0,0,0,0.85); color:#fff; font-family:monospace; font-size:12px; padding:8px; border-radius:8px;
    z-index:999999; box-shadow:0 6px 18px rgba(0,0,0,0.5); }
  #dev-overlay h4 { margin:0 0 6px 0; font-size:13px; color:#ffd700; }
  #dev-overlay pre { white-space:pre-wrap; word-break:break-word; margin:0; }
  #dev-overlay .close { position:absolute; left:8px; top:6px; color:#fff; opacity:0.6; cursor:pointer; }
  `;
  const style = document.createElement('style');
  style.textContent = css; document.head.appendChild(style);

  const overlay = document.createElement('div');
  overlay.id = 'dev-overlay';
  overlay.innerHTML = `<div class="close">✕</div><h4>Dev Overlay (errors)</h4><pre id="dev-logs">no errors</pre>`;
  document.body.appendChild(overlay);

  overlay.querySelector('.close').onclick = () => overlay.style.display='none';

  const logsEl = document.getElementById('dev-logs');
  function add(msg){
    const time = new Date().toLocaleTimeString();
    logsEl.textContent = `${time} — ${msg}\n\n` + logsEl.textContent;
  }

  window.addEventListener('error', function(e){
    add('ERROR: ' + (e && e.message ? e.message : JSON.stringify(e)));
  });
  window.addEventListener('unhandledrejection', function(e){
    add('UNHANDLED_PROMISE: ' + (e && e.reason ? (e.reason.message || JSON.stringify(e.reason)) : JSON.stringify(e)));
  });

  // small helper to log from code
  window.devLog = function(msg){ add(String(msg)); };

  // also expose fetch logger
  const originalFetch = window.fetch;
  window.fetch = function(...args){
    const [resource] = args;
    return originalFetch.apply(this, args).then(res=>{
      if (!res.ok) {
        add(`FETCH ${resource} => ${res.status} ${res.statusText}`);
      }
      return res;
    }).catch(err=>{
      add(`FETCH_ERROR ${resource} => ${err && err.message ? err.message : JSON.stringify(err)}`);
      throw err;
    });
  };
})();

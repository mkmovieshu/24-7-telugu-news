// static/js/main.js - పూర్తి సరిచేసిన కోడ్
// api.js నుండి ఫంక్షన్లను ఆలియాస్‌లతో ఇంపోర్ట్ చేయడం ద్వారా రికర్షన్ నివారిస్తుంది.
import { 
  fetchNews as apiFetchNews, 
  postReaction as apiPostReaction, 
  fetchComments as apiFetchComments, 
  postComment as apiPostComment 
} from './api.js'; 

(function(){
  // ======= config =======
  const NEWS_LIMIT = 100;

  // ======= state =======
  let newsList = [];
  let idx = 0;

  // ======= DOM refs (No change) =======
  const titleEl = document.getElementById('news-title');
  const summaryEl = document.getElementById('news-summary');
  const linkEl = document.getElementById('news-link');
  const likesCountEl = document.getElementById('likesCount');
  const dislikesCountEl = document.getElementById('dislikesCount');
  const prevBtn = document.getElementById('prevBtn');
  const nextBtn = document.getElementById('nextBtn');

  const commentListEl = document.getElementById('commentList');
  const commentForm = document.getElementById('commentForm');
  const commentInput = document.getElementById('commentInput');
  const commentsCountEl = document.getElementById('comments-count');

  // logger overlay
  const logBox = document.getElementById('mini-logger');
  const toggleBtn = document.getElementById('logger-toggle');
  toggleBtn.addEventListener('click', ()=> {
    logBox.style.display = logBox.style.display === 'block' ? 'none' : 'block';
  });
  function log(type, msg){
    try{
      const d = document.createElement('div');
      d.textContent = `[${type}] ${msg}`;
      if(type==='error') d.style.color = '#ff8080';
      logBox.appendChild(d);
      logBox.scrollTop = logBox.scrollHeight;
    }catch(e){}
    if(type==='error') console.error(msg); else console.log(msg);
  }

  // ======= UI renderers (No change) =======
  function renderCard(){
    if(!newsList || newsList.length===0){
      titleEl.textContent = "టైటిల్ లేదు";
      summaryEl.textContent = "న్యూస్ లోడ్ అవలేదో... అప్పుడు Refresh చెయ్యండి";
      linkEl.href = "#";
      likesCountEl.textContent = "0";
      dislikesCountEl.textContent = "0";
      commentListEl.innerHTML = '';
      commentsCountEl.textContent = "0";
      return;
    }
    const item = newsList[idx];
    titleEl.textContent = item.title || 'ఉపశీర్షిక లేదు';
    summaryEl.textContent = item.summary || '';
    linkEl.href = item.link || '#';
    likesCountEl.textContent = (item.likes||0);
    dislikesCountEl.textContent = (item.dislikes||0);

    // load comments for this news
    loadCommentsForCurrent();
  }

  function showNext(){
    if(newsList.length===0) return;
    idx = (idx + 1) % newsList.length;
    renderCard();
  }
  function showPrev(){
    if(newsList.length===0) return;
    idx = (idx - 1 + newsList.length) % newsList.length;
    renderCard();
  }

  // ======= backend actions (MODIFIED to use api.js imports) =======
  async function loadNews(){
    try{
      // MODIFIED: Use apiFetchNews (imported function)
      const data = await apiFetchNews(NEWS_LIMIT); 
      
      const items = data.items || [];
      // normalize: ensure id, title, summary, link, likes, dislikes (from original code)
      newsList = items.map(it=>({
        id: it.id || it._id || '',
        title: it.title || '',
        summary: it.summary || '',
        link: it.link || it.source || '',
        likes: Number(it.likes||0),
        dislikes: Number(it.dislikes||0)
      }));
      idx = 0;
      renderCard();
      log('info', `loaded ${newsList.length} news`);
    }catch(err){
      log('error', 'loadNews error: ' + err.message);
      titleEl.textContent = "న్యూస్ లోడ్ తప్పియా";
      summaryEl.textContent = err.message || '';
    }
  }

  async function postReaction(action){
    if(!newsList[idx] || !newsList[idx].id) { log('error','no news id'); return; }
    const id = newsList[idx].id;
    try{
      // MODIFIED: Use apiPostReaction (imported function)
      const res = await apiPostReaction(id, action);
      
      // update local
      newsList[idx].likes = res.likes;
      newsList[idx].dislikes = res.dislikes;
      likesCountEl.textContent = newsList[idx].likes;
      dislikesCountEl.textContent = newsList[idx].dislikes;
    }catch(err){
      log('error','postReaction error: ' + (err.message||err));
      alert('Reaction తప్పిపోయింది: '+ (err.message||err)); 
    }
  }

  async function loadCommentsForCurrent(){
    commentListEl.innerHTML = '';
    commentsCountEl.textContent = '0';
    if(!newsList[idx] || !newsList[idx].id) return;
    const id = newsList[idx].id;
    try{
      // MODIFIED: Use apiFetchComments (imported function)
      const data = await apiFetchComments(id);
      
      const items = (data.items || []);
      commentsCountEl.textContent = items.length;
      if(items.length===0){
        commentListEl.innerHTML = '<div class="sm">ఇక్కడ ఎటువంటి కామెంట్స్ లేవు</div>';
        return;
      }
      for(const c of items){
        const el = document.createElement('div');
        el.className = 'comment';
        el.textContent = c.text + '  ·  ' + (c.created_at ? new Date(c.created_at).toLocaleString() : '');
        commentListEl.appendChild(el);
      }
    }catch(err){
      log('error','loadComments error: '+err.message);
      commentListEl.innerHTML = '<div class="sm">కామెంట్స్ లో లోప్</div>';
    }
  }

  async function postComment(text){
    if(!newsList[idx] || !newsList[idx].id) { alert('News id లేదు'); return; }
    if(!text || !text.trim()){ alert('ఖాళీ కామెంట్ పంప్వద్దు'); return; }
    const id = newsList[idx].id;
    try{
      // MODIFIED: Use apiPostComment (imported function)
      const res = await apiPostComment(id, text);
      
      // add to local render immediately by reloading comments
      commentInput.value = '';
      await loadCommentsForCurrent();
    }catch(err){
      log('error','postComment error: '+err.message);
      alert('కామెంట్ పంపడంలో లోపం: '+ (err.message||err));
    }
  }

  // ======= attach events =======
  prevBtn.addEventListener('click', showPrev);
  nextBtn.addEventListener('click', showNext);
  document.getElementById('likeBtn').addEventListener('click', ()=>postReaction('like'));
  document.getElementById('dislikeBtn').addEventListener('click', ()=>postReaction('dislike'));

  commentForm.addEventListener('submit', function(ev){
    ev.preventDefault();
    const txt = commentInput.value;
    postComment(txt);
  });

  // enable left/right arrow keys
  window.addEventListener('keydown', function(e){
    if(e.key === 'ArrowRight') showNext();
    if(e.key === 'ArrowLeft') showPrev();
  });

  // on load
  document.addEventListener('DOMContentLoaded', ()=>{
    loadNews();
  });

  // catch errors
  window.addEventListener('error', function(ev){
    log('error','JS error: '+ev.message+' @ '+(ev.filename||'')+':'+(ev.lineno||''));
  });
  window.addEventListener('unhandledrejection', function(ev){
    log('error','Promise reject: '+(ev.reason && ev.reason.message ? ev.reason.message : JSON.stringify(ev.reason)));
  });

})();

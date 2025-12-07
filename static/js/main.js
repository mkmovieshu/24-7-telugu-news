// static/js/main.js - అప్‌డేట్ చేసిన కోడ్

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

  // ======= DOM refs =======
  const titleEl = document.getElementById('news-title');
  const summaryEl = document.getElementById('news-summary');
  const linkEl = document.getElementById('news-link');
  const likesCountEl = document.getElementById('likesCount');
  const dislikesCountEl = document.getElementById('dislikesCount');
  
  // ✅ కొత్తగా జోడించినది: న్యూస్ తేదీ ఎలిమెంట్
  const dateEl = document.getElementById('news-date'); 
  
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
  
  // ... (మిగిలిన log ఫంక్షన్)

  function showNews(idx) {
    if (newsList.length === 0) return;
    const item = newsList[idx];

    titleEl.textContent = item.title;
    summaryEl.textContent = item.summary;
    linkEl.href = item.link;
    
    // ✅ తేదీ/సమయాన్ని ఫార్మాట్ చేసి చూపించడం
    if (item.published) {
        try {
            const dateObj = new Date(item.published);
            // 'te-IN' (తెలుగు - భారతదేశం) లో ఫార్మాట్ చేస్తుంది
            dateEl.textContent = dateObj.toLocaleDateString('te-IN', {
                year: 'numeric',
                month: 'long',
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit',
                timeZoneName: 'short' // ఉదా: IST
            });
        } catch (e) {
            log('error', 'Date parsing failed for ' + item.id + ': ' + e.message);
            dateEl.textContent = 'తేదీ అందుబాటులో లేదు';
        }
    } else {
        dateEl.textContent = 'తేదీ అందుబాటులో లేదు';
    }

    // ... (మిగిలిన కోడ్)
    
// ... (మిగిలిన ఫంక్షన్)

// ... (చివరికి ఈ విధంగా ఉండాలి)

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
  document.addEventListener('DOMContentLoaded', ()=> {
    loadNews();
  });

  // catch errors
  window.addEventListener('error', function(ev){
    log('error','JS error: '+ev.message+' @ '+(ev.filename||'')+':'+(ev.lineno||''));
  });
  window.addEventListener('unhandledrejection', function(ev){
    log('error','Unhandled promise rejection: '+ev.reason);
  });

})(); // end IIFE

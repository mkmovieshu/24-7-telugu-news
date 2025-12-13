// static/js/main.js - పూర్తి సరిచేసిన కోడ్ (తేదీ డిస్‌ప్లే, స్వైపింగ్ ఫిక్స్)
// api.js నుండి ఫంక్షన్లను ఆలియాస్‌లతో ఇంపోర్ట్ చేయడం ద్వారా రికర్షన్ నివారిస్తుంది.
import { 
  fetchNews as apiFetchNews, 
  postReaction as apiPostReaction, 
  fetchComments as apiFetchComments, 
  postComment as apiPostComment 
} from '/static/js/api.js'; // <--- రూట్ నుండి పూర్తి మార్గాన్ని ఉపయోగించండి
// ... మిగిలిన కోడ్ ...

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
  // ✅ కొత్తగా చేర్చబడింది: న్యూస్ తేదీ ఎలిమెంట్
  const dateEl = document.getElementById('news-date'); 
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

  const logMessagesEl = document.getElementById('log-messages');
  function log(level, message) {
    console.log(`[${level.toUpperCase()}] ${message}`);
    const li = document.createElement('li');
    li.className = `log-${level}`;
    li.textContent = `[${new Date().toLocaleTimeString()}] ${message}`;
    logMessagesEl.prepend(li);
    if (logMessagesEl.children.length > 50) {
      logMessagesEl.removeChild(logMessagesEl.lastChild);
    }
  }

  // ======= Navigation =======

  function showNews(idx) {
    if (newsList.length === 0) return;

    const item = newsList[idx];

    titleEl.textContent = item.title;
    summaryEl.textContent = item.summary || 'సారాంశం ఇంకా సిద్ధం కాలేదు.';
    linkEl.href = item.link;

    // ✅ మార్పు 2: తేదీ/సమయాన్ని ఫార్మాట్ చేసి చూపించడం
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
    
    // లైక్స్/డిస్‌లైక్స్ అప్‌డేట్ చేయండి
    likesCountEl.textContent = item.likes || 0;
    dislikesCountEl.textContent = item.dislikes || 0;

    // నావిగేషన్ బటన్లను అప్‌డేట్ చేయండి
    prevBtn.disabled = idx === 0;
    nextBtn.disabled = idx === newsList.length - 1;

    // కామెంట్లు లోడ్ చేయండి
    loadCommentsForCurrent();
  }

  function showNext() {
    if (idx < newsList.length - 1) {
      idx++;
      showNews(idx);
    } else {
      log('info', 'చివరి వార్తకి చేరుకున్నారు.');
    }
  }

  function showPrev() {
    if (idx > 0) {
      idx--;
      showNews(idx);
    } else {
      log('info', 'మొదటి వార్త వద్ద ఉన్నారు.');
    }
  }

  prevBtn.addEventListener('click', showPrev);
  nextBtn.addEventListener('click', showNext);

  // ======= API Calls / Data Loading =======

  async function loadNews() {
    log('info', 'వార్తలను లోడ్ చేస్తున్నాము...');
    try {
      const data = await apiFetchNews(NEWS_LIMIT);
      newsList = data.items;
      if (newsList.length > 0) {
        log('success', `${newsList.length} వార్తలు విజయవంతంగా లోడ్ చేయబడ్డాయి.`);
        idx = 0; // మొదటి వార్త నుండి ప్రారంభించండి
        showNews(idx);
      } else {
        log('warning', 'వార్తలు ఏవీ లోడ్ కాలేదు. ఫీడ్స్ లేదా డేటాబేస్‌ను తనిఖీ చేయండి.');
        summaryEl.textContent = 'క్షమించండి, వార్తలు ఏవీ అందుబాటులో లేవు.';
      }
    } catch (e) {
      log('error', 'వార్తలు లోడ్ చేయడంలో లోపం: ' + e.message);
      summaryEl.textContent = 'వార్తలను లోడ్ చేయడంలో లోపం సంభవించింది.';
    }
  }

  // ======= Reactions =======

  async function handleReaction(type) {
    if (newsList.length === 0) return;
    const item = newsList[idx];
    log('info', `స్పందన (${type}) పంపుతోంది...`);
    try {
      const data = await apiPostReaction(item.id, type);
      // అప్‌డేట్ చేసిన లైక్స్/డిస్‌లైక్స్ కౌంట్‌ను అప్‌డేట్ చేయండి
      item.likes = data.likes;
      item.dislikes = data.dislikes;
      likesCountEl.textContent = item.likes;
      dislikesCountEl.textContent = item.dislikes;
      log('success', `స్పందన విజయవంతమైంది. Likes: ${item.likes}, Dislikes: ${item.dislikes}`);
    } catch (e) {
      log('error', 'స్పందన పంపడంలో లోపం: ' + e.message);
    }
  }

  document.getElementById('likeBtn').addEventListener('click', () => handleReaction('like'));
  document.getElementById('dislikeBtn').addEventListener('click', () => handleReaction('dislike'));

  // ======= Comments =======

  async function loadCommentsForCurrent() {
    if (newsList.length === 0) {
        commentListEl.innerHTML = '';
        commentsCountEl.textContent = '0';
        return;
    }
    const newsId = newsList[idx].id;
    log('info', 'కామెంట్లు లోడ్ చేస్తున్నాము...');
    try {
      const data = await apiFetchComments(newsId);
      const items = data.items;
      commentsCountEl.textContent = items.length;
      commentListEl.innerHTML = ''; // కామెంట్ల జాబితాను శుభ్రం చేయండి

      items.forEach(comment => {
        const li = document.createElement('li');
        li.className = 'comment-item';
        // కామెంట్ తేదీ ఫార్మాటింగ్
        let commentDate = 'సమయం లేదు';
        try {
            const dateObj = new Date(comment.created_at);
            commentDate = dateObj.toLocaleDateString('te-IN', {
                month: 'short',
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
            });
        } catch(e) {}
        
        li.innerHTML = `
          <p class="comment-text">${comment.text}</p>
          <span class="comment-date">${commentDate}</span>
        `;
        commentListEl.appendChild(li);
      });
      log('success', `${items.length} కామెంట్లు లోడ్ చేయబడ్డాయి.`);

    } catch (e) {
      log('error', 'కామెంట్లు లోడ్ చేయడంలో లోపం: ' + e.message);
      commentListEl.innerHTML = '<li class="comment-item">కామెంట్లు లోడ్ చేయడంలో లోపం.</li>';
    }
  }

  commentForm.addEventListener('submit', async function(e) {
    e.preventDefault();
    if (newsList.length === 0) return;
    const newsId = newsList[idx].id;
    const text = commentInput.value.trim();

    if (!text) {
      log('warning', 'కామెంట్‌లో ఖాళీగా ఉంది.');
      return;
    }
    
    log('info', 'కామెంట్ పోస్ట్ చేస్తున్నాము...');

    try {
      await apiPostComment(newsId, text);
      commentInput.value = ''; // ఫామ్‌ను శుభ్రం చేయండి
      log('success', 'కామెంట్ విజయవంతంగా పోస్ట్ చేయబడింది.');
      // అప్‌డేట్ అయిన కామెంట్‌ల కోసం మళ్లీ లోడ్ చేయండి
      await loadCommentsForCurrent(); 
    } catch (e) {
      log('error', 'కామెంట్ పోస్ట్ చేయడంలో లోపం: ' + e.message);
    }
  });


  // ======= Init / Global Export =======
  
  // enable left/right arrow keys
  window.addEventListener('keydown', function(e){
    if(e.key === 'ArrowRight') showNext();
    if(e.key === 'ArrowLeft') showPrev();
  });

  // ✅ మార్పు 3: స్వైపింగ్ కోసం గ్లోబల్ యాక్సెస్ (swipe.js దీనిని ఉపయోగిస్తుంది)
  window.showNext = showNext;
  window.showPrev = showPrev;
  
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

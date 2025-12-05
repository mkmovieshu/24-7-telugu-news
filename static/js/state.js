let state = {
    news: [],
    index: 0,
};

export function setNews(items) {
    state.news = items;
}

export function getCurrentNews() {
    return state.news[state.index] || null;
}

export function nextNews() {
    if (state.index < state.news.length - 1) {
        state.index++;
        return true;
    }
    return false;
}

export function prevNews() {
    if (state.index > 0) {
        state.index--;
        return true;
    }
    return false;
}

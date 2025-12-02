// api.js
import { setItems } from "./state.js";

const ENDPOINT = "/news"; // backend లో ఉన్న GET న్యూస్ రూట్

function normalizeItems(raw) {
  if (Array.isArray(raw)) return raw;
  if (raw && Array.isArray(raw.items)) return raw.items;
  if (raw && Array.isArray(raw.news)) return raw.news;
  if (raw && Array.isArray(raw.data)) return raw.data;
  return [];
}

export async function loadNews() {
  const res = await fetch(ENDPOINT);
  if (!res.ok) {
    throw new Error("News fetch failed");
  }
  const json = await res.json();
  const items = normalizeItems(json);
  setItems(items);
  return items;
}

const $ = s => document.querySelector(s);
const tr = k => (window.KM_I18N ? window.KM_I18N.t(k) : k);

const show = (id, html, error = false) => {
  const b = document.getElementById(id);
  b.className = `result${error ? ' error' : ''}`;
  b.innerHTML = html;
  // Every result can be read aloud on the website for farmers who prefer
  // listening. textContent deliberately omits icons/HTML and preserves the
  // language selected in the page dropdown.
  const listen = document.createElement('button');
  listen.type = 'button';
  listen.className = 'listen-button compact result-speak';
  listen.textContent = `🔊 ${tr('listen_label_compact')}`;
  listen.addEventListener('click', () => speakText(b.textContent));
  b.appendChild(listen);
  b.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
};

// Backend error messages we know how to translate client-side even if the
// backend itself hasn't localised them yet. Falls back to the raw message
// (or a generic one) if nothing matches.
const SERVER_MESSAGE_MAP = [
  { match: /no verified mandi quote/i, key: 'no_mandi_quote' },
  { match: /select the crop before checking/i, key: 'disease_choose_crop_first' },
  { match: /clear,\s*close,\s*well-?lit photo/i, key: 'photo_quality_reject' }
];
function localizeServerMessage(raw) {
  if (!raw) return tr('generic_error');
  const hit = SERVER_MESSAGE_MAP.find(m => m.match.test(raw));
  return hit ? tr(hit.key) : raw;
}
const errorOf = async r => {
  const detail = (await r.json().catch(() => ({}))).detail;
  return localizeServerMessage(detail);
};

const language = $('#language');

// Browser text-to-speech is used for instructions and every web result.
function speakText(text) {
  if (!('speechSynthesis' in window)) return alert(tr('speech_unsupported'));
  const u = new SpeechSynthesisUtterance(text);
  u.lang = `${language.value}-IN`;
  u.rate = 0.88;
  u.onerror = () => alert(tr('speech_failed'));
  speechSynthesis.cancel();
  speechSynthesis.resume();
  // Chrome sometimes needs a short tick after cancel/resume before it will speak.
  setTimeout(() => { speechSynthesis.resume(); speechSynthesis.speak(u); }, 100);
}

document.querySelectorAll('[data-speak-key]').forEach(b => b.addEventListener('click', () => {
  const key = b.dataset.speakKey === 'welcome' ? 'spoken_welcome' : 'spoken_safety';
  speakText(tr(key));
}));

const choose = (s, id, key) => document.querySelectorAll(s).forEach(b => b.addEventListener('click', () => {
  document.querySelectorAll(s).forEach(x => x.classList.remove('active'));
  b.classList.add('active');
  document.getElementById(id).value = b.dataset[key];
}));
// Only the disease-form crop chips are wired here — the market-form chips
// are re-rendered on every language change and are handled via delegation
// inside i18n.js instead.
choose('.crop-chip', 'selected-crop', 'crop');

const leaf = $('input[name="image"]');
leaf.addEventListener('change', () => {
  $('#file-name').textContent = leaf.files[0]?.name || tr('choose_leaf_photo');
});

$('#disease-form').addEventListener('submit', async e => {
  e.preventDefault();
  const f = e.currentTarget, b = f.querySelector('.primary-action');
  if (!leaf.files.length) return show('disease-result', tr('disease_choose_photo_first'), true);
  b.disabled = true;
  b.textContent = tr('disease_checking');
  try {
    const r = await fetch('/api/disease/analyze', { method: 'POST', body: new FormData(f) });
    if (!r.ok) throw Error(await errorOf(r));
    const { result, disclaimer } = await r.json();
    show('disease-result', `
      <h3>🌿 ${result.disease_name}</h3>
      <p><strong>${tr('disease_crop_label')}</strong> ${result.crop_guess || '—'} · <strong>${tr('disease_confidence_label')}</strong> ${(result.confidence * 100).toFixed(0)}%</p>
      <p><strong>${tr('disease_remedy_label')}</strong> ${result.remedy}</p>
      <p class="disclaimer">⚠️ ${disclaimer}</p>`);
  } catch (x) {
    show('disease-result', x.message, true);
  } finally {
    b.disabled = false;
    b.innerHTML = `${tr('btn_check_photo')} <span>→</span>`;
  }
});

$('#market-form').addEventListener('submit', async e => {
  e.preventDefault();
  const f = e.currentTarget, b = f.querySelector('.primary-action'), d = new FormData(f);
  if (!d.get('commodity')) return show('market-result', tr('market_choose_crop_first'), true);
  if (!d.get('state')) return show('market-result', tr('market_choose_state_first'), true);
  b.disabled = true;
  b.textContent = tr('market_finding');
  const q = new URLSearchParams(Object.fromEntries([...d].filter(([, v]) => v))).toString();
  try {
    const r = await fetch(`/api/market/price?${q}`);
    if (!r.ok) throw Error(await errorOf(r));
    const { result } = await r.json();
    show('market-result', `
      <h3>📊 ${result.commodity} · ${result.mandi}</h3>
      <p>${result.state} · ${result.price_date}${result.variety ? ` · ${result.variety}` : ''}</p>
      <div class="price-grid">
        <div>${tr('market_min')}<strong>₹${result.min_price_per_quintal}</strong></div>
        <div>${tr('market_modal')}<strong>₹${result.modal_price_per_quintal}</strong></div>
        <div>${tr('market_max')}<strong>₹${result.max_price_per_quintal}</strong></div>
      </div>
      <p class="disclaimer">${tr('market_wholesale_source')} ${result.source}</p>`);
  } catch (x) {
    show('market-result', x.message, true);
  } finally {
    b.disabled = false;
    b.innerHTML = `${tr('btn_see_price')} <span>→</span>`;
  }
});

const advisoryForm = $('#advisory-form');
$('#use-location').addEventListener('click', () => {
  if (!navigator.geolocation) return show('advisory-result', 'Location is not available in this browser.', true);
  navigator.geolocation.getCurrentPosition(position => {
    advisoryForm.elements.latitude.value = position.coords.latitude.toFixed(5);
    advisoryForm.elements.longitude.value = position.coords.longitude.toFixed(5);
    $('#use-location').textContent = '✓ खेत स्थान जोड़ा गया';
  }, () => show('advisory-result', 'Location permission was not given. You can still receive a soil-only advisory.', true), {timeout: 8000});
});
advisoryForm.addEventListener('submit', async e => {
  e.preventDefault(); const b = advisoryForm.querySelector('.primary-action'), q = new URLSearchParams(new FormData(advisoryForm));
  b.disabled = true; b.textContent = 'सलाह तैयार हो रही है…';
  try {
    const r = await fetch(`/api/advisory?${q}`); if (!r.ok) throw Error(await errorOf(r));
    const a = (await r.json()).result, w = a.weather;
    const weather = w.temperature_c == null ? 'स्थान नहीं दिया गया — केवल मिट्टी की सलाह' : `${w.temperature_c}°C · अगले 7 दिन बारिश ${w.rain_next_7_days_mm} mm`;
    show('advisory-result', `<h3>🧪 ${a.crop}: ${a.readiness_score}/100 तैयार</h3><p><strong>${a.sowing_status}</strong><br>मौसम: ${weather}</p><div class="price-grid"><div>N कमी<strong>${a.nutrient_gap_kg_per_ha.N} kg/ha</strong></div><div>P कमी<strong>${a.nutrient_gap_kg_per_ha.P} kg/ha</strong></div><div>K कमी<strong>${a.nutrient_gap_kg_per_ha.K} kg/ha</strong></div></div><p>${a.notes.map(n => `• ${n}`).join('<br>')}</p><p class="disclaimer">⚠️ ${a.disclaimer}</p>`);
  } catch (x) { show('advisory-result', x.message, true); }
  finally { b.disabled = false; b.innerHTML = 'फसल सलाह पाएं <span>→</span>'; }
});

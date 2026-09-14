const $ = s => document.querySelector(s);
const tr = k => (window.KM_I18N ? window.KM_I18N.t(k) : k);

// Native validation protects every action button, including legacy forms that
// deliberately use `novalidate` because their requests are submitted with JS.
document.addEventListener('submit', event => {
  const form = event.target;
  if (!(form instanceof HTMLFormElement) || form.checkValidity()) return;
  event.preventDefault();
  event.stopImmediatePropagation();
  form.reportValidity();
}, true);

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
const dataDeclaration = $('#data-declaration');
const declarationTitle = $('#declaration-title');
const declarationCopy = $('#declaration-copy');
const declarationLabel = $('#declaration-label');
const pilotConsent = $('#pilot-form input[name="consent_insights"]');
const renderDeclaration = () => {
  const hindi = language.value === 'hi';
  declarationTitle.textContent = hindi ? 'आपकी अनुमति, आपका नियंत्रण' : 'Your consent, your control';
  declarationCopy.textContent = hindi
    ? 'मैं सहमत हूँ कि मेरी जानकारी और संदेशों का उपयोग केवल गुमनाम तरीके से कृषिमित्र सेवा बेहतर बनाने के लिए किया जा सकता है।'
    : 'I agree that my information and messages may be used anonymously only to improve the KrishiMitr service.';
  declarationLabel.textContent = hindi ? 'मैं सहमत हूँ' : 'I agree';
};
try { dataDeclaration.checked = localStorage.getItem('km-data-declaration') === 'true'; } catch (_) { /* Privacy mode may block local storage. */ }
pilotConsent.checked = dataDeclaration.checked;
dataDeclaration.addEventListener('change', () => {
  pilotConsent.checked = dataDeclaration.checked;
  try { localStorage.setItem('km-data-declaration', String(dataDeclaration.checked)); } catch (_) { /* Consent still applies during this visit. */ }
});
pilotConsent.addEventListener('change', () => {
  dataDeclaration.checked = pilotConsent.checked;
  try { localStorage.setItem('km-data-declaration', String(dataDeclaration.checked)); } catch (_) { /* Consent still applies during this visit. */ }
});
renderDeclaration();
document.addEventListener('km:language-changed', renderDeclaration);
const localizeCropGuess = crop => {
  const value = String(crop || '').toLowerCase();
  const keys = {tomato: 'tomato', potato: 'potato', maize: 'maize', corn: 'maize', soybean: 'soybean', apple: 'apple', grape: 'grape', orange: 'orange', peach: 'peach', strawberry: 'strawberry', raspberry: 'raspberry', blueberry: 'blueberry', cherry: 'cherry', squash: 'squash', pepper: 'bell pepper'};
  const key = Object.entries(keys).find(([name]) => value.includes(name))?.[1];
  const cropItem = key && window.KM_I18N?.CROPS.find(item => item.key === key);
  return cropItem ? (cropItem[language.value] || cropItem.en) : crop;
};

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
  const keys = {welcome: 'spoken_welcome', safety: 'spoken_safety', photo: 'spoken_photo', marketplace: 'spoken_marketplace', advisory: 'spoken_advisory', pilot: 'spoken_pilot'};
  speakText(tr(keys[b.dataset.speakKey] || 'spoken_welcome'));
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

const galleryLeaf = $('#gallery-image');
let selectedLeafFile = null;
let previewUrl = null;
const selectLeafFile = file => {
  selectedLeafFile = file || null;
  $('#file-name').textContent = file ? `✓ ${file.name}` : tr('choose_leaf_photo');
  document.querySelector('.file-choice-card').classList.toggle('selected', !!file);
  const preview = $('#photo-preview');
  if (previewUrl) URL.revokeObjectURL(previewUrl);
  previewUrl = file ? URL.createObjectURL(file) : null;
  $('#leaf-preview-image').src = previewUrl || '';
  preview.classList.toggle('hidden', !file);
};
galleryLeaf.addEventListener('change', () => selectLeafFile(galleryLeaf.files[0]));
$('#change-photo').addEventListener('click', () => {
  galleryLeaf.value = ''; selectLeafFile(null); galleryLeaf.click();
});

$('#disease-form').addEventListener('submit', async e => {
  e.preventDefault();
  const f = e.currentTarget, b = f.querySelector('.primary-action');
  if (!selectedLeafFile) return show('disease-result', tr('disease_choose_photo_first'), true);
  b.disabled = true;
  b.textContent = tr('disease_checking');
  try {
    const payload = new FormData(f);
    payload.delete('image');
    payload.append('image', selectedLeafFile);
    const r = await fetch('/api/disease/analyze', { method: 'POST', body: payload });
    if (!r.ok) throw Error(await errorOf(r));
    const { result } = await r.json();
    show('disease-result', `
      <h3>🌿 ${result.disease_name}</h3>
      <p><strong>${tr('disease_crop_label')}</strong> ${localizeCropGuess(result.crop_guess) || '—'} · <strong>${tr('disease_confidence_label')}</strong> ${(result.confidence * 100).toFixed(0)}%</p>
      <p><strong>${tr('disease_remedy_label')}</strong> ${result.remedy}</p>
      <p class="disclaimer">⚠️ ${tr('disease_disclaimer')}</p>`);
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

$('#advisory-form').addEventListener('submit', async e => {
  e.preventDefault();
  const form = e.currentTarget, button = form.querySelector('.primary-action'), data = Object.fromEntries(new FormData(form));
  if (data.crop === '__other__') {
    const customCrop = String(data.custom_crop || '').trim();
    if (!customCrop) return show('advisory-result', language.value === 'hi' ? 'कृपया अपनी फसल का नाम लिखें।' : 'Please enter your crop name.', true);
    data.crop = customCrop;
  }
  delete data.custom_crop;
  button.disabled = true;
  try {
    const response = await fetch('/api/advisory/recommend', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(data)});
    if (!response.ok) throw Error(await errorOf(response));
    const {result} = await response.json();
    const crop = (window.KM_I18N?.CROPS || []).find(item => item.en.toLowerCase() === result.recommended_crop.toLowerCase());
    const cropName = crop ? (crop[language.value] || crop.en) : result.recommended_crop;
    const priority = result.priority === 'balanced' ? tr('advisory_balanced') : tr({nitrogen: 'advisory_n', phosphorus: 'advisory_p', potassium: 'advisory_k'}[result.priority]);
    const hindiSowingWindows = {"October to December": 'अक्टूबर से दिसंबर', "June to July": 'जून से जुलाई', "September to November": 'सितंबर से नवंबर'};
    const sowingWindow = language.value === 'hi' ? (hindiSowingWindows[result.sowing_window] || result.sowing_window) : result.sowing_window;
    show('advisory-result', `<h3>🌱 ${tr('advisory_recommended')}: ${cropName}</h3><p><strong>${tr('advisory_sowing')}:</strong> ${sowingWindow}</p><p><strong>${tr('advisory_priority')}:</strong> ${priority}</p><p>${tr(`advisory_answer_${result.answer_kind}`)}</p><p class="disclaimer">${result.fit === 'good' ? tr('advisory_good') : tr('advisory_check')}</p><p class="disclaimer">${tr('advisory_safety')}</p>`);
  } catch (error) { show('advisory-result', error.message, true); }
  finally { button.disabled = false; }
});

const advisoryForm = $('#advisory-form');
const advisoryCrop = $('#advisory-crop');
const advisoryOtherCrop = $('#advisory-other-crop');
const advisoryCustomCrop = advisoryOtherCrop.querySelector('input');
const renderAdvisoryCropChoices = () => {
  const hindi = language.value === 'hi';
  advisoryCrop.options[0].textContent = hindi ? 'फसल चुनें या AI से सुझाव लें' : 'Select a crop or get AI guidance';
  advisoryCrop.options[advisoryCrop.options.length - 1].textContent = hindi ? 'अन्य फसल लिखें' : 'Other crop (type name)';
  advisoryOtherCrop.querySelector('span').textContent = hindi ? 'अपनी फसल का नाम लिखें' : 'Enter your crop name';
  advisoryCustomCrop.placeholder = hindi ? 'जैसे: बाजरा' : 'e.g. Millet';
};
const toggleCustomCrop = () => {
  const other = advisoryCrop.value === '__other__';
  advisoryOtherCrop.classList.toggle('hidden', !other);
  advisoryCustomCrop.required = other;
  if (!other) advisoryCustomCrop.value = '';
};
advisoryCrop.addEventListener('change', toggleCustomCrop);
renderAdvisoryCropChoices();
document.addEventListener('km:language-changed', renderAdvisoryCropChoices);
const locationButton = document.createElement('button');
locationButton.type = 'button'; locationButton.id = 'use-location'; locationButton.className = 'location-button';
const locationStatus = document.createElement('p');
locationStatus.id = 'location-status'; locationStatus.className = 'location-status'; locationStatus.setAttribute('aria-live', 'polite');
const locationProfile = document.createElement('div');
locationProfile.className = 'location-profile-banner';
locationProfile.setAttribute('aria-live', 'polite');
const renderLocationCopy = () => {
  locationButton.innerHTML = `📍 <span>${tr('use_location')}</span>`;
  if (locationStatus.dataset.busy) return;
  const savedProfile = locationStatus.dataset.profile && JSON.parse(locationStatus.dataset.profile);
  if (savedProfile) {
    renderLocationProfile(savedProfile);
    locationStatus.textContent = language.value === 'hi'
      ? 'लोकेशन के अनुसार तापमान, बारिश और क्षेत्रीय मिट्टी प्रोफ़ाइल भरकर लॉक कर दी गई है।'
      : 'Weather and the regional soil profile have been filled and locked for this location.';
    return;
  }
  locationStatus.textContent = tr('location_help');
};
const renderLocationProfile = result => {
  if (!result) return;
  const hindi = language.value === 'hi';
  locationProfile.innerHTML = `<span class="profile-lock">🔒</span><div><strong>${hindi ? 'लोकेशन प्रोफ़ाइल लॉक है' : 'Location profile is locked'}</strong><small>${hindi ? `तापमान ${result.temperature}°C · बारिश ${result.rainfall} mm · N ${result.nitrogen} · P ${result.phosphorus} · K ${result.potassium} · pH ${result.ph}` : `Temperature ${result.temperature}°C · Rainfall ${result.rainfall} mm · N ${result.nitrogen} · P ${result.phosphorus} · K ${result.potassium} · pH ${result.ph}`}</small></div>`;
  locationProfile.classList.add('visible');
};
renderLocationCopy(); advisoryForm.prepend(locationProfile); advisoryForm.prepend(locationStatus); advisoryForm.prepend(locationButton);
document.addEventListener('km:language-changed', renderLocationCopy);
const locationFields = ['temperature', 'rainfall', 'nitrogen', 'phosphorus', 'potassium', 'ph'];
const setLocationValuesAndLock = result => {
  locationFields.forEach(name => {
    const field = advisoryForm.elements[name];
    if (!field || result[name] == null) return;
    field.value = result[name];
    field.readOnly = field.tagName === 'INPUT';
    field.dataset.locationLocked = 'true';
    field.setAttribute('aria-readonly', 'true');
    if (field.tagName === 'SELECT') {
      field.addEventListener('mousedown', event => event.preventDefault());
      field.addEventListener('keydown', event => event.preventDefault());
    }
  });
  advisoryForm.classList.add('location-profile-locked');
};
locationButton.addEventListener('click', () => {
  if (!navigator.geolocation) { locationStatus.textContent = tr('location_error'); return; }
  locationButton.disabled = true; locationStatus.dataset.busy = 'true'; locationStatus.textContent = tr('location_loading');
  const fetchWeather = async (latitude, longitude) => {
    try {
      const response = await fetch(`/api/advisory/weather?latitude=${encodeURIComponent(latitude)}&longitude=${encodeURIComponent(longitude)}`);
      if (response.ok) return (await response.json()).result;
    } catch (_) { /* Browser fallback below handles a temporarily unavailable backend route. */ }
    const direct = await fetch(`https://api.open-meteo.com/v1/forecast?latitude=${encodeURIComponent(latitude)}&longitude=${encodeURIComponent(longitude)}&current=temperature_2m&daily=precipitation_sum&forecast_days=1&timezone=auto`);
    if (!direct.ok) throw Error('weather unavailable');
    const data = await direct.json();
    const soil = latitude >= 27 && longitude >= 68 && longitude <= 80 ? {nitrogen: 75, phosphorus: 45, potassium: 35, ph: 7.0}
      : latitude < 19 ? {nitrogen: 70, phosphorus: 40, potassium: 45, ph: 6.5}
      : longitude >= 78 ? {nitrogen: 65, phosphorus: 40, potassium: 40, ph: 6.4}
      : {nitrogen: 60, phosphorus: 40, potassium: 35, ph: 6.5};
    return {temperature: data.current.temperature_2m, rainfall: data.daily.precipitation_sum[0], ...soil};
  };
  navigator.geolocation.getCurrentPosition(async position => {
    try {
      const {latitude, longitude} = position.coords;
      const result = await fetchWeather(latitude, longitude);
      setLocationValuesAndLock(result);
      locationStatus.dataset.profile = JSON.stringify(result);
      renderLocationProfile(result);
      locationStatus.textContent = language.value === 'hi'
        ? 'लोकेशन के अनुसार तापमान, बारिश और क्षेत्रीय मिट्टी प्रोफ़ाइल भरकर लॉक कर दी गई है।'
        : 'Weather and the regional soil profile have been filled and locked for this location.';
    } catch (_) { locationStatus.textContent = tr('location_error'); }
    finally { locationButton.disabled = false; delete locationStatus.dataset.busy; }
  }, error => {
    const key = error.code === 1 ? 'location_permission_error' : error.code === 2 ? 'location_unavailable_error' : error.code === 3 ? 'location_timeout_error' : 'location_error';
    locationStatus.textContent = tr(key); locationButton.disabled = false; delete locationStatus.dataset.busy;
  }, {enableHighAccuracy: true, timeout: 20000, maximumAge: 0});
});

$('#pilot-form').addEventListener('submit', async e => {
  e.preventDefault();
  const f = e.currentTarget, d = new FormData(f), b = f.querySelector('.primary-action');
  const identifier = String(d.get('identifier') || '').trim();
  if (identifier.length < 3) return show('pilot-result', tr('pilot_identifier_error'), true);
  b.disabled = true;
  try {
    const profile = {identifier, state: String(d.get('state') || '').trim() || null,
      district: String(d.get('district') || '').trim() || null, preferred_language: language.value,
      consent_insights: d.get('consent_insights') === 'on'};
    const saved = await fetch('/api/farmers/profile', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(profile)});
    if (!saved.ok) throw Error(await errorOf(saved));
    const plan = await fetch('/api/plans/request', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({identifier, plan: 'personalized_advisory'})});
    if (!plan.ok) throw Error(await errorOf(plan));
    show('pilot-result', tr('pilot_success'));
    f.reset();
  } catch (x) { show('pilot-result', x.message, true); }
  finally { b.disabled = false; }
});

const marketplaceDate = document.getElementById('marketplace-date');
if (marketplaceDate) {
  const today = new Date().toISOString().slice(0, 10);
  const refreshMarketplaceLanguage = () => {
    const selling = document.querySelector('.trade-tab.active')?.dataset.tradeMode === 'sell';
    marketplaceDate.textContent = new Intl.DateTimeFormat(language.value === 'hi' ? 'hi-IN' : 'en-IN', { day: 'numeric', month: 'long', year: 'numeric' }).format(new Date());
    document.getElementById('bid-mode-label').textContent = tr(selling ? 'marketplace_selling_for' : 'marketplace_buying_for');
    document.getElementById('bid-help').textContent = tr(selling ? 'marketplace_sell_help' : 'marketplace_buy_help');
    document.getElementById('bid-button-label').textContent = tr(selling ? 'marketplace_sell_bid' : 'marketplace_buy_bid');
  };
  refreshMarketplaceLanguage();
  document.addEventListener('km:language-changed', refreshMarketplaceLanguage);
  document.getElementById('bid-date').value = today;
  const cropFilter = document.getElementById('crop-filter');
  const priceFilter = document.getElementById('price-filter');
  const stateFilter = document.getElementById('state-filter');
  const varietyFilter = document.getElementById('variety-filter');
  const demoNote = document.createElement('p');
  demoNote.className = 'marketplace-demo-note';
  demoNote.dataset.i18n = 'marketplace_demo_note';
  demoNote.textContent = tr('marketplace_demo_note');
  document.querySelector('.market-filters').insertAdjacentElement('afterend', demoNote);
  document.addEventListener('km:language-changed', () => { demoNote.textContent = tr('marketplace_demo_note'); });
  const enhanceMultiSelect = select => {
    const existing = select.parentElement.querySelector('.multi-dropdown');
    if (existing) existing.remove();
    const box = document.createElement('details');
    box.className = 'multi-dropdown';
    const summary = document.createElement('summary');
    const list = document.createElement('div');
    box.append(summary, list);
    [...select.options].forEach(option => {
      const row = document.createElement('label');
      const check = document.createElement('input');
      check.type = 'checkbox'; check.value = option.value; check.checked = option.selected;
      check.addEventListener('change', () => {
        if (check.value === 'all' && check.checked) [...list.querySelectorAll('input')].forEach(input => { if (input !== check) input.checked = false; });
        if (check.value !== 'all' && check.checked) list.querySelector('input[value="all"]').checked = false;
        [...select.options].forEach(item => { item.selected = !!list.querySelector(`input[value="${item.value}"]`).checked; });
        const chosen = [...select.selectedOptions].map(item => item.textContent);
        summary.textContent = chosen.length === 0 ? tr('filter_choose') : chosen.length === 1 ? chosen[0] : `${chosen.length} ${tr('filter_selected')}`;
        select.dispatchEvent(new Event('change'));
        box.open = false;
      });
      row.append(check, document.createTextNode(option.textContent)); list.append(row);
    });
    const chosen = [...select.selectedOptions].map(item => item.textContent);
    summary.textContent = chosen.length === 1 ? chosen[0] : tr('filter_choose');
    select.insertAdjacentElement('afterend', box);
    box.addEventListener('toggle', () => {
      if (box.open) document.querySelectorAll('.multi-dropdown[open]').forEach(other => { if (other !== box) other.open = false; });
    });
  };
  enhanceMultiSelect(cropFilter);
  enhanceMultiSelect(stateFilter);
  document.addEventListener('km:language-changed', () => { enhanceMultiSelect(cropFilter); enhanceMultiSelect(stateFilter); });
  const updateListings = () => {
    const mode = document.querySelector('.trade-tab.active').dataset.tradeMode;
    const crops = [...cropFilter.selectedOptions].map(option => option.value),
      states = [...stateFilter.selectedOptions].map(option => option.value), priceType = priceFilter.value,
      variety = varietyFilter.value;
    let count = 0;
    document.querySelectorAll('.crop-listing').forEach(card => {
      const cardState = card.dataset.state || ({ 'गेहूँ': 'haryana', 'मक्का': 'madhya-pradesh' }[card.dataset.crop] || 'maharashtra');
      const cardVariety = card.dataset.variety || ({ 'गेहूँ': 'grade-a', 'मक्का': 'organic' }[card.dataset.crop] || 'hybrid');
      const visible = card.dataset.mode === mode && (crops.includes('all') || crops.length === 0 || crops.includes(card.dataset.crop)) &&
        (priceType === 'all' || card.dataset.type === priceType) && (states.includes('all') || states.length === 0 || states.includes(cardState)) &&
        (variety === 'all' || cardVariety === variety);
      card.classList.toggle('hidden', !visible);
      if (visible) count += 1;
    });
    document.getElementById('filter-empty').classList.toggle('hidden', count > 0);
    document.getElementById('listing-title').textContent = tr(mode === 'buy' ? 'marketplace_buy_listings' : 'marketplace_sell_listings');
  };
  cropFilter.addEventListener('change', updateListings);
  priceFilter.addEventListener('change', updateListings);
  stateFilter.addEventListener('change', updateListings);
  varietyFilter.addEventListener('change', updateListings);
  document.addEventListener('km:language-changed', updateListings);
  updateListings();
  const renderSavedBids = async () => {
    try {
      const mode = document.querySelector('.trade-tab.active').dataset.tradeMode;
      const response = await fetch(`/api/marketplace/bids?trade_type=${mode}`);
      if (!response.ok) return;
      const {bids} = await response.json();
      const grid = document.querySelector('.listing-grid');
      grid.querySelectorAll('.saved-bid').forEach(card => card.remove());
      for (const bid of bids) {
        const card = document.createElement('article');
        card.className = 'crop-listing saved-bid'; card.dataset.mode = bid.trade_type; card.dataset.crop = bid.crop;
        card.dataset.price = bid.price; card.dataset.type = 'bid'; card.dataset.state = 'all'; card.dataset.variety = 'all';
        const mapLink = bid.latitude != null && bid.longitude != null ? `https://www.openstreetmap.org/?mlat=${bid.latitude}&mlon=${bid.longitude}#map=15/${bid.latitude}/${bid.longitude}` : '';
        card.innerHTML = `<span class="crop-art">${bid.trade_type === 'buy' ? '🛒' : '🌾'}</span><div><h4></h4><p></p><small></small></div><div class="listing-price"><em>LIVE BID</em><strong></strong><span>₹ / quintal</span></div>`;
        card.querySelector('h4').textContent = bid.crop;
        card.querySelector('p').textContent = `${bid.trade_type === 'buy' ? 'Buyer needs' : 'For sale'} · ${bid.quantity} quintals`;
        let locationLabel = bid.location_label;
        if (bid.latitude != null && bid.longitude != null) {
          try {
            const locationResponse = await fetch(`/api/location/reverse?latitude=${encodeURIComponent(bid.latitude)}&longitude=${encodeURIComponent(bid.longitude)}&language=${encodeURIComponent(language.value)}`);
            if (locationResponse.ok) locationLabel = (await locationResponse.json()).location_label;
          } catch (_) { /* Existing readable label remains as fallback. */ }
        }
        card.querySelector('small').innerHTML = mapLink ? `📍 <a href="${mapLink}" target="_blank" rel="noopener">${locationLabel} · View map</a>` : `📍 ${locationLabel}`;
        card.querySelector('strong').textContent = `₹${Number(bid.price).toLocaleString('en-IN')}`;
        grid.prepend(card);
      }
      updateListings();
    } catch (_) { /* Bid list can still show seeded demo cards if API is unreachable. */ }
  };
  renderSavedBids();
  document.addEventListener('km:language-changed', renderSavedBids);
  let bidCoordinates = null;
  const locateBid = document.createElement('button');
  locateBid.type = 'button'; locateBid.className = 'bid-locate';
  const refreshBidLocationCopy = () => { if (!locateBid.dataset.state) locateBid.textContent = `📍 ${tr('use_location')}`; };
  refreshBidLocationCopy(); document.addEventListener('km:language-changed', refreshBidLocationCopy);
  const bidLocationInput = document.getElementById('bid-form').elements.location;
  bidLocationInput.insertAdjacentElement('afterend', locateBid);
  locateBid.addEventListener('click', async () => navigator.geolocation?.getCurrentPosition(async position => {
    bidCoordinates = position.coords;
    locateBid.disabled = true; locateBid.dataset.state = 'loading'; locateBid.textContent = `📍 ${tr('bid_location_loading')}`;
    try {
      const response = await fetch(`/api/location/reverse?latitude=${encodeURIComponent(position.coords.latitude)}&longitude=${encodeURIComponent(position.coords.longitude)}&language=${encodeURIComponent(language.value)}`);
      if (response.ok) {
        bidLocationInput.value = (await response.json()).location_label;
      } else {
        const direct = await fetch(`https://nominatim.openstreetmap.org/reverse?format=jsonv2&zoom=18&lat=${encodeURIComponent(position.coords.latitude)}&lon=${encodeURIComponent(position.coords.longitude)}`, {headers: {'Accept-Language': language.value === 'hi' ? 'hi,en' : 'en'}});
        if (!direct.ok) throw Error();
        const place = await direct.json();
        const address = place.address || {};
        const parts = [address.house_number, address.road, address.neighbourhood, address.suburb, address.city || address.town || address.village, address.state].filter(Boolean);
        if (!parts.length) throw Error();
        bidLocationInput.value = [...new Set(parts)].join(', ');
      }
      locateBid.textContent = `✓ ${tr('bid_location_success')}`;
    } catch (_) { bidLocationInput.value = tr('bid_location_fallback'); locateBid.textContent = `✓ ${tr('bid_location_fallback')}`; }
    finally { locateBid.disabled = false; locateBid.dataset.state = ''; }
  }, () => { locateBid.textContent = tr('bid_location_unavailable'); locateBid.dataset.state = ''; }, {enableHighAccuracy: true, timeout: 15000}));
  document.querySelectorAll('.trade-tab').forEach(tab => tab.addEventListener('click', () => {
    const selling = tab.dataset.tradeMode === 'sell';
    document.querySelectorAll('.trade-tab').forEach(x => { x.classList.toggle('active', x === tab); x.setAttribute('aria-selected', x === tab ? 'true' : 'false'); });
    refreshMarketplaceLanguage();
    updateListings();
    renderSavedBids();
  }));
  document.querySelectorAll('.crop-listing').forEach(card => card.addEventListener('click', () => {
    document.querySelectorAll('.crop-listing').forEach(x => x.classList.toggle('selected', x === card));
    document.getElementById('bid-crop').value = card.dataset.crop;
    document.getElementById('bid-price').value = card.dataset.price;
  }));
  document.getElementById('bid-form').addEventListener('submit', async e => {
    e.preventDefault(); const form = e.currentTarget;
    if (!form.reportValidity()) return;
    const trade = document.querySelector('.trade-tab.active').dataset.tradeMode === 'sell' ? tr('marketplace_sell_trade') : tr('marketplace_buy_trade');
    const data = new FormData(form), result = document.getElementById('bid-result');
    try {
      const response = await fetch('/api/marketplace/bids', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({trade_type: document.querySelector('.trade-tab.active').dataset.tradeMode, crop: data.get('crop'), quantity: Number(data.get('quantity')), price: Number(data.get('price')), location_label: data.get('location'), bid_date: data.get('bid_date'), latitude: bidCoordinates?.latitude ?? null, longitude: bidCoordinates?.longitude ?? null})});
      if (!response.ok) throw Error(await errorOf(response));
      result.textContent = tr('marketplace_bid_success').replace('{crop}', data.get('crop')).replace('{trade}', trade).replace('{price}', Number(data.get('price')).toLocaleString('en-IN')).replace('{date}', data.get('bid_date'));
      result.classList.remove('hidden');
      await renderSavedBids();
    } catch (error) { result.textContent = error.message || tr('generic_error'); result.classList.remove('hidden'); }
  });
}

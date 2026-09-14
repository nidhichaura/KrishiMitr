/* ============================================================
   KrishiMitr — Localisation (Hindi, English + Punjabi)
   Single source of truth: every visible string, crop label and
   state name lives here so the WHOLE page switches together.
   ============================================================ */

/* Canonical crop list. `key` is the value sent to the backend API
   and never changes; hi/en are only the DISPLAY labels. */
const CROPS = [
  { key: 'wheat',        icon: '🌾', hi: 'गेहूं',    en: 'Wheat' },
  { key: 'rice',         icon: '🍚', hi: 'धान',     en: 'Rice' },
  { key: 'cotton',       icon: '☁️', hi: 'कपास',    en: 'Cotton' },
  { key: 'onion',        icon: '🧅', hi: 'प्याज',    en: 'Onion' },
  { key: 'tomato',       icon: '🍅', hi: 'टमाटर',   en: 'Tomato' },
  { key: 'potato',       icon: '🥔', hi: 'आलू',     en: 'Potato' },
  { key: 'soybean',      icon: '🫘', hi: 'सोयाबीन', en: 'Soybean' },
  { key: 'sugarcane',    icon: '🎋', hi: 'गन्ना',    en: 'Sugarcane' },
  { key: 'maize',        icon: '🌽', hi: 'मक्का',    en: 'Maize' },
  { key: 'mustard',      icon: '🌼', hi: 'सरसों',    en: 'Mustard' },
  { key: 'banana',       icon: '🍌', hi: 'केला',     en: 'Banana' },
  { key: 'bhindi',       icon: '🥬', hi: 'भिंडी',    en: 'Okra' },
  { key: 'bottle gourd', icon: '🥒', hi: 'लौकी',     en: 'Bottle gourd' },
  { key: 'brinjal',      icon: '🍆', hi: 'बैंगन',    en: 'Brinjal' },
  { key: 'cauliflower',  icon: '🥦', hi: 'फूलगोभी', en: 'Cauliflower' },
  { key: 'cucumber',     icon: '🥒', hi: 'खीरा',     en: 'Cucumber' },
  { key: 'lemon',        icon: '🍋', hi: 'नींबू',    en: 'Lemon' },
  { key: 'papaya',       icon: '🍈', hi: 'पपीता',    en: 'Papaya' },
  { key: 'pumpkin',      icon: '🎃', hi: 'कद्दू',    en: 'Pumpkin' },
  { key: 'radish',       icon: '🥕', hi: 'मूली',     en: 'Radish' },
  { key: 'sponge gourd', icon: '🥒', hi: 'तोरी',     en: 'Sponge gourd' },
  { key: 'apple',        icon: '🍎', hi: 'सेब',      en: 'Apple' },
  { key: 'grape',        icon: '🍇', hi: 'अंगूर',    en: 'Grape' },
  { key: 'orange',       icon: '🍊', hi: 'संतरा',    en: 'Orange' }
];

/* `key` (English name) is what's sent to the backend as the state value;
   hi/en are only the DISPLAY labels shown in the dropdown. */
const STATES = [
  ['Andhra Pradesh', 'आंध्र प्रदेश'], ['Arunachal Pradesh', 'अरुणाचल प्रदेश'],
  ['Assam', 'असम'], ['Bihar', 'बिहार'], ['Chhattisgarh', 'छत्तीसगढ़'],
  ['Goa', 'गोवा'], ['Gujarat', 'गुजरात'], ['Haryana', 'हरियाणा'],
  ['Himachal Pradesh', 'हिमाचल प्रदेश'], ['Jharkhand', 'झारखंड'],
  ['Karnataka', 'कर्नाटक'], ['Kerala', 'केरल'], ['Madhya Pradesh', 'मध्य प्रदेश'],
  ['Maharashtra', 'महाराष्ट्र'], ['Manipur', 'मणिपुर'], ['Meghalaya', 'मेघालय'],
  ['Mizoram', 'मिजोरम'], ['Nagaland', 'नागालैंड'], ['Odisha', 'ओडिशा'],
  ['Punjab', 'पंजाब'], ['Rajasthan', 'राजस्थान'], ['Sikkim', 'सिक्किम'],
  ['Tamil Nadu', 'तमिलनाडु'], ['Telangana', 'तेलंगाना'], ['Tripura', 'त्रिपुरा'],
  ['Uttar Pradesh', 'उत्तर प्रदेश'], ['Uttarakhand', 'उत्तराखंड'],
  ['West Bengal', 'पश्चिम बंगाल'],
  ['Andaman and Nicobar Islands', 'अंडमान और निकोबार द्वीपसमूह'],
  ['Chandigarh', 'चंडीगढ़'],
  ['Dadra and Nagar Haveli and Daman and Diu', 'दादरा और नगर हवेली और दमन और दीव'],
  ['Delhi', 'दिल्ली'], ['Jammu and Kashmir', 'जम्मू और कश्मीर'],
  ['Ladakh', 'लद्दाख'], ['Lakshadweep', 'लक्षद्वीप'], ['Puducherry', 'पुदुचेरी']
].map(([en, hi]) => ({ key: en, en, hi }));

// Punjabi labels are added separately so canonical API values never change.
// Missing regional names intentionally fall back to English instead of
// rendering an empty option.
const PUNJABI_CROPS = {
  wheat: 'ਕਣਕ', rice: 'ਝੋਨਾ', cotton: 'ਕਪਾਹ', onion: 'ਪਿਆਜ਼', tomato: 'ਟਮਾਟਰ',
  potato: 'ਆਲੂ', soybean: 'ਸੋਇਆਬੀਨ', sugarcane: 'ਗੰਨਾ', maize: 'ਮੱਕੀ',
  mustard: 'ਸਰ੍ਹੋਂ', banana: 'ਕੇਲਾ', bhindi: 'ਭਿੰਡੀ', 'bottle gourd': 'ਘੀਆ',
  brinjal: 'ਬੈਂਗਣ', cauliflower: 'ਫੁੱਲਗੋਭੀ', cucumber: 'ਖੀਰਾ', lemon: 'ਨਿੰਬੂ',
  papaya: 'ਪਪੀਤਾ', pumpkin: 'ਕੱਦੂ', radish: 'ਮੂਲੀ', 'sponge gourd': 'ਤੋਰੀ',
  apple: 'ਸੇਬ', grape: 'ਅੰਗੂਰ', orange: 'ਸੰਤਰਾ'
};
const PUNJABI_STATES = { Punjab: 'ਪੰਜਾਬ', Haryana: 'ਹਰਿਆਣਾ', Rajasthan: 'ਰਾਜਸਥਾਨ',
  'Himachal Pradesh': 'ਹਿਮਾਚਲ ਪ੍ਰਦੇਸ਼', Chandigarh: 'ਚੰਡੀਗੜ੍ਹ', Delhi: 'ਦਿੱਲੀ',
  'Uttar Pradesh': 'ਉੱਤਰ ਪ੍ਰਦੇਸ਼', Uttarakhand: 'ਉੱਤਰਾਖੰਡ', 'Jammu and Kashmir': 'ਜੰਮੂ ਅਤੇ ਕਸ਼ਮੀਰ' };
CROPS.forEach(crop => { crop.pa = PUNJABI_CROPS[crop.key] || crop.en; });
STATES.forEach(state => { state.pa = PUNJABI_STATES[state.key] || state.en; });

/* All static UI copy + dynamic-message copy, in one place. */
const STRINGS = {
  hi: {
    page_title: 'कृषिमित्र — किसान का साथी',
    lang_label: 'भाषा',
    aria_language_select: 'अपनी भाषा चुनें',
    aria_listen_instructions: 'निर्देश सुनें',
    listen_label: 'सुनें',
    eyebrow_welcome: 'आपका डिजिटल कृषि साथी',
    h1_welcome: 'नमस्ते किसान भाई / बहन! 👋',
    p_welcome: 'नीचे एक बटन दबाइए। बाकी काम कृषिमित्र आसान भाषा में बताएगा।',
    aria_choice_grid: 'मुख्य सेवाएं',
    choice_photo_title: 'पत्ते की फोटो लें',
    choice_photo_desc: 'बीमारी की शुरुआती जांच',
    choice_photo_cta: 'फोटो लें →',
    choice_price_title: 'आज का मंडी भाव',
    choice_price_desc: 'सरकारी स्रोत से थोक मूल्य',
    choice_price_cta: 'भाव देखें →',
    eyebrow_steps: 'बस तीन कदम',
    h2_disease: 'पत्ते की फोटो से जांच',
    step1: 'अच्छी रोशनी में एक पत्ते की फोटो लें',
    step2: 'पत्ता फोटो के बीच में और साफ दिखना चाहिए',
    step3: 'स्क्रीनशॉट या इंटरनेट फोटो न भेजें',
    legend_crop_optional: 'पहले फसल चुनें',
    legend_crop_optional_small: '(रोग जांच के लिए जरूरी)',
    aria_crop_group: 'फसल चुनें',
    camera_open: 'कैमरा / गैलरी खोलें',
    choose_leaf_photo: 'एक साफ पत्ते की फोटो चुनें',
    btn_check_photo: 'फोटो जांचें',
    eyebrow_price: 'आज का सही भाव',
    h2_price: 'मंडी भाव देखें',
    simple_note: 'पहले अपनी फसल और राज्य दबाएं। मंडी का नाम देना जरूरी नहीं है।',
    legend_crop: 'फसल चुनें',
    aria_market_crop_group: 'मंडी के लिए फसल चुनें',
    state_label: 'अपना राज्य चुनें',
    state_placeholder: 'राज्य चुनें',
    mandi_summary: 'मंडी का नाम पता है? (वैकल्पिक)',
    mandi_placeholder: 'जैसे Azadpur',
    btn_see_price: 'आज का भाव देखें',
    safety_label: 'ज़रूरी बात:',
    safety_text: 'यह शुरुआती AI जांच है। दवा की मात्रा या उपचार शुरू करने से पहले नज़दीकी कृषि विशेषज्ञ से सलाह लें।',
    listen_label_compact: 'सुनें',
    footer_tagline: 'तकनीक के साथ बेहतर खेती।',
    whatsapp_cta: 'WhatsApp पर बात करें ↗',

    speech_unsupported: 'आपके browser में सुनाने की सुविधा उपलब्ध नहीं है।',
    speech_failed: 'ऑडियो नहीं चल पाया। कृपया speaker का volume जांचें और पेज रीफ्रेश करके फिर दबाएं।',
    generic_error: 'कुछ तकनीकी समस्या हुई। कृपया फिर कोशिश करें।',
    disease_choose_photo_first: 'पहले कैमरा / गैलरी से पत्ते की फोटो चुनें।',
    disease_choose_crop_first: 'रोग जांच से पहले अपनी फसल चुनें।',
    disease_checking: 'जांच हो रही है…',
    disease_crop_label: 'फसल:',
    disease_confidence_label: 'भरोसा:',
    disease_remedy_label: 'क्या करें:',
    market_choose_crop_first: 'पहले ऊपर से अपनी फसल दबाएं।',
    market_choose_state_first: 'कृपया अपना राज्य चुनें।',
    market_finding: 'भाव खोज रहे हैं…',
    market_min: 'न्यूनतम',
    market_modal: 'मोडल भाव',
    market_max: 'अधिकतम',
    market_wholesale_source: 'थोक भाव प्रति क्विंटल · स्रोत:',
    whatsapp_not_configured: 'WhatsApp सेवा का नंबर अभी जोड़ा नहीं गया है। कृपया कृषिमित्र वेबसाइट पर फोटो जांचें या आयोजक से WhatsApp नंबर पूछें।',
    no_mandi_quote: 'अभी इस फसल और राज्य के लिए सत्यापित मंडी भाव उपलब्ध नहीं है।',
    photo_quality_reject: 'कृपया पत्ते की एक साफ, नज़दीक से ली गई और अच्छी रोशनी वाली फोटो अपलोड करें।',

    spoken_welcome: 'नमस्ते। कृषिमित्र में आपका स्वागत है। पत्ते की फोटो से बीमारी देखें, या मंडी का भाव जानें।',
    spoken_safety: 'यह शुरुआती ए आई जांच है। दवा देने से पहले नजदीकी कृषि विशेषज्ञ से सलाह लें।'
  },
  en: {
    page_title: "KrishiMitr — Farmer's Companion",
    lang_label: 'Language',
    aria_language_select: 'Select your language',
    aria_listen_instructions: 'Listen to instructions',
    listen_label: 'Listen',
    eyebrow_welcome: 'Your digital farming companion',
    h1_welcome: 'Hello dear farmer! 👋',
    p_welcome: "Tap a button below. KrishiMitr will guide you the rest of the way in simple language.",
    aria_choice_grid: 'Main services',
    choice_photo_title: 'Take a leaf photo',
    choice_photo_desc: 'Initial disease screening',
    choice_photo_cta: 'Take photo →',
    choice_price_title: "Today's mandi price",
    choice_price_desc: 'Wholesale price from a government source',
    choice_price_cta: 'See price →',
    eyebrow_steps: 'Just three steps',
    h2_disease: 'Check using a leaf photo',
    step1: 'Take a leaf photo in good light',
    step2: 'The leaf should be clear and centred in the photo',
    step3: "Don't send screenshots or photos from the internet",
    legend_crop_optional: 'First choose your crop',
    legend_crop_optional_small: '(required for disease screening)',
    aria_crop_group: 'Choose crop',
    camera_open: 'Open camera / gallery',
    choose_leaf_photo: 'Choose a clear leaf photo',
    btn_check_photo: 'Check photo',
    eyebrow_price: "Today's accurate price",
    h2_price: 'See mandi price',
    simple_note: 'First select your crop and state. Giving the mandi name is optional.',
    legend_crop: 'Choose crop',
    aria_market_crop_group: 'Choose crop for mandi price',
    state_label: 'Choose your state',
    state_placeholder: 'Select state',
    mandi_summary: 'Know the mandi name? (optional)',
    mandi_placeholder: 'e.g. Azadpur',
    btn_see_price: "See today's price",
    safety_label: 'Important:',
    safety_text: 'This is only an initial AI check. Consult a local agriculture expert before starting any treatment or dosage.',
    listen_label_compact: 'Listen',
    footer_tagline: 'Better farming with technology.',
    whatsapp_cta: 'Chat on WhatsApp ↗',

    speech_unsupported: 'Your browser does not support the read-aloud feature.',
    speech_failed: 'Audio could not play. Please check your speaker volume and try again after refreshing the page.',
    generic_error: 'Something went wrong. Please try again.',
    disease_choose_photo_first: 'Please choose a leaf photo from camera/gallery first.',
    disease_choose_crop_first: 'Please choose your crop before disease screening.',
    disease_checking: 'Checking…',
    disease_crop_label: 'Crop:',
    disease_confidence_label: 'Confidence:',
    disease_remedy_label: 'What to do:',
    market_choose_crop_first: 'Please select your crop above first.',
    market_choose_state_first: 'Please choose your state.',
    market_finding: 'Finding price…',
    market_min: 'Min',
    market_modal: 'Modal price',
    market_max: 'Max',
    market_wholesale_source: 'Wholesale price per quintal · Source:',
    whatsapp_not_configured: "The WhatsApp number hasn't been set up yet. Please check on the KrishiMitr website, or ask the organiser for the WhatsApp number.",
    no_mandi_quote: 'No verified mandi quote is available for this crop and state right now.',
    photo_quality_reject: 'Please upload one clear, close, well-lit photo of a leaf.',

    spoken_welcome: "Welcome to KrishiMitr. Check a leaf photo for disease, or find today's mandi price.",
    spoken_safety: 'This is an initial AI screening. Consult a local agricultural expert before giving any treatment.'
  }
};

STRINGS.pa = {
  ...STRINGS.en,
  page_title: 'ਕ੍ਰਿਸ਼ੀਮਿੱਤਰ — ਕਿਸਾਨ ਦਾ ਸਾਥੀ', lang_label: 'ਭਾਸ਼ਾ',
  aria_language_select: 'ਆਪਣੀ ਭਾਸ਼ਾ ਚੁਣੋ', aria_listen_instructions: 'ਹਦਾਇਤਾਂ ਸੁਣੋ',
  listen_label: 'ਸੁਣੋ', eyebrow_welcome: 'ਤੁਹਾਡਾ ਡਿਜ਼ੀਟਲ ਖੇਤੀ ਸਾਥੀ',
  h1_welcome: 'ਸਤ ਸ੍ਰੀ ਅਕਾਲ ਕਿਸਾਨ ਵੀਰੋ / ਭੈਣੋ! 👋',
  p_welcome: 'ਹੇਠਾਂ ਇੱਕ ਬਟਨ ਦਬਾਓ। ਕ੍ਰਿਸ਼ੀਮਿੱਤਰ ਤੁਹਾਡੀ ਸਧਾਰਨ ਭਾਸ਼ਾ ਵਿੱਚ ਮਦਦ ਕਰੇਗਾ।',
  aria_choice_grid: 'ਮੁੱਖ ਸੇਵਾਵਾਂ', choice_photo_title: 'ਪੱਤੇ ਦੀ ਫੋਟੋ ਲਓ',
  choice_photo_desc: 'ਬਿਮਾਰੀ ਦੀ ਸ਼ੁਰੂਆਤੀ ਜਾਂਚ', choice_photo_cta: 'ਫੋਟੋ ਲਓ →',
  choice_price_title: 'ਅੱਜ ਦਾ ਮੰਡੀ ਭਾਅ', choice_price_desc: 'ਸਰਕਾਰੀ ਸਰੋਤ ਤੋਂ ਥੋਕ ਮੁੱਲ',
  choice_price_cta: 'ਭਾਅ ਵੇਖੋ →', eyebrow_steps: 'ਸਿਰਫ਼ ਤਿੰਨ ਕਦਮ',
  h2_disease: 'ਪੱਤੇ ਦੀ ਫੋਟੋ ਨਾਲ ਜਾਂਚ', step1: 'ਚੰਗੀ ਰੌਸ਼ਨੀ ਵਿੱਚ ਇੱਕ ਪੱਤੇ ਦੀ ਫੋਟੋ ਲਓ',
  step2: 'ਪੱਤਾ ਸਾਫ਼ ਅਤੇ ਫੋਟੋ ਦੇ ਵਿਚਕਾਰ ਹੋਵੇ', step3: 'ਸਕ੍ਰੀਨਸ਼ਾਟ ਜਾਂ ਇੰਟਰਨੈੱਟ ਦੀ ਫੋਟੋ ਨਾ ਭੇਜੋ',
  legend_crop_optional: 'ਪਹਿਲਾਂ ਫ਼ਸਲ ਚੁਣੋ', legend_crop_optional_small: '(ਰੋਗ ਜਾਂਚ ਲਈ ਜ਼ਰੂਰੀ)',
  aria_crop_group: 'ਫ਼ਸਲ ਚੁਣੋ', camera_open: 'ਕੈਮਰਾ / ਗੈਲਰੀ ਖੋਲ੍ਹੋ',
  choose_leaf_photo: 'ਇੱਕ ਸਾਫ਼ ਪੱਤੇ ਦੀ ਫੋਟੋ ਚੁਣੋ', btn_check_photo: 'ਫੋਟੋ ਜਾਂਚੋ',
  eyebrow_price: 'ਅੱਜ ਦਾ ਸਹੀ ਭਾਅ', h2_price: 'ਮੰਡੀ ਭਾਅ ਵੇਖੋ',
  simple_note: 'ਪਹਿਲਾਂ ਆਪਣੀ ਫ਼ਸਲ ਅਤੇ ਰਾਜ ਚੁਣੋ। ਮੰਡੀ ਦਾ ਨਾਮ ਦੇਣਾ ਵਿਕਲਪਿਕ ਹੈ।',
  legend_crop: 'ਫ਼ਸਲ ਚੁਣੋ', aria_market_crop_group: 'ਮੰਡੀ ਭਾਅ ਲਈ ਫ਼ਸਲ ਚੁਣੋ',
  state_label: 'ਆਪਣਾ ਰਾਜ ਚੁਣੋ', state_placeholder: 'ਰਾਜ ਚੁਣੋ',
  mandi_summary: 'ਮੰਡੀ ਦਾ ਨਾਮ ਪਤਾ ਹੈ? (ਵਿਕਲਪਿਕ)', mandi_placeholder: 'ਜਿਵੇਂ ਲੁਧਿਆਣਾ',
  btn_see_price: 'ਅੱਜ ਦਾ ਭਾਅ ਵੇਖੋ', safety_label: 'ਜ਼ਰੂਰੀ ਗੱਲ:',
  safety_text: 'ਇਹ ਸਿਰਫ਼ ਸ਼ੁਰੂਆਤੀ AI ਜਾਂਚ ਹੈ। ਦਵਾਈ ਜਾਂ ਇਲਾਜ ਤੋਂ ਪਹਿਲਾਂ ਨੇੜਲੇ ਖੇਤੀ ਮਾਹਿਰ ਦੀ ਸਲਾਹ ਲਓ।',
  footer_tagline: 'ਤਕਨਾਲੋਜੀ ਨਾਲ ਬਿਹਤਰ ਖੇਤੀ।', whatsapp_cta: 'WhatsApp ਉੱਤੇ ਗੱਲ ਕਰੋ ↗',
  speech_unsupported: 'ਤੁਹਾਡੇ ਬ੍ਰਾਊਜ਼ਰ ਵਿੱਚ ਸੁਣਾਉਣ ਦੀ ਸਹੂਲਤ ਉਪਲਬਧ ਨਹੀਂ ਹੈ।',
  speech_failed: 'ਆਡੀਓ ਨਹੀਂ ਚੱਲ ਸਕਿਆ। ਕਿਰਪਾ ਕਰਕੇ ਸਪੀਕਰ ਦੀ ਆਵਾਜ਼ ਜਾਂਚੋ ਅਤੇ ਮੁੜ ਕੋਸ਼ਿਸ਼ ਕਰੋ।',
  generic_error: 'ਕੋਈ ਤਕਨੀਕੀ ਸਮੱਸਿਆ ਆਈ ਹੈ। ਕਿਰਪਾ ਕਰਕੇ ਦੁਬਾਰਾ ਕੋਸ਼ਿਸ਼ ਕਰੋ।',
  disease_choose_photo_first: 'ਪਹਿਲਾਂ ਕੈਮਰੇ / ਗੈਲਰੀ ਤੋਂ ਪੱਤੇ ਦੀ ਫੋਟੋ ਚੁਣੋ।', disease_checking: 'ਜਾਂਚ ਹੋ ਰਹੀ ਹੈ…',
  disease_choose_crop_first: 'ਰੋਗ ਜਾਂਚ ਤੋਂ ਪਹਿਲਾਂ ਆਪਣੀ ਫ਼ਸਲ ਚੁਣੋ।',
  disease_crop_label: 'ਫ਼ਸਲ:', disease_confidence_label: 'ਭਰੋਸਾ:', disease_remedy_label: 'ਕੀ ਕਰਨਾ ਹੈ:',
  market_choose_crop_first: 'ਪਹਿਲਾਂ ਉੱਪਰੋਂ ਆਪਣੀ ਫ਼ਸਲ ਚੁਣੋ।', market_choose_state_first: 'ਕਿਰਪਾ ਕਰਕੇ ਆਪਣਾ ਰਾਜ ਚੁਣੋ।',
  market_finding: 'ਭਾਅ ਲੱਭਿਆ ਜਾ ਰਿਹਾ ਹੈ…', market_min: 'ਘੱਟੋ-ਘੱਟ', market_modal: 'ਔਸਤ ਭਾਅ', market_max: 'ਵੱਧ ਤੋਂ ਵੱਧ',
  market_wholesale_source: 'ਥੋਕ ਭਾਅ ਪ੍ਰਤੀ ਕੁਇੰਟਲ · ਸਰੋਤ:',
  whatsapp_not_configured: 'WhatsApp ਸੇਵਾ ਦਾ ਨੰਬਰ ਅਜੇ ਸੈੱਟ ਨਹੀਂ ਹੈ।',
  no_mandi_quote: 'ਇਸ ਫ਼ਸਲ ਅਤੇ ਰਾਜ ਲਈ ਪ੍ਰਮਾਣਿਤ ਮੰਡੀ ਭਾਅ ਇਸ ਵੇਲੇ ਉਪਲਬਧ ਨਹੀਂ ਹੈ।',
  photo_quality_reject: 'ਕਿਰਪਾ ਕਰਕੇ ਪੱਤੇ ਦੀ ਸਾਫ਼, ਨੇੜਿਉਂ ਅਤੇ ਚੰਗੀ ਰੌਸ਼ਨੀ ਵਾਲੀ ਫੋਟੋ ਅੱਪਲੋਡ ਕਰੋ।',
  spoken_welcome: 'ਕ੍ਰਿਸ਼ੀਮਿੱਤਰ ਵਿੱਚ ਤੁਹਾਡਾ ਸਵਾਗਤ ਹੈ। ਪੱਤੇ ਦੀ ਫੋਟੋ ਨਾਲ ਬਿਮਾਰੀ ਜਾਂਚੋ ਜਾਂ ਅੱਜ ਦਾ ਮੰਡੀ ਭਾਅ ਜਾਣੋ।',
  spoken_safety: 'ਇਹ ਸ਼ੁਰੂਆਤੀ ਏ ਆਈ ਜਾਂਚ ਹੈ। ਇਲਾਜ ਤੋਂ ਪਹਿਲਾਂ ਨੇੜਲੇ ਖੇਤੀ ਮਾਹਿਰ ਨਾਲ ਸਲਾਹ ਕਰੋ।'
};

let currentLang = 'hi';

function t(key) {
  return (STRINGS[currentLang] && STRINGS[currentLang][key]) || STRINGS.hi[key] || key;
}

function applyStaticText() {
  document.documentElement.lang = currentLang;
  document.title = t('page_title');
  document.querySelectorAll('[data-i18n]').forEach(el => { el.textContent = t(el.dataset.i18n); });
  document.querySelectorAll('[data-i18n-placeholder]').forEach(el => { el.placeholder = t(el.dataset.i18nPlaceholder); });
  document.querySelectorAll('[data-i18n-aria]').forEach(el => { el.setAttribute('aria-label', t(el.dataset.i18nAria)); });
}

function renderCropChips() {
  // Fixed 4 chips inside the disease-check form
  document.querySelectorAll('#disease-form .crop-chip').forEach(btn => {
    const c = CROPS.find(c => c.key === btn.dataset.crop);
    if (c) btn.textContent = `${c.icon} ${c[currentLang] || c.en}`;
  });
  // Full crop list inside the market-price form
  const marketChips = document.querySelector('#market-form .chips');
  const selected = document.querySelector('#selected-commodity').value;
  marketChips.innerHTML = CROPS.map(c =>
    `<button type="button" class="market-chip${c.key === selected ? ' active' : ''}" data-commodity="${c.key}">${c.icon} ${c[currentLang] || c.en}</button>`
  ).join('');
}

function renderStateSelect() {
  const sel = document.querySelector('select[name="state"]');
  const prev = sel.value;
  sel.innerHTML = `<option value="">${t('state_placeholder')}</option>` +
    STATES.map(s => `<option value="${s.key}"${s.key === prev ? ' selected' : ''}>${s[currentLang] || s.en}</option>`).join('');
}

function setLanguage(lang) {
  currentLang = ['hi', 'en', 'pa'].includes(lang) ? lang : 'hi';
  applyStaticText();
  renderCropChips();
  renderStateSelect();
  document.querySelectorAll('input[name="language"]').forEach(i => { i.value = currentLang; });
  document.querySelectorAll('[data-speak-key]').forEach(b => {
    // keep TTS text in sync too, read from STRINGS via spoken_* keys
  });
  document.dispatchEvent(new CustomEvent('km:language-changed', { detail: { lang: currentLang } }));
}

// Delegated click handler survives the innerHTML re-render on language change
const marketChips = document.querySelector('#market-form .chips');
marketChips.addEventListener('click', e => {
  const b = e.target.closest('.market-chip');
  if (!b) return;
  marketChips.querySelectorAll('button').forEach(x => x.classList.remove('active'));
  b.classList.add('active');
  document.querySelector('#selected-commodity').value = b.dataset.commodity;
});

// WhatsApp placeholder handling
const whatsapp = document.querySelector('#whatsapp-link');
whatsapp.addEventListener('click', e => {
  if (whatsapp.getAttribute('href') === '#help') {
    e.preventDefault();
    alert(t('whatsapp_not_configured'));
  }
});

// Language dropdown drives everything
document.querySelector('#language').addEventListener('change', e => setLanguage(e.target.value));

// Expose a small API for app.js to use
window.KM_I18N = { t, CROPS, STATES, setLanguage, get lang() { return currentLang; } };

// Initial render (defaults to whatever the <select> currently shows, i.e. Hindi)
setLanguage(document.querySelector('#language').value || 'hi');

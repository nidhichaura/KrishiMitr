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
  { key: 'orange',       icon: '🍊', hi: 'संतरा',    en: 'Orange' },
  { key: 'peach',        icon: '🍑', hi: 'आड़ू',      en: 'Peach' },
  { key: 'bell pepper',  icon: '🫑', hi: 'शिमला मिर्च', en: 'Bell pepper' },
  { key: 'cherry',       icon: '🍒', hi: 'चेरी',      en: 'Cherry' },
  { key: 'blueberry',    icon: '🫐', hi: 'ब्लूबेरी',  en: 'Blueberry' },
  { key: 'strawberry',   icon: '🍓', hi: 'स्ट्रॉबेरी', en: 'Strawberry' },
  { key: 'raspberry',    icon: '🫐', hi: 'रास्पबेरी', en: 'Raspberry' },
  { key: 'squash',       icon: '🎃', hi: 'स्क्वैश',   en: 'Squash' }
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
    choice_market_title: 'फसल खरीदें या बेचें', choice_market_desc: 'आज की बोली लगाएं और खरीदारों से जुड़ें', choice_market_cta: 'बाज़ार खोलें →',
    marketplace_eyebrow: 'सीधा किसान बाज़ार', marketplace_title: 'आज की फसल बोली', marketplace_today: 'आज,', marketplace_intro: 'फसल सूची देखें, अपनी उपज बेचें, या अपनी खरीद की दैनिक बोली लगाएं।', marketplace_live: 'लाइव बोली', marketplace_buy: '🛒 फसल खरीदें', marketplace_sell: '🌾 फसल बेचें', marketplace_available: 'आज उपलब्ध', marketplace_nearby: 'पास की फसलें', marketplace_all_crops: 'सभी फसलें ▾', marketplace_buying_for: 'खरीदने के लिए', marketplace_selling_for: 'बेचने के लिए', marketplace_place_bid: 'अपनी बोली लगाएं', marketplace_buy_help: 'अच्छी बोली विक्रेताओं को तुरंत दिखाई देगी।', marketplace_sell_help: 'अपनी उपज और अपेक्षित कीमत खरीदारों को दिखाएं।', marketplace_crop: 'फसल', marketplace_choose_crop: 'फसल चुनें', marketplace_quantity: 'मात्रा', marketplace_bid_price: 'बोली कीमत', marketplace_location: 'मंडी / स्थान', marketplace_date: 'बोली की तारीख', marketplace_quintal: 'क्विंटल', marketplace_per_quintal: '₹ / क्विंटल', marketplace_location_placeholder: 'जैसे करनाल, हरियाणा', marketplace_quantity_placeholder: 'जैसे 20', marketplace_price_placeholder: '₹ प्रति क्विंटल', marketplace_buy_bid: 'खरीद बोली लगाएं', marketplace_sell_bid: 'बिक्री सूची बनाएं', marketplace_privacy: '🔒 आपका संपर्क केवल आपकी सहमति के बाद साझा किया जाएगा।', marketplace_bid_success: '✓ {crop} के लिए आपकी {trade} ₹{price} / क्विंटल पर {date} के लिए तैयार है।', marketplace_buy_trade: 'खरीद बोली', marketplace_sell_trade: 'बिक्री सूची',
    aria_marketplace_tabs: 'खरीदें या बेचें', crop_rice: 'धान', crop_onion: 'प्याज', crop_soybean: 'सोयाबीन',
    filter_crop: 'फसल', filter_price_type: 'मूल्य प्रकार', filter_all_crops: 'सभी फसलें', filter_all_prices: 'सभी मूल्य', filter_msp: 'MSP मूल्य', filter_bid: 'बोली मूल्य', filter_empty: 'इस फ़िल्टर के लिए कोई फसल नहीं मिली।', buy_wheat_meta: 'खरीद आवश्यकता · 35 क्विंटल', buy_maize_meta: 'खरीद आवश्यकता · 50 क्विंटल', buy_wheat_location: 'पानीपत, हरियाणा · नक्शा देखें', buy_maize_location: 'देवास, मध्य प्रदेश · नक्शा देखें', marketplace_buy_listings: 'खरीद की ज़रूरतें', marketplace_sell_listings: 'बिक्री के लिए फसलें',
    merged_mandi_title: 'आज का मंडी भाव देखें', merged_mandi_note: 'किसी भी फसल, राज्य और मंडी का सत्यापित थोक भाव', filter_state: 'राज्य', filter_all_states: 'सभी राज्य', state_haryana: 'हरियाणा', state_maharashtra: 'महाराष्ट्र', state_madhya_pradesh: 'मध्य प्रदेश', filter_variety: 'फसल की किस्म', filter_all_varieties: 'सभी किस्में', variety_grade_a: 'ग्रेड A', variety_hybrid: 'हाइब्रिड', variety_organic: 'जैविक', filter_min_price: 'न्यूनतम कीमत',
    filter_multiple_hint: 'एक से अधिक चुनने के लिए Ctrl/Cmd दबाएं',
    marketplace_demo_note: 'डेमो: नीचे दिखाई बोली उदाहरण हैं। असली बोली केवल सत्यापित उपयोगकर्ताओं के जोड़ने पर दिखाई जाएगी।',
    filter_choose: 'चुनें', filter_selected: 'चुने गए',
    opencv_assurance: 'फोटो की सफ़ाई और पत्ते की पहचान OpenCV से जांची जाती है।', spoken_photo: 'पहले अपनी फसल चुनें। फिर कैमरा खोलें और पत्ते की साफ, नज़दीक से फोटो लें। कृषिमित्र OpenCV और AI से फोटो जांचेगा।', spoken_marketplace: 'यहाँ आप मंडी का सत्यापित भाव देख सकते हैं, फसल और राज्य चुन सकते हैं, या फसल खरीदने और बेचने की बोली लगा सकते हैं।', spoken_pilot: 'विशेषज्ञ से मदद के लिए अपना मोबाइल नंबर या ईमेल भरें। आपकी अनुमति के बिना जानकारी साझा नहीं होगी।',
    camera_tip: 'अभी पत्ते की फोटो लें', gallery_open: 'गैलरी से चुनें', gallery_tip: 'पहले से ली गई फोटो चुनें',
    photo_ready: 'फोटो जांच के लिए तैयार है', photo_ready_tip: 'साफ दिखाई दे रही है? अब फोटो जांचें दबाएं।', change_photo: 'फोटो बदलें',
    camera_title: 'पत्ते की लाइव फोटो लें', camera_instruction: 'पत्ते को रोशनी में रखें और स्क्रीन के बीच में दिखाएं।', capture_photo: 'फोटो लें', camera_unavailable: 'कैमरा नहीं खुल पाया। ब्राउज़र में कैमरा अनुमति दें या गैलरी से फोटो चुनें।',
    file_choose: 'फोटो फ़ाइल चुनें', file_choose_tip: 'फोन या कंप्यूटर से पत्ते की साफ फोटो चुनें', file_choose_cta: 'फ़ाइल चुनें →',
    auto_leaf_title: 'AI खुद पत्ते और बीमारी की पहचान करेगा', auto_leaf_note: 'बस एक साफ पत्ते की फोटो चुनें।',
    advisory_eyebrow: 'AI खेत सलाह', advisory_title: 'मिट्टी और मौसम के अनुसार सलाह', advisory_note: 'मिट्टी जांच की NPK रिपोर्ट और अपने खेत की स्थिति भरें। AI आपको फसल की अनुकूलता और अगला कदम बताएगा।', advisory_crop: 'वर्तमान / पसंदीदा फसल', advisory_any_crop: 'AI को चुनने दें', advisory_temp: 'औसत तापमान °C', advisory_rain: 'हाल की / अनुमानित बारिश (mm)', advisory_n: 'नाइट्रोजन (N)', advisory_p: 'फॉस्फोरस (P)', advisory_k: 'पोटैशियम (K)', advisory_ph: 'मिट्टी pH', advisory_question: 'अपना सवाल पूछें (वैकल्पिक)', advisory_question_placeholder: 'जैसे: क्या इस महीने मक्का बोना सही है?', advisory_submit: 'AI खेत सलाह देखें', advisory_safety: '⚠️ यह निर्णय-सहायता है, उर्वरक की निश्चित मात्रा नहीं। अंतिम मात्रा मिट्टी जांच और स्थानीय कृषि अधिकारी से तय करें।', advisory_recommended: 'अनुकूल फसल', advisory_sowing: 'बुवाई की सामान्य अवधि', advisory_priority: 'ध्यान देने योग्य पोषक तत्व', advisory_balanced: 'NPK स्थिति संतुलित है', advisory_good: 'आपकी दी हुई स्थितियाँ इस फसल के लिए अच्छी लगती हैं।', advisory_check: 'बुवाई से पहले स्थितियाँ स्थानीय कृषि विशेषज्ञ से जांचें।', spoken_advisory: 'मिट्टी की NPK रिपोर्ट, पी एच, तापमान और बारिश भरें। AI आपको उपयुक्त फसल और पोषक तत्व पर अगला कदम बताएगा।',
    advisory_answer_sowing: 'आपके खेत की स्थिति के आधार पर ऊपर दी सामान्य बुवाई अवधि देखें। स्थानीय मौसम चेतावनी और सिंचाई उपलब्धता भी जांचें।', advisory_answer_nutrient: 'मॉडल पोषक तत्व की कमी का संकेत देता है, पर उर्वरक की मात्रा केवल मिट्टी जांच और कृषि अधिकारी की सलाह से तय करें।', advisory_answer_general: 'दिए गए खेत डेटा के आधार पर यह सबसे सुरक्षित अगला कदम है। अधिक सटीक सलाह के लिए मिट्टी जांच की हाल की रिपोर्ट जोड़ें।',
    use_location: 'मेरी लोकेशन से मौसम लें', location_help: 'आपकी अनुमति के बाद तापमान और आज की बारिश अपने आप भर जाएगी।', location_loading: 'लोकेशन और मौसम लिया जा रहा है…', location_success: 'लोकेशन के अनुसार मौसम भर दिया गया। NPK और pH अपनी मिट्टी जांच रिपोर्ट से भरें।', location_error: 'लोकेशन या मौसम नहीं मिल पाया। कृपया तापमान और बारिश खुद भरें।',
    location_permission_error: 'लोकेशन अनुमति बंद है। Browser के address-bar के lock icon से Location को Allow करें, फिर दोबारा दबाएं।', location_unavailable_error: 'फोन/कंप्यूटर की लोकेशन उपलब्ध नहीं है। Device Location चालू करें और खुले स्थान या बेहतर network में फिर कोशिश करें।', location_timeout_error: 'लोकेशन लेने में समय लगा। बेहतर network के साथ फिर दबाएं।',
    bid_location_fallback: 'लोकेशन कैप्चर हुई — पास का लैंडमार्क जोड़ें',
    bid_location_loading: 'पास का स्थान ढूंढ रहे हैं…', bid_location_success: 'सटीक स्थान और लैंडमार्क जुड़ गया', bid_location_unavailable: 'स्थान उपलब्ध नहीं है',
    listing_wheat: 'गेहूँ', listing_tomato: 'टमाटर', listing_maize: 'मक्का', listing_wheat_meta: 'ग्रेड A · 42 क्विंटल', listing_tomato_meta: 'ताज़ा उपज · 18 क्विंटल', listing_maize_meta: 'सूखा अनाज · 60 क्विंटल', listing_wheat_location: '📍 करनाल, हरियाणा', listing_tomato_location: '📍 नासिक, महाराष्ट्र', listing_maize_location: '📍 इंदौर, मध्य प्रदेश',
    eyebrow_steps: 'बस तीन कदम',
    h2_disease: 'पत्ते की फोटो से जांच',
    step1: 'अच्छी रोशनी में एक पत्ते की फोटो लें',
    step2: 'पत्ता फोटो के बीच में और साफ दिखना चाहिए',
    step3: 'स्क्रीनशॉट या इंटरनेट फोटो न भेजें',
    legend_crop_optional: 'फसल चुनें (वैकल्पिक)',
    legend_crop_optional_small: '(नहीं पता? AI पत्ते से पहचानने की कोशिश करेगा)',
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
    mandi_placeholder: 'जैसे आज़ादपुर',
    btn_see_price: 'आज का भाव देखें',
    safety_label: 'ज़रूरी बात:',
    safety_text: 'यह शुरुआती AI जांच है। दवा की मात्रा या उपचार शुरू करने से पहले नज़दीकी कृषि विशेषज्ञ से सलाह लें।',
    listen_label_compact: 'सुनें',
    footer_tagline: 'तकनीक के साथ बेहतर खेती।',
    whatsapp_cta: 'WhatsApp पर बात करें ↗',
    pilot_eyebrow: 'विशेष सहायता',
    pilot_title: 'विशेषज्ञ की सलाह के लिए अनुरोध',
    pilot_note: 'बीमारी की जांच और मंडी भाव हमेशा निःशुल्क हैं। यदि आप भविष्य में विशेषज्ञ की सलाह चाहते हैं, तो यहाँ अपनी जानकारी भरें।',
    pilot_identifier_label: 'मोबाइल नंबर या ईमेल',
    pilot_district_label: 'जिला (वैकल्पिक)',
    pilot_state_label: 'राज्य (वैकल्पिक)',
    pilot_consent: 'मैं सेवा को बेहतर बनाने के लिए अपनी गतिविधि का केवल गुमनाम उपयोग करने की अनुमति देता/देती हूँ। मेरा मोबाइल नंबर, संदेश और फोटो साझा नहीं किए जाएंगे।',
    pilot_submit: 'अनुरोध भेजें',
    pilot_identifier_error: 'कृपया सही मोबाइल नंबर या ईमेल दर्ज करें।',
    pilot_success: 'आपका अनुरोध दर्ज हो गया है। यह सेवा उपलब्ध होने पर हम आपको बताएंगे।',

    speech_unsupported: 'आपके ब्राउज़र में सुनाने की सुविधा उपलब्ध नहीं है।',
    speech_failed: 'ऑडियो नहीं चल पाया। कृपया स्पीकर की आवाज़ जांचें और पेज रीफ्रेश करके फिर दबाएं।',
    generic_error: 'कुछ तकनीकी समस्या हुई। कृपया फिर कोशिश करें।',
    disease_choose_photo_first: 'पहले कैमरा / गैलरी से पत्ते की फोटो चुनें।',
    disease_choose_crop_first: 'रोग जांच से पहले अपनी फसल चुनें।',
    disease_checking: 'जांच हो रही है…',
    disease_crop_label: 'फसल:',
    disease_confidence_label: 'भरोसा:',
    disease_remedy_label: 'क्या करें:',
    disease_disclaimer: 'यह शुरुआती फोटो जांच है। दवा या उपचार से पहले नज़दीकी कृषि विशेषज्ञ से सलाह लें।',
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
    choice_market_title: 'Buy or sell crops', choice_market_desc: 'Place today’s bid and connect with buyers', choice_market_cta: 'Open marketplace →',
    marketplace_eyebrow: 'Direct farmer marketplace', marketplace_title: "Today's crop bids", marketplace_today: 'Today,', marketplace_intro: 'Browse crop listings, sell your harvest, or place a daily buying bid.', marketplace_live: 'Live bidding', marketplace_buy: '🛒 Buy crops', marketplace_sell: '🌾 Sell crops', marketplace_available: 'Available today', marketplace_nearby: 'Nearby crops', marketplace_all_crops: 'All crops ▾', marketplace_buying_for: 'For buying', marketplace_selling_for: 'For selling', marketplace_place_bid: 'Place your bid', marketplace_buy_help: 'A strong bid will be shown to sellers right away.', marketplace_sell_help: 'Show your harvest and expected price to buyers.', marketplace_crop: 'Crop', marketplace_choose_crop: 'Choose crop', marketplace_quantity: 'Quantity', marketplace_bid_price: 'Bid price', marketplace_location: 'Mandi / location', marketplace_date: 'Bid date', marketplace_quintal: 'Quintal', marketplace_per_quintal: '₹ / quintal', marketplace_location_placeholder: 'e.g. Karnal, Haryana', marketplace_quantity_placeholder: 'e.g. 20', marketplace_price_placeholder: '₹ per quintal', marketplace_buy_bid: 'Place buying bid', marketplace_sell_bid: 'Create sale listing', marketplace_privacy: '🔒 Your contact is shared only with your consent.', marketplace_bid_success: '✓ Your {trade} for {crop} at ₹{price} / quintal is ready for {date}.', marketplace_buy_trade: 'buying bid', marketplace_sell_trade: 'sale listing',
    aria_marketplace_tabs: 'Buy or sell', crop_rice: 'Rice', crop_onion: 'Onion', crop_soybean: 'Soybean',
    filter_crop: 'Crop', filter_price_type: 'Price type', filter_all_crops: 'All crops', filter_all_prices: 'All prices', filter_msp: 'MSP price', filter_bid: 'Bid price', filter_empty: 'No crops match these filters.', buy_wheat_meta: 'Purchase need · 35 quintals', buy_maize_meta: 'Purchase need · 50 quintals', buy_wheat_location: 'Panipat, Haryana · View map', buy_maize_location: 'Dewas, Madhya Pradesh · View map', marketplace_buy_listings: 'Buying requests', marketplace_sell_listings: 'Crops for sale',
    merged_mandi_title: "See today's mandi price", merged_mandi_note: 'Verified wholesale prices by crop, state and mandi', filter_state: 'State', filter_all_states: 'All states', state_haryana: 'Haryana', state_maharashtra: 'Maharashtra', state_madhya_pradesh: 'Madhya Pradesh', filter_variety: 'Crop variety', filter_all_varieties: 'All varieties', variety_grade_a: 'Grade A', variety_hybrid: 'Hybrid', variety_organic: 'Organic', filter_min_price: 'Minimum price',
    filter_multiple_hint: 'Hold Ctrl/Cmd to choose more than one',
    marketplace_demo_note: 'Demo: the bids below are examples. Live bids will appear only after verified users are connected.',
    filter_choose: 'Choose', filter_selected: 'selected',
    opencv_assurance: 'Photo clarity and leaf presence are checked using OpenCV.', spoken_photo: 'First choose your crop. Then open the camera and take a clear, close photo of one leaf. KrishiMitr checks it using OpenCV and AI.', spoken_marketplace: 'Here you can see a verified mandi price by choosing your crop and state, or place a bid to buy or sell crops.', spoken_pilot: 'For expert help, enter your mobile number or email. Your details are not shared without your permission.',
    camera_tip: 'Take a leaf photo now', gallery_open: 'Choose from gallery', gallery_tip: 'Select a photo already taken',
    photo_ready: 'Photo is ready to check', photo_ready_tip: 'Does it look clear? Tap Check photo now.', change_photo: 'Change photo',
    camera_title: 'Take a live leaf photo', camera_instruction: 'Keep the leaf in good light and in the centre of the screen.', capture_photo: 'Take photo', camera_unavailable: 'The camera could not open. Allow camera access in your browser, or choose a photo from the gallery.',
    file_choose: 'Choose photo file', file_choose_tip: 'Choose a clear leaf photo from your phone or computer', file_choose_cta: 'Choose file →',
    auto_leaf_title: 'AI will identify the leaf and disease', auto_leaf_note: 'Just choose one clear leaf photo.',
    advisory_eyebrow: 'AI field advisory', advisory_title: 'Advice from soil and weather conditions', advisory_note: 'Enter your soil-test NPK values and field conditions. AI will show crop fit and the next step.', advisory_crop: 'Current / preferred crop', advisory_any_crop: 'Let AI choose', advisory_temp: 'Average temperature °C', advisory_rain: 'Recent / expected rainfall (mm)', advisory_n: 'Nitrogen (N)', advisory_p: 'Phosphorus (P)', advisory_k: 'Potassium (K)', advisory_ph: 'Soil pH', advisory_question: 'Ask your question (optional)', advisory_question_placeholder: 'e.g. Is it right to sow maize this month?', advisory_submit: 'See AI field advice', advisory_safety: '⚠️ This is decision support, not a fertiliser prescription. Confirm final quantity with a soil test and local agriculture officer.', advisory_recommended: 'Suitable crop', advisory_sowing: 'Typical sowing window', advisory_priority: 'Nutrient to check', advisory_balanced: 'NPK condition looks balanced', advisory_good: 'Your entered conditions look suitable for this crop.', advisory_check: 'Check local conditions with an agriculture expert before sowing.', spoken_advisory: 'Enter your soil test NPK values, pH, temperature and rainfall. AI will suggest a suitable crop and nutrient next step.',
    advisory_answer_sowing: 'Based on your field conditions, see the typical sowing window above. Also check local weather alerts and irrigation availability.', advisory_answer_nutrient: 'The model indicates a nutrient gap, but fertiliser quantity must be decided only with a soil test and agriculture officer.', advisory_answer_general: 'This is the safest next step from the field data you entered. Add a recent soil-test report for more precise advice.',
    use_location: 'Use my location for weather', location_help: 'After your permission, temperature and today’s rainfall will fill automatically.', location_loading: 'Getting location and weather…', location_success: 'Weather was filled for your location. Enter NPK and pH from your soil-test report.', location_error: 'Location or weather could not be found. Please enter temperature and rainfall yourself.',
    location_permission_error: 'Location permission is blocked. Use the lock icon in the browser address bar to allow Location, then try again.', location_unavailable_error: 'Your device location is unavailable. Turn on Device Location and try again with a better network or open sky.', location_timeout_error: 'Location took too long. Try again with a better network.',
    bid_location_fallback: 'Location captured — add a nearby landmark',
    bid_location_loading: 'Finding nearby place…', bid_location_success: 'Exact place and landmark added', bid_location_unavailable: 'Location unavailable',
    listing_wheat: 'Wheat', listing_tomato: 'Tomato', listing_maize: 'Maize', listing_wheat_meta: 'Grade A · 42 quintals', listing_tomato_meta: 'Farm fresh · 18 quintals', listing_maize_meta: 'Dry grain · 60 quintals', listing_wheat_location: '📍 Karnal, Haryana', listing_tomato_location: '📍 Nashik, Maharashtra', listing_maize_location: '📍 Indore, Madhya Pradesh',
    eyebrow_steps: 'Just three steps',
    h2_disease: 'Check using a leaf photo',
    step1: 'Take a leaf photo in good light',
    step2: 'The leaf should be clear and centred in the photo',
    step3: "Don't send screenshots or photos from the internet",
    legend_crop_optional: 'Choose crop (optional)',
    legend_crop_optional_small: '(not sure? AI will try to identify it from the leaf)',
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
    pilot_eyebrow: 'Extra support',
    pilot_title: 'Request expert advice',
    pilot_note: 'Disease screening and mandi prices are always free. Fill this form only if you want expert advice in the future.',
    pilot_identifier_label: 'Mobile number or email',
    pilot_district_label: 'District (optional)',
    pilot_state_label: 'State (optional)',
    pilot_consent: 'I allow anonymous use of my activity only to improve the service. My mobile number, messages and photos will not be shared.',
    pilot_submit: 'Submit request',
    pilot_identifier_error: 'Please enter a valid mobile number or email.',
    pilot_success: 'Your request is recorded. We will let you know when this service is available.',

    speech_unsupported: 'Your browser does not support the read-aloud feature.',
    speech_failed: 'Audio could not play. Please check your speaker volume and try again after refreshing the page.',
    generic_error: 'Something went wrong. Please try again.',
    disease_choose_photo_first: 'Please choose a leaf photo from camera/gallery first.',
    disease_choose_crop_first: 'Please choose your crop before disease screening.',
    disease_checking: 'Checking…',
    disease_crop_label: 'Crop:',
    disease_confidence_label: 'Confidence:',
    disease_remedy_label: 'What to do:',
    disease_disclaimer: 'This is an initial photo screening. Consult a local agricultural expert before starting treatment.',
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
  disease_disclaimer: 'ਇਹ ਸ਼ੁਰੂਆਤੀ ਫੋਟੋ ਜਾਂਚ ਹੈ। ਇਲਾਜ ਤੋਂ ਪਹਿਲਾਂ ਨੇੜਲੇ ਖੇਤੀ ਮਾਹਿਰ ਨਾਲ ਸਲਾਹ ਕਰੋ।',
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

"""
Lightweight language detection (script-based) and localized string templates.

This avoids pulling in a heavy translation model — for a real deployment you
would route through Bhashini's translation API (see services/speech_service.py
for where that integration point lives). For now, detection is done via
Unicode block matching, which is fast, dependency-free, and works well for
short WhatsApp messages typed in native scripts.
"""
from app.core.constants import Language

# Unicode ranges for common Indian scripts
_SCRIPT_RANGES = {
    Language.HINDI.value: [(0x0900, 0x097F)],     # Devanagari (also used for Marathi)
    Language.PUNJABI.value: [(0x0A00, 0x0A7F)],   # Gurmukhi
    Language.TAMIL.value: [(0x0B80, 0x0BFF)],     # Tamil
    Language.TELUGU.value: [(0x0C00, 0x0C7F)],    # Telugu
    Language.BENGALI.value: [(0x0980, 0x09FF)],   # Bengali / Assamese
    Language.ODIA.value: [(0x0B00, 0x0B7F)],      # Odia
    Language.KANNADA.value: [(0x0C80, 0x0CFF)],   # Kannada
    Language.MALAYALAM.value: [(0x0D00, 0x0D7F)], # Malayalam
    Language.GUJARATI.value: [(0x0A80, 0x0AFF)],  # Gujarati
    Language.URDU.value: [(0x0600, 0x06FF)],      # Arabic script (Urdu)
}


# Common Hindi/farming words typed in Roman script ("Hinglish") — very common
# on WhatsApp. Without this, ASCII text is wrongly assumed to be English.
_ROMANIZED_HINDI_MARKERS = {
    "namaste", "namaskar", "namaskaar", "kaise", "kaisa", "kaisi",
    "dhanyawad", "dhanyavad", "shukriya", "bhaiya", "kisan", "fasal",
    "khet", "mandi", "bhav", "kimat", "kitna", "kitni", "paani", "barish",
    "gehu", "gehun", "chawal", "aloo", "pyaz", "tamatar", "sarson",
    "ganna", "makka", "kapas", "bech", "bimari", "kharab",
}

_SCRIPT_LANGUAGE_MARKERS = {
    # Marathi and Hindi share Devanagari; Assamese and Bengali share Bengali
    # script.  These common words make text replies choose the right variant.
    Language.MARATHI.value: {"आहे", "शेती", "पीक", "पिके", "किंमत", "कोणती"},
    Language.ASSAMESE.value: {"নমস্কাৰ", "মই", "আপোনাৰ", "শস্যৰ", "শস্য", "অসম"},
}

_LANGUAGE_ALIASES = {"od": "or", "ori": "or", "ben": "bn", "kan": "kn", "mal": "ml", "mar": "mr"}


def normalize_language(lang: str | None, default: str = "hi") -> str:
    """Return an internal supported code for browser, ASR, and text inputs."""
    code = (lang or "").lower().split("-")[0]
    code = _LANGUAGE_ALIASES.get(code, code)
    return code if code in {item.value for item in Language} else default


def detect_user_language(text: str, default: str = "hi") -> str:
    """Detect language from script of the text. Falls back to `default`."""
    if not text or not text.strip():
        return default

    normalized_text = text.lower()
    for lang, markers in _SCRIPT_LANGUAGE_MARKERS.items():
        if any(marker in normalized_text for marker in markers):
            return lang

    for lang, ranges in _SCRIPT_RANGES.items():
        for char in text:
            code_point = ord(char)
            for start, end in ranges:
                if start <= code_point <= end:
                    return lang

    # Check for Hindi words written in Roman script before assuming English
    normalized_tokens = set(text.lower().split())
    if normalized_tokens & _ROMANIZED_HINDI_MARKERS:
        return Language.HINDI.value

    # No Indic script or Hinglish keyword matched -> assume Latin/English input
    if text.strip().isascii():
        return Language.ENGLISH.value

    return default


# Localized message templates keyed by [message_key][language]
MESSAGES = {
    "greeting": {
        "hi": "🙏 नमस्ते! मैं कृषिमित्र हूं, आपका कृषि सहायक। आप मुझसे फसल की कीमत या बीमारी के बारे में पूछ सकते हैं।",
        "en": "🙏 Hello! I'm KrishiMitr, your farming assistant. Ask me about crop prices or send a leaf photo to check for disease.",
        "mr": "🙏 नमस्कार! मी कृषिमित्र आहे, तुमचा शेती सहाय्यक. तुम्ही पीक भाव किंवा रोगाबद्दल विचारू शकता.",
        "pa": "🙏 ਸਤ ਸ੍ਰੀ ਅਕਾਲ! ਮੈਂ ਕ੍ਰਿਸ਼ੀਮਿੱਤਰ ਹਾਂ, ਤੁਹਾਡਾ ਖੇਤੀ ਸਹਾਇਕ।",
        "ta": "🙏 வணக்கம்! நான் கிரிஷிமித்ரா, உங்கள் விவசாய உதவியாளர்.",
    "te": "🙏 నమస్తే! నేను కృషిమిత్ర, మీ వ్యవసాయ సహాయకుడిని.",
        "bn": "🙏 নমস্কার! আমি কৃষিমিত্র, আপনার কৃষি সহায়ক। ফসলের দাম বা রোগ সম্পর্কে জিজ্ঞাসা করতে পারেন।",
        "or": "🙏 ନମସ୍କାର! ମୁଁ କୃଷିମିତ୍ର, ଆପଣଙ୍କ କୃଷି ସହାୟକ। ଫସଲ ଦର କିମ୍ବା ରୋଗ ବିଷୟରେ ପଚାରନ୍ତୁ।",
        "kn": "🙏 ನಮಸ್ಕಾರ! ನಾನು ಕೃಷಿಮಿತ್ರ, ನಿಮ್ಮ ಕೃಷಿ ಸಹಾಯಕ. ಬೆಳೆ ಬೆಲೆ ಅಥವಾ ರೋಗದ ಬಗ್ಗೆ ಕೇಳಬಹುದು.",
        "ml": "🙏 നമസ്കാരം! ഞാൻ കൃഷിമിത്ര, നിങ്ങളുടെ കാർഷിക സഹായി. വിളവിന്റെ വിലയോ രോഗത്തെക്കുറിച്ചോ ചോദിക്കാം.",
        "gu": "🙏 નમસ્તે! હું કૃષિમિત્ર, તમારો ખેતી સહાયક છું. પાકના ભાવ અથવા રોગ વિશે પૂછો.",
        "as": "🙏 নমস্কাৰ! মই কৃষিমিত্ৰ, আপোনাৰ কৃষি সহায়ক। শস্যৰ দাম বা ৰোগৰ বিষয়ে সুধিব পাৰে।",
    },
    "market_price_result": {
        "hi": "📊 *{commodity}* का सत्यापित थोक भाव ({mandi}, {state}):\nकिस्म: {variety}\nन्यूनतम: ₹{min_price}/क्विंटल\nअधिकतम: ₹{max_price}/क्विंटल\nमोडल भाव: ₹{modal_price}/क्विंटल\nडेटा दिनांक: {date}\nस्रोत: {source}",
        "en": "📊 Verified wholesale *{commodity}* quote ({mandi}, {state}):\nVariety: {variety}\nMin: ₹{min_price}/quintal\nMax: ₹{max_price}/quintal\nModal: ₹{modal_price}/quintal\nData date: {date}\nSource: {source}",
        "mr": "📊 *{commodity}* चा भाव ({mandi}, {state}):\nकिमान: ₹{min_price}/क्विंटल\nकमाल: ₹{max_price}/क्विंटल\nसरासरी: ₹{modal_price}/क्विंटल\nदिनांक: {date}",
        "pa": "📊 *{commodity}* ਦਾ ਭਾਅ ({mandi}, {state}):\nਘੱਟੋ-ਘੱਟ: ₹{min_price}/ਕੁਇੰਟਲ\nਵੱਧ ਤੋਂ ਵੱਧ: ₹{max_price}/ਕੁਇੰਟਲ\nਔਸਤ: ₹{modal_price}/ਕੁਇੰਟਲ",
        "ta": "📊 *{commodity}* விலை ({mandi}, {state}):\nகுறைந்தபட்சம்: ₹{min_price}\nஅதிகபட்சம்: ₹{max_price}\nசராசரி: ₹{modal_price}",
        "te": "📊 *{commodity}* ధర ({mandi}, {state}):\nకనిష్టం: ₹{min_price}\nగరిష్టం: ₹{max_price}\nసగటు: ₹{modal_price}",
        "bn": "📊 *{commodity}* এর মণ্ডি দর ({mandi}, {state}):\nসর্বনিম্ন: ₹{min_price}/কুইন্টাল\nসর্বোচ্চ: ₹{max_price}/কুইন্টাল\nগড়: ₹{modal_price}/কুইন্টাল\nতারিখ: {date}",
        "or": "📊 *{commodity}* ମଣ୍ଡି ଦର ({mandi}, {state}):\nସର୍ବନିମ୍ନ: ₹{min_price}/କ୍ୱିଣ୍ଟାଲ\nସର୍ବାଧିକ: ₹{max_price}/କ୍ୱିଣ୍ଟାଲ\nହାରାହାରି: ₹{modal_price}/କ୍ୱିଣ୍ଟାଲ\nତାରିଖ: {date}",
        "kn": "📊 *{commodity}* ಮಂಡಿ ಬೆಲೆ ({mandi}, {state}):\nಕನಿಷ್ಠ: ₹{min_price}/ಕ್ವಿಂಟಾಲ್\nಗರಿಷ್ಠ: ₹{max_price}/ಕ್ವಿಂಟಾಲ್\nಸರಾಸರಿ: ₹{modal_price}/ಕ್ವಿಂಟಾಲ್\nದಿನಾಂಕ: {date}",
        "ml": "📊 *{commodity}* മണ്ഡി വില ({mandi}, {state}):\nകുറഞ്ഞത്: ₹{min_price}/ക്വിന്റൽ\nകൂടിയത്: ₹{max_price}/ക്വിന്റൽ\nശരാശരി: ₹{modal_price}/ക്വിന്റൽ\nതീയതി: {date}",
        "gu": "📊 *{commodity}* મંડી ભાવ ({mandi}, {state}):\nન્યૂનતમ: ₹{min_price}/ક્વિન્ટલ\nમહત્તમ: ₹{max_price}/ક્વિન્ટલ\nસરેરાશ: ₹{modal_price}/ક્વિન્ટલ\nતારીખ: {date}",
    },
    "market_price_unknown_commodity": {
        "hi": "माफ़ कीजिए, मुझे फसल का नाम समझ नहीं आया। कृपया लिखें जैसे: 'गेहूं का भाव' या 'onion price'.",
        "en": "Sorry, I couldn't identify the crop name. Please try like: 'wheat price' or 'गेहूं का भाव'.",
        "mr": "माफ करा, मला पिकाचे नाव समजले नाही. कृपया 'गहू भाव' असे लिहा.",
        "pa": "ਮਾਫ਼ ਕਰੋ, ਮੈਨੂੰ ਫ਼ਸਲ ਦਾ ਨਾਮ ਸਮਝ ਨਹੀਂ ਆਇਆ।",
        "ta": "மன்னிக்கவும், பயிர் பெயரை என்னால் புரிந்துகொள்ள முடியவில்லை.",
        "te": "క్షమించండి, పంట పేరు అర్థం కాలేదు.",
        "bn": "দুঃখিত, ফসলের নাম বুঝতে পারিনি।",
        "or": "କ୍ଷମା କରନ୍ତୁ, ଫସଲର ନାମ ବୁଝିପାରିଲି ନାହିଁ।",
        "kn": "ಕ್ಷಮಿಸಿ, ಬೆಳೆ ಹೆಸರು ಅರ್ಥವಾಗಲಿಲ್ಲ.",
        "ml": "ക്ഷമിക്കണം, വിളയുടെ പേര് മനസ്സിലായില്ല.",
        "gu": "માફ કરશો, પાકનું નામ સમજાયું નથી.",
    },
    "market_price_unavailable": {
        "hi": "अभी सत्यापित मंडी भाव उपलब्ध नहीं है। कृपया फसल और राज्य भेजें, जैसे: 'उत्तर प्रदेश में धान का भाव'। सबसे सही भाव के लिए मंडी का नाम भी जोड़ें।",
        "en": "A verified mandi quote is not available right now. Please send the crop and state, for example: 'paddy price in Uttar Pradesh'. Add the mandi name for the most precise quote.",
        "bn": "এখন যাচাইকৃত মণ্ডির দাম পাওয়া যাচ্ছে না। অনুগ্রহ করে ফসল ও রাজ্যের নাম পাঠান।",
        "or": "ବର୍ତ୍ତମାନ ଯାଞ୍ଚ ହୋଇଥିବା ମଣ୍ଡି ଦର ମିଳୁନାହିଁ। ଦୟାକରି ଫସଲ ଏବଂ ରାଜ୍ୟ ଲେଖନ୍ତୁ।",
        "kn": "ಪರಿಶೀಲಿಸಿದ ಮಂಡಿ ಬೆಲೆ ಈಗ ಲಭ್ಯವಿಲ್ಲ. ದಯವಿಟ್ಟು ಬೆಳೆ ಮತ್ತು ರಾಜ್ಯದ ಹೆಸರನ್ನು ಕಳುಹಿಸಿ.",
        "ml": "സ്ഥിരീകരിച്ച മണ്ഡി വില ഇപ്പോൾ ലഭ്യമല്ല. വിളയും സംസ്ഥാനവും അയയ്ക്കുക.",
        "gu": "ચકાસાયેલ મંડી ભાવ હાલમાં ઉપલબ્ધ નથી. કૃપા કરીને પાક અને રાજ્ય મોકલો.",
    },
    "market_price_source_unavailable": {
        "hi": "⚠️ *{commodity}* के लिए *{state}* का सत्यापित मंडी भाव अभी सरकारी स्रोत से नहीं मिल पा रहा है। कृपया कुछ मिनट बाद फिर प्रयास करें, या सबसे सटीक खोज के लिए मंडी का नाम भेजें।",
        "en": "⚠️ The verified mandi-price source for *{commodity}* in *{state}* is temporarily unavailable. Please try again in a few minutes, or send the mandi name for a more precise lookup.",
        "bn": "⚠️ *{state}*-এ *{commodity}* এর যাচাইকৃত মণ্ডি দর এখন সরকারি উৎসে পাওয়া যাচ্ছে না। কয়েক মিনিট পরে আবার চেষ্টা করুন, অথবা নির্দিষ্ট মণ্ডির নাম পাঠান।",
        "mr": "⚠️ *{state}* मधील *{commodity}* चा सत्यापित मंडी भाव सध्या सरकारी स्रोतावर उपलब्ध नाही. काही मिनिटांनी पुन्हा प्रयत्न करा.",
        "pa": "⚠️ *{state}* ਵਿੱਚ *{commodity}* ਦਾ ਪ੍ਰਮਾਣਿਤ ਮੰਡੀ ਭਾਅ ਇਸ ਵੇਲੇ ਸਰਕਾਰੀ ਸਰੋਤ ਤੋਂ ਉਪਲਬਧ ਨਹੀਂ ਹੈ। ਕੁਝ ਮਿੰਟ ਬਾਅਦ ਮੁੜ ਕੋਸ਼ਿਸ਼ ਕਰੋ।",
        "ta": "⚠️ *{state}* இல் *{commodity}* க்கான சரிபார்க்கப்பட்ட மண்டி விலை தற்போது அரசு மூலத்தில் கிடைக்கவில்லை. சில நிமிடங்களுக்குப் பிறகு முயற்சிக்கவும்.",
        "te": "⚠️ *{state}* లో *{commodity}* ధృవీకరించిన మండీ ధర ప్రస్తుతం ప్రభుత్వ మూలం నుండి అందుబాటులో లేదు. కొన్ని నిమిషాల తర్వాత మళ్లీ ప్రయత్నించండి.",
        "or": "⚠️ *{state}* ରେ *{commodity}* ର ଯାଞ୍ଚ ହୋଇଥିବା ମଣ୍ଡି ଦର ଏବେ ସରକାରୀ ଉତ୍ସରେ ମିଳୁନାହିଁ। କିଛି ମିନିଟ ପରେ ପୁଣି ଚେଷ୍ଟା କରନ୍ତୁ।",
        "kn": "⚠️ *{state}* ದಲ್ಲಿ *{commodity}* ಪರಿಶೀಲಿತ ಮಂಡಿ ಬೆಲೆ ಈಗ ಸರ್ಕಾರಿ ಮೂಲದಿಂದ ಲಭ್ಯವಿಲ್ಲ. ಕೆಲವು ನಿಮಿಷಗಳ ನಂತರ ಮತ್ತೆ ಪ್ರಯತ್ನಿಸಿ.",
        "ml": "⚠️ *{state}* ൽ *{commodity}* ന്റെ സ്ഥിരീകരിച്ച മണ്ഡി വില ഇപ്പോൾ സർക്കാർ ഉറവിടത്തിൽ ലഭ്യമല്ല. കുറച്ച് മിനിറ്റുകൾക്ക് ശേഷം വീണ്ടും ശ്രമിക്കുക.",
        "gu": "⚠️ *{state}* માં *{commodity}* નો ચકાસાયેલ મંડી ભાવ હાલમાં સરકારી સ્ત્રોત પરથી ઉપલબ્ધ નથી. થોડી મિનિટ પછી ફરી પ્રયાસ કરો.",
    },
    "available_crops": {
        "hi": "🌾 *{state}* में आज मंडी रिपोर्ट में उपलब्ध फसलें:\n{crops}\n\nइनमें से किसी का भाव पूछें, जैसे: '{example} का भाव {state} में'।",
        "en": "🌾 Crops available in today's mandi report for *{state}*:\n{crops}\n\nAsk for a price, for example: '{example} price in {state}'.",
        "mr": "🌾 *{state}* मधील आजच्या मंडी अहवालात उपलब्ध पिके:\n{crops}\n\nयापैकी एखाद्या पिकाचा भाव विचारा, उदा.: '{example} चा भाव {state} मध्ये'।",
        "pa": "🌾 *{state}* ਦੀ ਅੱਜ ਦੀ ਮੰਡੀ ਰਿਪੋਰਟ ਵਿੱਚ ਉਪਲਬਧ ਫਸਲਾਂ:\n{crops}\n\nਇਨ੍ਹਾਂ ਵਿੱਚੋਂ ਕਿਸੇ ਦਾ ਭਾਅ ਪੁੱਛੋ, ਜਿਵੇਂ: '{example} ਦਾ ਭਾਅ {state} ਵਿੱਚ'।",
        "ta": "🌾 *{state}* இன்றைய மண்டி அறிக்கையில் கிடைக்கும் பயிர்கள்:\n{crops}\n\nஇதில் ஒன்றின் விலையைக் கேளுங்கள், உதாரணம்: '{example} விலை {state}'।",
        "te": "🌾 *{state}* నేటి మండీ నివేదికలో అందుబాటులో ఉన్న పంటలు:\n{crops}\n\nవీటిలో దేని ధర అయినా అడగండి, ఉదాహరణకు: '{example} ధర {state} లో'।",
        "bn": "🌾 *{state}* আজকের মণ্ডি রিপোর্টে উপলব্ধ ফসল:\n{crops}\n\nএগুলির যেকোনোটির দাম জিজ্ঞাসা করুন, যেমন: '{example}-এর দাম {state}-এ'।",
        "or": "🌾 *{state}* ରେ ଆଜିର ମଣ୍ଡି ରିପୋର୍ଟରେ ଉପଲବ୍ଧ ଫସଲଗୁଡ଼ିକ:\n{crops}\n\nଏଥିରୁ କୌଣସି ଫସଲର ଦର ପଚାରନ୍ତୁ, ଯେପରି: '{example} ଦର {state} ରେ'।",
        "kn": "🌾 *{state}* ನ ಇಂದಿನ ಮಂಡಿ ವರದಿಯಲ್ಲಿ ಲಭ್ಯವಿರುವ ಬೆಳೆಗಳು:\n{crops}\n\nಇವುಗಳಲ್ಲಿ ಯಾವುದಾದರೂ ಬೆಳೆಯ ಬೆಲೆ ಕೇಳಿ, ಉದಾಹರಣೆ: '{example} ಬೆಲೆ {state} ನಲ್ಲಿ'।",
        "ml": "🌾 *{state}* ഇന്നത്തെ മണ്ടി റിപ്പോർട്ടിൽ ലഭ്യമായ വിളകൾ:\n{crops}\n\nഇവയിൽ ഏതെങ്കിലും വിളയുടെ വില ചോദിക്കൂ, ഉദാഹരണം: '{example} വില {state} ൽ'।",
        "gu": "🌾 *{state}* ના આજના મંડી રિપોર્ટમાં ઉપલબ્ધ પાકો:\n{crops}\n\nઆમાંથી કોઈપણ પાકનો ભાવ પૂછો, જેમ કે: '{example} નો ભાવ {state} માં'।",
        "as": "🌾 *{state}* ৰ আজিৰ মাণ্ডী ৰিপ’ৰ্টত উপলব্ধ শস্য:\n{crops}\n\nইয়াৰ যিকোনো শস্যৰ দাম সুধিব পাৰে, যেনে: '{example} ৰ দাম {state} ত'।",
        "ur": "🌾 *{state}* کی آج کی منڈی رپورٹ میں دستیاب فصلیں:\n{crops}\n\nان میں سے کسی فصل کی قیمت پوچھیں، مثلاً: '{example} کی قیمت {state} میں'۔",
    },
    "available_crops_unavailable": {
        "hi": "अभी *{state}* की आज की मंडी-रिपोर्ट नहीं मिल पा रही है। कृपया कुछ मिनट बाद फिर पूछें।",
        "en": "Today's mandi report for *{state}* is temporarily unavailable. Please try again in a few minutes.",
        "mr": "*{state}* चा आजचा मंडी अहवाल सध्या उपलब्ध नाही. कृपया काही मिनिटांनी पुन्हा प्रयत्न करा।",
        "pa": "*{state}* ਦੀ ਅੱਜ ਦੀ ਮੰਡੀ ਰਿਪੋਰਟ ਇਸ ਵੇਲੇ ਉਪਲਬਧ ਨਹੀਂ ਹੈ। ਕੁਝ ਮਿੰਟ ਬਾਅਦ ਦੁਬਾਰਾ ਕੋਸ਼ਿਸ਼ ਕਰੋ।",
        "ta": "*{state}* இன்றைய மண்டி அறிக்கை தற்போது கிடைக்கவில்லை. சில நிமிடங்களுக்குப் பிறகு முயற்சிக்கவும்।",
        "te": "*{state}* నేటి మండీ నివేదిక ప్రస్తుతం అందుబాటులో లేదు. కొన్ని నిమిషాల తర్వాత మళ్లీ ప్రయత్నించండి।",
        "bn": "*{state}* আজকের মণ্ডি রিপোর্ট এখন পাওয়া যাচ্ছে না। কয়েক মিনিট পরে আবার চেষ্টা করুন।",
        "or": "*{state}* ର ଆଜିର ମଣ୍ଡି ରିପୋର୍ଟ ଏବେ ମିଳୁନାହିଁ। ଦୟାକରି କିଛି ମିନିଟ ପରେ ପୁଣି ପଚାରନ୍ତୁ।",
        "kn": "*{state}* ನ ಇಂದಿನ ಮಂಡಿ ವರದಿ ಈಗ ಲಭ್ಯವಿಲ್ಲ. ಕೆಲವು ನಿಮಿಷಗಳ ನಂತರ ಮತ್ತೆ ಪ್ರಯತ್ನಿಸಿ।",
        "ml": "*{state}* ഇന്നത്തെ മണ്ടി റിപ്പോർട്ട് ഇപ്പോൾ ലഭ്യമല്ല. കുറച്ച് മിനിറ്റുകൾക്ക് ശേഷം വീണ്ടും ശ്രമിക്കുക।",
        "gu": "*{state}* નો આજનો મંડી રિપોર્ટ હાલમાં ઉપલબ્ધ નથી. કૃપા કરીને થોડી મિનિટ પછી ફરી પ્રયાસ કરો।",
        "as": "*{state}* ৰ আজিৰ মাণ্ডী ৰিপ’ৰ্ট এতিয়া উপলব্ধ নহয়। কেইমিনিটমান পিছত পুনৰ চেষ্টা কৰক।",
        "ur": "*{state}* کی آج کی منڈی رپورٹ فی الحال دستیاب نہیں ہے۔ چند منٹ بعد دوبارہ کوشش کریں۔",
    },
    "voice_service_unavailable": {
        "hi": "माफ़ कीजिए, मैं आपकी आवाज़ अभी समझ नहीं पाया। कृपया दोबारा साफ़ और धीरे बोलें, या टेक्स्ट संदेश भेजें।",
        "en": "Sorry, I could not understand the voice note. Please speak clearly and try again, or send a text message.",
        "bn": "দুঃখিত, আমি আপনার ভয়েস মেসেজটি পরিষ্কারভাবে বুঝতে পারিনি। দয়া করে শান্ত জায়গায় ধীরে ও স্পষ্টভাবে আবার বলুন, অথবা টেক্সট পাঠান।",
        "mr": "माफ करा, तुमचा आवाज स्पष्ट समजला नाही. कृपया शांत ठिकाणी हळू आणि स्पष्टपणे पुन्हा बोला किंवा मजकूर पाठवा.",
        "pa": "ਮਾਫ਼ ਕਰਨਾ, ਮੈਂ ਤੁਹਾਡਾ ਵੌਇਸ ਮੈਸੇਜ ਸਾਫ਼ ਨਹੀਂ ਸਮਝ ਸਕਿਆ। ਕਿਰਪਾ ਕਰਕੇ ਸ਼ਾਂਤ ਥਾਂ ਤੇ ਹੌਲੀ ਅਤੇ ਸਪੱਸ਼ਟ ਤੌਰ ਤੇ ਦੁਬਾਰਾ ਬੋਲੋ ਜਾਂ ਟੈਕਸਟ ਭੇਜੋ।",
        "ta": "மன்னிக்கவும், உங்கள் குரல் செய்தி தெளிவாகப் புரியவில்லை. அமைதியான இடத்தில் மெதுவாகவும் தெளிவாகவும் மீண்டும் பேசவும் அல்லது உரை அனுப்பவும்.",
        "te": "క్షమించండి, మీ వాయిస్ సందేశం స్పష్టంగా అర్థం కాలేదు. దయచేసి నిశ్శబ్ద ప్రదేశంలో నెమ్మదిగా, స్పష్టంగా మళ్లీ మాట్లాడండి లేదా టెక్స్ట్ పంపండి.",
        "or": "କ୍ଷମା କରନ୍ତୁ, ଆପଣଙ୍କ ଭଏସ୍ ମେସେଜ୍ ସ୍ପଷ୍ଟ ଭାବେ ବୁଝିପାରିଲି ନାହିଁ। ଦୟାକରି ଶାନ୍ତ ସ୍ଥାନରେ ଧୀରେ ଓ ସ୍ପଷ୍ଟ ଭାବେ ପୁଣି କୁହନ୍ତୁ କିମ୍ବା ଟେକ୍ସଟ୍ ପଠାନ୍ତୁ।",
        "kn": "ಕ್ಷಮಿಸಿ, ನಿಮ್ಮ ಧ್ವನಿ ಸಂದೇಶ ಸ್ಪಷ್ಟವಾಗಿ ಅರ್ಥವಾಗಲಿಲ್ಲ. ದಯವಿಟ್ಟು ಶಾಂತವಾದ ಸ್ಥಳದಲ್ಲಿ ನಿಧಾನವಾಗಿ ಮತ್ತು ಸ್ಪಷ್ಟವಾಗಿ ಮತ್ತೆ ಮಾತನಾಡಿ ಅಥವಾ ಪಠ್ಯ ಕಳುಹಿಸಿ.",
        "ml": "ക്ഷമിക്കണം, നിങ്ങളുടെ ശബ്ദസന്ദേശം വ്യക്തമായി മനസ്സിലായില്ല. ശാന്തമായ സ്ഥലത്ത് പതുക്കെയും വ്യക്തമായും വീണ്ടും പറയുക, അല്ലെങ്കിൽ ടെക്സ്റ്റ് അയയ്ക്കുക.",
        "gu": "માફ કરશો, તમારો વૉઇસ મેસેજ સ્પષ્ટ સમજાયો નથી. કૃપા કરીને શાંત જગ્યાએ ધીમે અને સ્પષ્ટ રીતે ફરી બોલો અથવા ટેક્સ્ટ મોકલો.",
    },
    "disease_result": {
        "hi": "🌿 *रोग जांच परिणाम*\nफसल: {crop}\nस्थिति: {disease}\nविश्वास: {confidence}%\n\n💊 *उपचार सुझाव:*\n{remedy}\n\n⚠️ यह प्रारंभिक photo screening है। दवा देने से पहले स्थानीय कृषि विशेषज्ञ से पुष्टि करें।",
        "en": "🌿 *Disease Check Result*\nCrop: {crop}\nCondition: {disease}\nConfidence: {confidence}%\n\n💊 *Recommended Remedy:*\n{remedy}\n\n⚠️ This is an initial photo screening. Confirm with a local agricultural expert before treatment.",
        "mr": "🌿 *रोग तपासणी निकाल*\nपीक: {crop}\nस्थिती: {disease}\nविश्वास: {confidence}%\n\n💊 *उपाय:*\n{remedy}",
        "pa": "🌿 *ਰੋਗ ਜਾਂਚ ਨਤੀਜਾ*\nਫ਼ਸਲ: {crop}\nਹਾਲਤ: {disease}\nਭਰੋਸਾ: {confidence}%\n\n💊 *ਸੁਝਾਅ:*\n{remedy}\n\n⚠️ ਇਹ ਸ਼ੁਰੂਆਤੀ ਫੋਟੋ ਜਾਂਚ ਹੈ। ਦਵਾਈ ਤੋਂ ਪਹਿਲਾਂ ਸਥਾਨਕ ਖੇਤੀ ਮਾਹਿਰ ਨਾਲ ਪੁਸ਼ਟੀ ਕਰੋ।",
        "ta": "🌿 *நோய் பரிசோதனை முடிவு*\nபயிர்: {crop}\nநிலை: {disease}\n\n💊 *பரிந்துரை:*\n{remedy}",
        "te": "🌿 *వ్యాధి పరీక్ష ఫలితం*\nపంట: {crop}\nస్థితి: {disease}\n\n💊 *సూచన:*\n{remedy}",
    },
    "ask_for_image": {
        "hi": "बीमारी की जांच के लिए कृपया पत्ते की एक साफ फोटो भेजें। 📷",
        "en": "To check for disease, please send a clear photo of the affected leaf. 📷",
        "mr": "रोग तपासणीसाठी कृपया पानाचा स्पष्ट फोटो पाठवा. 📷",
        "pa": "ਰੋਗ ਜਾਂਚ ਲਈ ਕਿਰਪਾ ਕਰਕੇ ਪੱਤੇ ਦੀ ਸਾਫ਼ ਫੋਟੋ ਭੇਜੋ। 📷",
        "ta": "நோயை பரிசோதிக்க தெளிவான இலை புகைப்படத்தை அனுப்பவும். 📷",
        "te": "వ్యాధిని పరీక్షించడానికి ఆకు యొక్క స్పష్టమైన ఫోటో పంపండి. 📷",
        "bn": "রোগ পরীক্ষা করতে আক্রান্ত পাতার একটি পরিষ্কার ছবি পাঠান। 📷",
        "or": "ରୋଗ ଯାଞ୍ଚ ପାଇଁ ପତ୍ରର ଏକ ସ୍ପଷ୍ଟ ଫଟୋ ପଠାନ୍ତୁ। 📷",
        "kn": "ರೋಗ ಪರೀಕ್ಷೆಗೆ ಬಾಧಿತ ಎಲೆಯ ಸ್ಪಷ್ಟ ಫೋಟೋ ಕಳುಹಿಸಿ. 📷",
        "ml": "രോഗം പരിശോധിക്കാൻ ബാധിച്ച ഇലയുടെ വ്യക്തമായ ചിത്രം അയയ്ക്കുക. 📷",
        "gu": "રોગ તપાસવા અસરગ્રસ્ત પાનનો સ્પષ્ટ ફોટો મોકલો. 📷",
    },
    "ask_photo_with_crop": {
        "hi": "📷 बीमारी जांच के लिए फोटो के साथ फसल का नाम भी लिखें, जैसे: 'टमाटर का पत्ता'। केवल एक पत्ते की साफ़, करीब से ली हुई फोटो भेजें।",
        "en": "📷 For disease screening, send the photo with the crop name, for example: 'tomato leaf'. Send one clear close-up photo of a single leaf.",
        "mr": "📷 रोग तपासणीसाठी फोटोसोबत पिकाचे नाव लिहा, उदा. 'टोमॅटोचे पान'. एका पानाचा स्पष्ट जवळून फोटो पाठवा.",
        "pa": "📷 ਰੋਗ ਜਾਂਚ ਲਈ ਫੋਟੋ ਨਾਲ ਫ਼ਸਲ ਦਾ ਨਾਮ ਲਿਖੋ, ਜਿਵੇਂ 'ਟਮਾਟਰ ਦਾ ਪੱਤਾ'। ਇੱਕ ਪੱਤੇ ਦੀ ਸਾਫ਼ ਨਜ਼ਦੀਕੀ ਫੋਟੋ ਭੇਜੋ।",
        "ta": "📷 நோய் பரிசோதனைக்கு புகைப்படத்துடன் பயிரின் பெயரையும் எழுதுங்கள்; உதாரணம்: 'தக்காளி இலை'. ஒரு இலையின் தெளிவான அருகாமை புகைப்படத்தை அனுப்புங்கள்.",
        "te": "📷 వ్యాధి పరీక్షకు ఫోటోతో పాటు పంట పేరు రాయండి, ఉదాహరణకు: 'టమాటా ఆకు'. ఒక ఆకు యొక్క స్పష్టమైన దగ్గరి ఫోటో పంపండి.",
    },
    "invalid_leaf_photo": {
        "hi": "📷 इस फोटो में समर्थित फसल का पत्ता स्पष्ट रूप से पहचान नहीं हो पाया। कृपया केवल एक पत्ते की करीब से, अच्छी रोशनी में और बिना धुंधली फोटो भेजें।",
        "pa": "📷 ਇਸ ਫੋਟੋ ਵਿੱਚ ਸਮਰਥਿਤ ਫ਼ਸਲ ਦਾ ਪੱਤਾ ਪੱਕੇ ਤੌਰ ਤੇ ਪਛਾਣਿਆ ਨਹੀਂ ਗਿਆ। ਕਿਰਪਾ ਕਰਕੇ ਇੱਕ ਪੱਤੇ ਦੀ ਨੇੜਿਉਂ, ਚੰਗੀ ਰੌਸ਼ਨੀ ਵਾਲੀ ਅਤੇ ਸਾਫ਼ ਫੋਟੋ ਭੇਜੋ।",
        "en": "📷 I could not confidently identify a supported crop leaf in this photo. Please send one close, well-lit, non-blurry photo of a single leaf.",
        "bn": "📷 এই ছবিতে পাতাটি পরিষ্কার দেখা যাচ্ছে না। একটি পাতার কাছ থেকে তোলা, আলোযুক্ত ও ঝাপসা নয় এমন ছবি পাঠান।",
        "or": "📷 ଏହି ଫଟୋରେ ପତ୍ର ସ୍ପଷ୍ଟ ଦେଖାଯାଉନାହିଁ। ଗୋଟିଏ ପତ୍ରର ନିକଟରୁ, ଭଲ ଆଲୋକରେ ଫଟୋ ପଠାନ୍ତୁ।",
        "kn": "📷 ಈ ಚಿತ್ರದಲ್ಲಿ ಎಲೆ ಸ್ಪಷ್ಟವಾಗಿ ಕಾಣುತ್ತಿಲ್ಲ. ಒಂದೇ ಎಲೆಯ ಹತ್ತಿರದ, ಚೆನ್ನಾಗಿ ಬೆಳಕಿರುವ ಫೋಟೋ ಕಳುಹಿಸಿ.",
        "ml": "📷 ഈ ചിത്രത്തിൽ ഇല വ്യക്തമായി കാണുന്നില്ല. ഒരു ഇലയുടെ അടുത്തുനിന്നുള്ള, നല്ല വെളിച്ചത്തിലുള്ള ചിത്രം അയയ്ക്കുക.",
        "gu": "📷 આ ફોટામાં પાન સ્પષ્ટ દેખાતું નથી. એક પાનનો નજીકથી, સારા પ્રકાશમાં લીધેલો ફોટો મોકલો.",
    },
    "crop_photo_mismatch": {
        "hi": "📷 यह फोटो *{crop}* के पत्ते जैसी पहचान नहीं हो रही है। कृपया खेत के असली {crop} पत्ते की करीब से फोटो भेजें—सफेद पृष्ठभूमि, स्क्रीनशॉट या इंटरनेट की sample photo नहीं।",
        "en": "📷 This photo does not appear to match a {crop} leaf. Please send a close-up photo of a real {crop} leaf from the field—not a white-background, screenshot, or internet sample image.",
        "pa": "📷 ਇਹ ਫੋਟੋ *{crop}* ਦੇ ਪੱਤੇ ਨਾਲ ਮੇਲ ਨਹੀਂ ਖਾਂਦੀ। ਕਿਰਪਾ ਕਰਕੇ ਖੇਤ ਦੇ ਅਸਲੀ {crop} ਪੱਤੇ ਦੀ ਨੇੜਿਉਂ ਫੋਟੋ ਭੇਜੋ—ਸਕ੍ਰੀਨਸ਼ਾਟ ਜਾਂ ਇੰਟਰਨੈੱਟ ਦੀ ਤਸਵੀਰ ਨਹੀਂ।",
    },
    "disease_crop_unsupported": {
        "hi": "अभी *{crop}* के रोग की जांच इस मॉडल में उपलब्ध नहीं है। कृपया वेबसाइट में दी गई समर्थित फसल चुनें या स्थानीय कृषि विशेषज्ञ से सलाह लें।",
        "en": "Disease screening for *{crop}* is not available in this model yet. Choose a crop supported on the website or consult a local agricultural expert.",
        "pa": "*{crop}* ਦੀ ਬਿਮਾਰੀ ਜਾਂਚ ਇਸ ਮਾਡਲ ਵਿੱਚ ਹਾਲੇ ਉਪਲਬਧ ਨਹੀਂ ਹੈ। ਕਿਰਪਾ ਕਰਕੇ ਸਮਰਥਿਤ ਫ਼ਸਲ ਦਾ ਨਾਮ ਲਿਖ ਕੇ ਮੁੜ ਫੋਟੋ ਭੇਜੋ।",
    },
    "unsupported_media": {
        "hi": "क्षमा करें, यह फ़ाइल प्रकार समर्थित नहीं है। कृपया टेक्स्ट, ऑडियो या फोटो भेजें।",
        "en": "Sorry, this file type isn't supported yet. Please send text, a voice note, or a photo.",
        "mr": "माफ करा, हा फाइल प्रकार सध्या समर्थित नाही.",
        "pa": "ਮਾਫ਼ ਕਰੋ, ਇਹ ਫਾਈਲ ਕਿਸਮ ਸਮਰਥਿਤ ਨਹੀਂ ਹੈ।",
        "ta": "மன்னிக்கவும், இந்த கோப்பு வகை ஆதரிக்கப்படவில்லை.",
        "te": "క్షమించండి, ఈ ఫైల్ రకం మద్దతు లేదు.",
    },
    "unknown_intent": {
        "hi": "मुझे समझ नहीं आया। आप फसल का भाव पूछ सकते हैं या पत्ते की फोटो भेज सकते हैं। 🌾",
        "en": "I didn't quite understand. You can ask for crop prices or send a leaf photo. 🌾",
        "mr": "मला समजले नाही. तुम्ही पिकाचा भाव विचारू शकता किंवा पानाचा फोटो पाठवू शकता. 🌾",
        "pa": "ਮੈਨੂੰ ਸਮਝ ਨਹੀਂ ਆਇਆ। ਤੁਸੀਂ ਫ਼ਸਲ ਦਾ ਭਾਅ ਪੁੱਛ ਸਕਦੇ ਹੋ। 🌾",
        "ta": "எனக்குப் புரியவில்லை. நீங்கள் பயிர் விலையைக் கேட்கலாம். 🌾",
        "te": "నాకు అర్థం కాలేదు. మీరు పంట ధర అడగవచ్చు. 🌾",
        "bn": "আমি বুঝতে পারিনি। আপনি ফসলের দাম জানতে বা পাতার ছবি পাঠাতে পারেন। 🌾",
        "or": "ମୁଁ ବୁଝିପାରିଲି ନାହିଁ। ଆପଣ ଫସଲ ଦର ପଚାରିପାରିବେ କିମ୍ବା ପତ୍ରର ଫଟୋ ପଠାଇପାରିବେ। 🌾",
        "kn": "ನನಗೆ ಅರ್ಥವಾಗಲಿಲ್ಲ. ಬೆಳೆ ಬೆಲೆ ಕೇಳಬಹುದು ಅಥವಾ ಎಲೆಯ ಫೋಟೋ ಕಳುಹಿಸಬಹುದು. 🌾",
        "ml": "എനിക്ക് മനസ്സിലായില്ല. വിളയുടെ വില ചോദിക്കുകയോ ഇലയുടെ ചിത്രം അയയ്ക്കുകയോ ചെയ്യാം. 🌾",
        "gu": "મને સમજાયું નથી. તમે પાકનો ભાવ પૂછી શકો અથવા પાનનો ફોટો મોકલી શકો છો. 🌾",
    },
    "processing_error": {
        "hi": "क्षमा करें, कुछ तकनीकी समस्या हुई है। कृपया थोड़ी देर बाद पुनः प्रयास करें।",
        "en": "Sorry, something went wrong on our end. Please try again in a moment.",
        "mr": "माफ करा, काहीतरी तांत्रिक अडचण आली. कृपया पुन्हा प्रयत्न करा.",
        "pa": "ਮਾਫ਼ ਕਰੋ, ਕੋਈ ਤਕਨੀਕੀ ਸਮੱਸਿਆ ਆਈ ਹੈ।",
        "ta": "மன்னிக்கவும், ஒரு தொழில்நுட்ப சிக்கல் ஏற்பட்டது.",
        "te": "క్షమించండి, సాంకేతిక సమస్య ఏర్పడింది.",
    },
}


def translate(key: str, lang: str, **kwargs) -> str:
    """Fetch a localized template and format it with kwargs. Falls back to English, then Hindi."""
    lang = normalize_language(lang, default=Language.ENGLISH.value)
    templates = MESSAGES.get(key, {})
    template = templates.get(lang) or templates.get("en") or templates.get("hi") or ""
    try:
        return template.format(**kwargs)
    except (KeyError, IndexError):
        return template

"""
Shared constants / enums used across the KrishiMitr backend.
"""
from enum import Enum


class Intent(str, Enum):
    MARKET_PRICE = "market_price"
    DISEASE_CHECK = "disease_check"
    WEATHER = "weather"
    GREETING = "greeting"
    UNSUPPORTED_MEDIA = "unsupported_media"
    UNKNOWN = "unknown"


class MediaCategory(str, Enum):
    AUDIO = "audio"
    IMAGE = "image"
    NONE = "none"
    UNSUPPORTED = "unsupported"


class Language(str, Enum):
    HINDI = "hi"
    ENGLISH = "en"
    MARATHI = "mr"
    PUNJABI = "pa"
    TAMIL = "ta"
    TELUGU = "te"
    BENGALI = "bn"
    ODIA = "or"
    KANNADA = "kn"
    MALAYALAM = "ml"
    GUJARATI = "gu"
    ASSAMESE = "as"
    URDU = "ur"


SUPPORTED_LANGUAGES = {l.value for l in Language}

# Canonical commodity names -> keyword variants (English + major Indian languages, transliterated)
COMMODITY_KEYWORDS = {
    "wheat": ["wheat", "gehu", "gehun", "गेहूं", "ਕਣਕ", "ਗੇਹੂੰ", "গম", "ଗହମ", "ಗೋಧಿ", "ഗോതമ്പ്", "ઘઉં"],
    "rice": ["rice", "paddy", "chawal", "dhan", "चावल", "धान", "ਚਾਵਲ", "ਝੋਨਾ", "ধান", "চাল", "ଧାନ", "ಅಕ್ಕಿ", "നെല്ല്", "ચોખા"],
    "cotton": ["cotton", "kapas", "कपास", "ਕਪਾਹ", "তুলা", "କପା", "ಹತ್ತಿ", "പരുത്തി", "કપાસ"],
    "onion": ["onion", "pyaz", "pyaaz", "प्याज", "ਪਿਆਜ਼", "পেঁয়াজ", "ପିଆଜ", "ಈರುಳ್ಳಿ", "ഉള്ളി", "ડુંગળી"],
    "tomato": ["tomato", "tamatar", "टमाटर", "ਟਮਾਟਰ", "ਟਮਾਟੇ", "টমেটো", "ଟମାଟୋ", "ಟೊಮೆಟೊ", "തക്കാളി", "ટામેટા"],
    "potato": ["potato", "aloo", "aaloo", "aalu", "आलू", "ਆਲੂ", "ਆਲੂਆਂ", "আলু", "ଆଳୁ", "ಆಲೂಗಡ್ಡೆ", "ഉരുളക്കിഴങ്ങ്", "બટાકા"],
    "soybean": ["soybean", "soyabean", "soya", "सोयाबीन", "সয়াবিন", "ସୋୟାବିନ୍", "ಸೋಯಾಬೀನ್", "സോയാബീൻ", "સોયાબીન"],
    "sugarcane": ["sugarcane", "ganna", "ganne", "गन्ना", "আখ", "ଆଖୁ", "ಕಬ್ಬು", "കരിമ്പ്", "શેરડી"],
    "maize": ["maize", "corn", "makka", "मक्का", "ਮੱਕੀ", "ਭੁੱਟਾ", "ভুট্টা", "ମକା", "ಮೆಕ್ಕೆಜೋಳ", "ചോളം", "મકાઈ"],
    "mustard": ["mustard", "sarson", "सरसों", "ਸਰ੍ਹੋਂ", "ਸਰਸੋਂ", "সরিষা", "ସୋରିଷ", "ಸಾಸಿವೆ", "കടുക്", "રાઈ"],
    # Common vegetables and fruits accepted by the live AGMARKNET price flow.
    # Include the Hindi/Hinglish spellings farmers naturally use on WhatsApp.
    "apple": ["apple", "seb", "सेब"],
    # Banana names as farmers write or say them in every supported language.
    # Romanized variants matter just as much as native-script variants on
    # WhatsApp (for example, "Odisha re Kadali Dara").
    "banana": [
        "banana", "kela", "kele", "केला", "केळी", "ਕੇਲਾ", "ਕੇਲੇ",
        "vaazhaipazham", "vazhaipazham", "வாழைப்பழம்",
        "aratipandu", "అరటిపండు", "kola", "kol", "কলা", "kadali", "କଦଳୀ",
        "balehannu", "ಬಾಳೆಹಣ್ಣು", "vazhappazham", "വാഴപ്പഴം",
        "કેળા", "কল", "کیلا",
    ],
    "bhindi": ["bhindi", "okra", "lady finger", "ladies finger", "भिंडी"],
    "bottle gourd": ["bottle gourd", "lauki", "ghiya", "लौकी", "घीया"],
    "brinjal": ["brinjal", "baingan", "eggplant", "बैंगन"],
    "cauliflower": ["cauliflower", "gobhi", "phool gobhi", "फूलगोभी", "गोभी"],
    "cucumber": ["cucumber", "kheera", "khira", "खीरा"],
    "lemon": ["lemon", "nimbu", "नींबू", "नीबू"],
    "papaya": ["papaya", "papita", "पपीता"],
    "pumpkin": ["pumpkin", "kaddu", "कद्दू"],
    "radish": ["radish", "mooli", "muli", "मूली"],
    "sponge gourd": ["sponge gourd", "tori", "torai", "तोरी"],
    # Additional crops covered by the bundled PlantVillage leaf-disease model.
    "grape": ["grape", "angoor", "अंगूर"],
    "orange": ["orange", "santra", "संतरा"],
    # Coffee is recognised so the assistant can clearly explain that it is
    # outside the bundled PlantVillage disease model, rather than incorrectly
    # treating a clear coffee photo as a poor-quality image.
    "coffee": ["coffee", "coffee leaf", "कॉफी", "ਕੌਫੀ"],
    "peach": ["peach", "aadu", "आड़ू"],
    "bell pepper": ["bell pepper", "capsicum", "shimla mirch", "शिमला मिर्च"],
    "cherry": ["cherry", "चेरी"],
    "blueberry": ["blueberry", "ब्लूबेरी"],
    "strawberry": ["strawberry", "स्ट्रॉबेरी"],
    "raspberry": ["raspberry", "रास्पबेरी"],
    "squash": ["squash", "स्क्वैश"],
}

DEFAULT_STATE = "Uttar Pradesh"

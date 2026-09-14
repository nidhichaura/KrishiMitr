# KrishiMitr — Complete Technical Analysis

**Evidence basis.** This report is derived from the checked-in source, configuration, scripts, tests, model checkpoint and project documentation in this repository. “Implemented” means it is in the code; “not specified” means it cannot be established from those sources. The supplied attachment contained the requested analysis format, not a separate project report.

## 1. Project overview

**Project name:** KrishiMitr.  
**Objective:** give Indian farmers a multilingual, voice-first assistant for (1) crop-leaf disease screening and (2) verified wholesale mandi-price lookup.  
**Problem solved:** farmers may have limited English literacy, intermittent smartphone access, and difficulty obtaining timely, trustworthy crop advice and prices.  
**Users:** Indian farmers using the mobile web site, WhatsApp, SMS, or a keypad-phone IVR.  
**Use case:** a farmer uploads/sends one clear leaf image for an initial disease screen, asks/speaks a price query such as “wheat price in Punjab,” and receives a response in their detected language.  
**Implemented features:** responsive website; WhatsApp text/audio/image webhook; SMS and Hindi DTMF IVR fallback; script-based Indic-language detection and templates; rule-based intent/entity extraction; official AGMARKNET price retrieval; trained EfficientNet-B0 image classification; image-quality/non-leaf/crop-match safeguards; Sarvam ASR/TTS integration; Twilio replies; health endpoint; Docker support; CORS, signature validation, input limits and rate limiting.

## 2. Complete technology stack

| Category | Technology | Where and why |
|---|---|---|
| Programming languages | Python 3.11 | FastAPI application, services, ML inference/training, tests and scripts. Docker base image is `python:3.11-slim`. |
| Programming languages | JavaScript (vanilla) | `app/static/app.js` drives forms, browser fetch calls, UI rendering and browser speech synthesis. |
| Programming languages | HTML/CSS | `index.html`, `style.css`, `i18n.js` implement the mobile-first interface and translated labels. |
| Front end | Vanilla DOM API, Fetch, FormData, Web Speech API | No React/Vue/Angular is used. Fetch sends the photo/price requests; `speechSynthesis` reads UI content aloud. |
| Backend | FastAPI 0.110, Uvicorn | ASGI API/server; routes are registered in `main.py`. |
| Backend/data validation | Pydantic 2, pydantic-settings | Internal request/result schemas and `.env`-backed typed settings. |
| ML/DL | PyTorch, Torchvision, EfficientNet-B0 | Training and local inference of the 38-class leaf-disease classifier; ImageNet general-object safety gate. |
| Computer vision | OpenCV, NumPy, Pillow | Decode, blur/leaf-quality validation, resize, BGR→RGB and normalisation. Pillow is installed; direct use is not established in source. |
| Messaging/telephony | Twilio Python SDK, TwiML, Twilio WhatsApp API | Validates inbound webhook signature; receives WhatsApp/SMS/voice calls; returns TwiML; optional outbound REST sender. |
| Speech AI | Sarvam Saaras v4 / Bulbul v3 APIs, HTTPX | Saaras transcribes WhatsApp voice notes; Bulbul generates MP3 replies. Requires API key; no mock transcript is emitted. |
| Market API | AGMARKNET 2.0 API; data.gov.in OGD API fallback | Returns state/mandi/day wholesale min, max and modal prices; the code refuses to invent a quote. |
| Security/network | CORS middleware, RequestValidator, HTTPX | Restricts configured browser origins, verifies `X-Twilio-Signature`, makes bounded-time outbound HTTP requests. |
| Deployment/dev tools | Docker, pip/venv, PowerShell, `unittest`, ngrok (documented) | Containerization, dependency installation, demo launcher, smoke tests, and optional public HTTPS tunnelling. |
| Database | **No database is implemented** | No ORM, SQL/NoSQL client, migration, table or persistent user/message store appears in the project. Filesystem stores model weights and short-lived generated audio. |

`Bhashini` appears as a configurable future/mock URL and a documented extension point. It is **not called by the implemented speech path**, which calls Sarvam.

## 3. AI / ML / DL

| Area | Status and exact technique |
|---|---|
| AI | Yes, in the broad sense: automated intent routing, ASR/TTS integrations and image-based decision support. |
| Machine learning | Yes: supervised image classification; transfer learning from ImageNet EfficientNet-B0 weights. |
| Deep learning | Yes: EfficientNet-B0 convolutional neural network (CNN) for leaf-disease multiclass classification. |
| Computer vision | Yes: OpenCV preprocessing/quality gates plus CNN inference; an ImageNet EfficientNet-B0 model rejects selected non-leaf objects. |
| NLP | Limited/rule-based NLP: keyword matching scores intents, extracts crop/state aliases, and script/marker-based language detection. No trained NLP classifier is implemented. |
| Generative AI | No LLM or generative-image/text model is implemented. Sarvam TTS generates speech audio from templated text, but that does not make the application a generative-AI project. |

### Disease model

| Item | Implemented detail |
|---|---|
| Model | `torchvision.models.efficientnet_b0`; checkpoint `weights/efficientnet_leaf_disease.pt`. |
| Algorithm type | Supervised, multiclass image classification / recognition. It does **not** detect bounding boxes or segment lesions. |
| Input | One JPG/PNG/WEBP leaf image, max 8 MB; classifier receives a 224×224 RGB float tensor, ImageNet-normalised. |
| Output | Top-1 PlantVillage class label, softmax confidence, healthy flag, inferred crop, and a configured bilingual remedy/disclaimer. |
| Classes | 38 checkpoint labels: Apple (4), Blueberry, Cherry (2), Corn/maize (4), Grape (4), Orange, Peach (2), bell pepper (2), Potato (3), Raspberry, Soybean, Squash, Strawberry (2), Tomato (10). |
| Preprocessing/features | Decode; reject too-small, blurry, low/high plant-coverage, or non-primary-leaf images; optional ImageNet object gate; resize 224²; 3×3 Gaussian blur; BGR→RGB; scale [0,1]; ImageNet mean/std normalisation. CNN learns visual features automatically. |
| Training | `ImageFolder` data; 80/20 deterministic split script (seed 42); train augmentation: resize 256, random resized crop 224, horizontal flip, ±12° rotation and color jitter; AdamW (LR `3e-4`, weight decay `1e-4`); cross-entropy loss; default 12 epochs; GPU if available; save checkpoint with best validation accuracy. |
| Testing/evaluation | Training script computes only training and validation accuracy each epoch. The repository has 43,447 train / 10,858 validation images across 38 classes. The actual achieved accuracy, F1, precision/recall, confusion matrix, held-out field-test results and test split are **not specified/published** (`training.log` is empty). README correctly requests these before accuracy claims. |
| Selection reason | EfficientNet-B0 offers pretrained ImageNet transfer learning and a compact standard 224×224 model, suitable for local CPU-capable inference. This rationale is documented; comparative experiment results are not specified. |
| Alternatives | MobileNetV3/EfficientNet-Lite for smaller mobile deployment; ResNet-50/ConvNeXt/ViT for alternatives; YOLO/Mask R-CNN only if lesion detection/segmentation is required; calibrated/OOD detector for safer field deployment. These are alternatives, not current components. |

**Important operational distinction:** a real 38-class checkpoint is present, so normal runtime can load `TrainedDiseaseClassifierModel`. If weights or optional dependencies fail, code falls back to a deterministic heuristic “mock EfficientNet” that uses greenness plus a SHA-256-derived class choice. That fallback is demo continuity, **not ML diagnosis**. The app also rejects classification confidence below 0.90.

## 4. Algorithms

| Algorithm | Category | Purpose | Input → Output | Location |
|---|---|---|---|---|
| EfficientNet-B0 + softmax | Deep supervised classification | Classify leaf condition | 224² RGB → 1 of 38 labels + probability | `disease_classifier.py` |
| ImageNet EfficientNet-B0 gate | General-object classification | Reject known non-leaf objects | image → ImageNet label/confidence → accept/reject | `vision_service.py` |
| OpenCV heuristic quality gate | Rule-based CV | Reject blurry/invalid/non-primary-leaf photos | pixels → validation error/accepted image | `validate_leaf_photo` |
| Gaussian blur, resize, colour conversion, normalisation | Image preprocessing | Prepare safe model tensor | image → normalised 224² RGB | `preprocess_image` |
| Keyword scoring | Rule-based NLP classification | Intent detection | text → market/disease/weather/greeting/unknown + score | `detect_intent` |
| Alias/string matching | Rule-based NER | Extract crop and state | text → canonical commodity/state | `extract_commodity`, `extract_state` |
| Unicode-script + marker matching | Rule-based language ID | Select language template | text → language code | `detect_user_language` |
| ASR (Saaras v4) | External speech recognition | Voice note → text | audio → transcript/language/confidence | `transcribe_audio` |
| TTS (Bulbul v3) | External speech synthesis | Spoken response | text/language → MP3 | `create_voice_reply` |
| Sliding-window deque | Rate limiting | Limit public API requests | client IP/timestamps → allow or HTTP 429 | `rate_limit.py` |

## 5. Project modules

| Module | Purpose / input / processing / output | Technologies and relationships |
|---|---|---|
| Web UI | Leaf photo/crop/language or market crop/state/mandi input; validates client choices and calls JSON endpoints; shows result. | HTML/CSS/JS/i18n; talks to `web.py`; links to WhatsApp. |
| Web API | Serves `/`, validates upload type/size, rate-limits requests, calls vision/market services. | FastAPI/Pydantic; bridge between browser and core services. |
| WhatsApp router | Processes Twilio form payload; routes text/audio/image/unsupported media; returns UTF-8 TwiML. | FastAPI, Twilio; orchestrates speech, vision, market, response, voice services. |
| SMS/IVR fallback | SMS uses text route; IVR presents a Hindi keypad menu and advice. | Twilio Messaging/Voice TwiML; shares webhook security/intent pipeline. |
| Speech/NLU | Audio transcription; language, intent, crop and state extraction. | Sarvam + HTTPX; rule-based NLP; feeds market/disease prompt routing. |
| Vision/ML | Validate photo, infer class, map disease to response/remedy. | OpenCV/NumPy/PyTorch/Torchvision; feeds response service. |
| Market | Query official live price feeds; optionally list today’s available commodities. | AGMARKNET/data.gov.in/HTTPX; feeds response/UI. |
| Response/localisation | Converts structured results into native-script template text. | Python templates; used by webhooks and web API response. |
| Media/audio | Downloads Twilio media to temporary file; makes/reclaims public MP3 replies. | HTTPX/filesystem/Sarvam; used by WhatsApp audio path. |
| Configuration/security | Loads environment config, logs, signatures, rate limits. | pydantic-settings, Twilio validator, CORS; shared by routes/services. |
| Training/data preparation | Makes split and trains/saves best checkpoint. | PyTorch/Torchvision/ImageFolder; produces model consumed by vision. |

## 6. System architecture and workflows

`Farmer → Web browser / WhatsApp / SMS / IVR → FastAPI → speech/vision/market service → local model or external API → response templates/TwiML or JSON → farmer`.

**Text/SMS price flow:** user enters text → language detector + keyword intent/entity extraction → require commodity and state → AGMARKNET 2.0 (then data.gov.in only if configured) → format mandi, variety, date, min/max/modal wholesale price → TwiML SMS/WhatsApp or web JSON.

**Leaf-photo flow:** browser uploads or Twilio media URL is downloaded → type/size checks (web) → OpenCV decode, object/quality/leaf checks → optional stated-crop match → local EfficientNet-B0 → reject <0.90 confidence → map label to remedy and expert disclaimer → JSON on web or localized TwiML response on WhatsApp.

**Voice-note flow:** Twilio audio → download → Sarvam Saaras request with agricultural keyterms → reject empty/<0.55 confidence transcript → rule-based text path → TwiML text plus Sarvam Bulbul MP3 when public URL/configuration are available.

**IVR flow:** incoming call → signature check → Hindi `<Gather>` menu → digit 1/2/3 gives an audio message; it does not perform speech recognition or leaf classification.

## 7. Database

**Technology/tables/relationships:** not specified because **no database exists**. The application does not persist accounts, chats, market records, diagnoses, or uploaded source images. In-memory state is only the per-IP rate-limit deque and cached AGMARKNET state-ID map. Filesystem data includes `weights/efficientnet_leaf_disease.pt`, dataset folders and temporary public audio files (max 100 / 24 hours). Backend–database communication is therefore not applicable.

## 8. Frontend

Vanilla responsive web UI at `/` with one primary page. Screens/sections: language selection, disease-upload form/result, mandi-price form/result, WhatsApp CTA and speaker controls. Disease form requires a photo; market form requires crop and state before fetch. Browser uses `FormData` POST to `/api/disease/analyze` and `fetch` GET to `/api/market/price`. Results render disease, crop, confidence, remedy/disclaimer or market values/source. Translations are client-side in `i18n.js`; state is DOM/form state only—no Redux, React state manager or frontend authentication. Server remains authoritative for MIME/8-MB validation and rate limit.

## 9. Backend and API surface

| Endpoint | Purpose |
|---|---|
| `GET /` | Render static farmer home page with configured WhatsApp link. |
| `GET /health` | JSON liveness status/timestamp. |
| `POST /api/disease/analyze` | Multipart image/crop/language; rate-limited; returns structured screening result. |
| `GET /api/market/price` | Commodity/state/optional mandi; rate-limited; returns verified price or 404. |
| `POST /webhook/whatsapp` | Twilio form webhook for text, photo or audio; returns TwiML. |
| `POST /webhook/sms` | Twilio SMS text route; returns TwiML. |
| `POST /webhook/ivr` | Hindi voice menu. |
| `POST /webhook/ivr/menu` | DTMF menu handler. |
| `GET /audio-replies/{file}` | Static public generated audio served for Twilio delivery. |

Business logic is service-based, with no auth/login or database layer. The backend communicates with ML via local Python method calls, and external systems through HTTPX/Twilio SDK.

## 10. AI/ML pipeline

`PlantVillage labelled folders → seeded 80/20 split → augmentation + ImageNet normalisation → pretrained EfficientNet-B0 fine-tuning → best validation-accuracy checkpoint → OpenCV photo gate → 224² normalised tensor → softmax top-1 prediction → confidence/crop/remedy guard → localized screening result.`

Data collection provenance beyond its PlantVillage-style folder structure is not specified. Feature extraction is automatic convolutional representation learning, not hand-engineered descriptors. Evaluation currently means validation accuracy only; F1/confusion matrix/field testing are not implemented or reported.

## 11. APIs and external services

| Service | Data exchanged | Use |
|---|---|---|
| Twilio WhatsApp | Form webhook in; TwiML text/media out; optional REST outbound message | Main conversational channel. |
| Twilio SMS/Voice | Form/DTMF in; Messaging/Voice TwiML out | Basic-phone fallback. |
| Sarvam Saaras | Audio file + model/language/keyterms → transcript/language/confidence | Voice-note ASR. |
| Sarvam Bulbul | Localised response text → base64 MP3 | Spoken WhatsApp reply. |
| AGMARKNET 2.0 | State/date/commodity → mandi market rows | Primary current wholesale price source. |
| data.gov.in OGD | Commodity/state/mandi/API key → historic/current record | Fallback source. |
| ngrok | Not application logic; documented HTTPS tunnel for local Twilio demos. |

## 12. Security

Implemented: Twilio HMAC signature validation (enabled by default); secret settings read from `.env`; configurable restrictive CORS; allow-list of image MIME types; 8-MB image cap; per-IP in-memory 20/minute default API limit; HTTP 403/413/415/422 errors; temporary-file cleanup; audio retention limit; no fabricated ASR/price output; model confidence/quality/crop safeguards; no credentials are hard-coded beyond safe mock defaults. No login, RBAC, JWT, sessions, password hashing, database encryption, malware scanning, antivirus, CSRF layer, audit store or distributed rate limiter is implemented. HTTPS is a deployment requirement, not enforced by code.

## 13. Folder/file structure

```text
main.py                         App creation, CORS, static mounts, routers
app/config.py                   Environment settings
app/core/constants.py           Enums, commodities
app/routes/                     Web, WhatsApp, SMS/IVR, health endpoints
app/services/                   Speech, vision, market, response, Twilio, TTS
app/ml_models/disease_classifier.py  Real/fallback model wrappers and remedies
app/models/schemas.py           Pydantic internal DTOs
app/utils/                      Language, media, logger, rate limiter
app/static/                     HTML, CSS, JS, UI translations
scripts/                        Dataset splitter and trainer
data/plant_disease/             38-class train/validation image folders
weights/                        EfficientNet checkpoint and Torch cache
tests/                          Public-surface/security smoke tests
README.md / TRAINING_GUIDE.md   Setup and ML operating documentation
Dockerfile                      Python 3.11 container definition
```

## 14. Technology → purpose (concise)

| Technology | Category | Purpose |
|---|---|---|
| FastAPI/Uvicorn | Backend | Serve APIs/webhooks/site |
| HTML/CSS/JS | Frontend | Mobile farmer UI |
| Pydantic | Validation/config | Typed settings and schemas |
| PyTorch/Torchvision | DL | Train/run EfficientNet-B0 |
| OpenCV/NumPy | CV | Validate/preprocess leaf photos |
| Twilio/TwiML | Communications | WhatsApp, SMS, IVR |
| Sarvam | Speech AI | ASR and TTS |
| AGMARKNET/data.gov.in | External data | Verified mandi quotes |
| Docker | Deployment | Portable backend runtime |

## 15. Module → technology → algorithm

| Module | Technology | Algorithm/model | Purpose |
|---|---|---|---|
| Disease screening | OpenCV, PyTorch | EfficientNet-B0 softmax classifier | Leaf condition prediction |
| Image safety | Torchvision/OpenCV | ImageNet classifier + CV heuristics | Avoid invalid/non-leaf result |
| Text understanding | Python/Unicode | Keyword scoring/alias matching | Intent, crop, state, language |
| Voice | Sarvam | Saaras ASR; Bulbul TTS | Speech in/out |
| Market | HTTPX | Deterministic official-record selection | Quote lookup |
| Channels | FastAPI/Twilio | Media-type routing/DTMF menu | Deliver interaction |

## 16. End-to-end working

1. Farmer opens the website or contacts the Twilio number.
2. The channel collects text, voice, or a leaf photo.
3. FastAPI validates the request; Twilio webhooks also require a valid signature.
4. Text/audio becomes text, language is selected, and rules determine user intent.
5. A price request queries an official government source and returns the exact source/date/mandi; absence returns an honest unavailable message.
6. A photo is checked for image safety and leaf quality, then locally classified; uncertain/mismatched photos are rejected.
7. The app creates a translated response with guidance and safety disclaimer.
8. The web UI displays JSON; Twilio receives TwiML, and voice-note users can receive an MP3 reply if Sarvam/public HTTPS is configured.

## 17. What makes it AI/ML/DL?

KrishiMitr is a **hybrid AI-enabled agriculture application**. Its leaf-disease capability is genuinely deep learning/CV when the supplied EfficientNet checkpoint loads. ASR/TTS are external AI services. Its text intent and language parts are conventional rules, not trained ML, and mandi lookup/WhatsApp/IVR are normal software integrations. It is not a generative-AI/LLM project. The heuristic fallback must be presented as demo mode, not as a trained disease model.

## 18. Technical interview / viva questions

### Basic (15)

1. **What is KrishiMitr?** A multilingual farmer assistant for initial leaf screening and verified mandi prices.
2. **Who uses it?** Indian farmers on web, WhatsApp, SMS or IVR.
3. **Which language is the backend written in?** Python.
4. **What framework is used?** FastAPI.
5. **What is a webhook here?** A Twilio HTTP call sent to the app when a message/call arrives.
6. **What does the disease feature take as input?** One clear leaf photograph.
7. **What does it return?** A condition label, confidence, crop guess, remedy text and disclaimer.
8. **What does mandi price mean here?** Wholesale market min, max and modal price per quintal.
9. **Which source supplies prices?** AGMARKNET 2.0, with optional data.gov.in fallback.
10. **Does the project have a database?** No implemented database.
11. **Which ML model is used?** EfficientNet-B0.
12. **What is computer vision?** Making software understand image content.
13. **What is confidence?** The model’s top-class softmax probability, not a guarantee of correctness.
14. **Why use local-language responses?** To reduce language/access barriers for farmers.
15. **Why is IVR included?** To provide a keypad-phone fallback.

### Technical (15)

1. **How is an image prepared?** Decode, validate, resize to 224×224, blur, RGB conversion and ImageNet normalisation.
2. **Which loss trains the classifier?** Cross-entropy loss.
3. **Which optimizer is used?** AdamW with `3e-4` LR and `1e-4` weight decay.
4. **How is the best checkpoint chosen?** Highest validation accuracy.
5. **What augmentation is used?** Random crop, flip, rotation and colour jitter.
6. **How are intents detected?** Counts multilingual keyword matches and selects highest score.
7. **How are crop/state entities found?** Canonical alias matching in the text.
8. **How is language detected?** Unicode script ranges plus Marathi/Assamese and Romanised-Hindi markers.
9. **How does WhatsApp reply?** FastAPI returns a TwiML `<Response><Message>` payload.
10. **How is a forged webhook blocked?** Twilio `RequestValidator` verifies `X-Twilio-Signature`.
11. **Why require state for a price?** It prevents silently returning a price from an arbitrary location.
12. **Why is a 0.90 threshold used?** To reject uncertain disease predictions.
13. **How does voice work?** Sarvam ASR turns audio into text; normal text routing runs; Sarvam TTS can make MP3.
14. **How is the public web API throttled?** Per-IP deque tracks requests in a rolling 60-second window.
15. **What is the fallback model?** A deterministic greenness/hash heuristic, used only if real weights cannot load.

### Difficult (10)

1. **Why is validation accuracy insufficient?** It can hide per-class failure, imbalance and domain shift; report F1, precision/recall, confusion matrix and field tests.
2. **What is PlantVillage domain shift?** Lab-style leaves may differ from farm photos in lighting, background, pests and mixed symptoms.
3. **Why use transfer learning?** ImageNet features reduce data/training needed compared with starting from random weights.
4. **Why is top-1 classification not detection?** It assigns a whole image one label; it does not locate diseased regions.
5. **What is a confidence limitation?** Softmax can be overconfident on out-of-distribution images, hence the quality/object gates and expert disclaimer.
6. **How would you make rate limiting production-ready?** Put limits in Redis/API gateway keyed by trusted identity/IP across all instances.
7. **What security issue does `PUBLIC_BASE_URL` solve?** It makes signature validation use the externally configured URL when a proxy changes the internal request URL.
8. **What data privacy improvement is needed?** Define consent/retention policy and avoid storing identifiers/media; use encrypted storage if persistence is added.
9. **Why is no mock transcript important?** A fabricated crop/state could create harmful advice or a false price result.
10. **How would you improve model deployment?** Field-data fine-tuning, calibration, OOD detector, per-class metrics, expert-reviewed remedies and monitoring.

## 19. Final technical summary

| Field | Summary |
|---|---|
| Project | KrishiMitr |
| Problem | Accessible, multilingual crop support and verified mandi information |
| Frontend | Static mobile-first HTML/CSS/vanilla JS |
| Backend | Python FastAPI/Uvicorn |
| Database | None implemented |
| Languages | Python, JavaScript, HTML, CSS |
| Frameworks | FastAPI, Pydantic, PyTorch/Torchvision, OpenCV |
| AI/ML/DL | CV/DL disease screening; external ASR/TTS; rule-based NLP |
| Algorithm/model | EfficientNet-B0 multiclass classifier; keyword intent logic |
| APIs | Twilio, Sarvam, AGMARKNET 2.0, optional data.gov.in |
| Modules | Web, WhatsApp, SMS/IVR, speech, vision, market, response, training |
| Authentication | No user auth; Twilio webhook-signature verification |
| Deployment | Docker; local Uvicorn; documented ngrok/HTTPS |
| Key features | Leaf screening, prices, multilingual response, voice, basic-phone fallback, safeguards |

# ONE-PAGE CHEAT SHEET

**Say this in viva:** “KrishiMitr is a Python FastAPI agriculture assistant for Indian farmers. Farmers use a mobile web page, WhatsApp, SMS or IVR. For a leaf photo, OpenCV first checks image quality, then a locally loaded PyTorch EfficientNet-B0 model classifies one of 38 PlantVillage disease/healthy labels. The input is resized to 224×224 RGB and ImageNet-normalised; the output is a label and softmax confidence. We reject low confidence below 0.90 and tell the farmer this is only an initial screen that needs expert confirmation. Training uses transfer learning, augmented ImageFolder data, AdamW, cross-entropy and best validation accuracy. The repository contains 43,447 train and 10,858 validation images, but final accuracy/F1 are not published.

For price questions, rule-based multilingual keywords extract intent, crop and state. The backend uses AGMARKNET 2.0 first and data.gov.in only as fallback, returning actual mandi, date and min/max/modal wholesale price. Voice notes use Sarvam Saaras ASR; replies can use Sarvam Bulbul TTS. Twilio provides WhatsApp/SMS/IVR and validates webhook signatures. There is no database, login or JWT. Security includes Twilio signatures, CORS, file type/8-MB checks, rate limiting and temporary-audio cleanup. This is a hybrid AI project: real CV/DL for disease classification, external speech AI, and normal rule-based software for intent/prices—not an LLM or generative-AI project.”

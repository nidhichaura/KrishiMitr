# KrishiMitr

A multilingual, voice-first AI assistant backend for Indian farmers, built on
FastAPI and the Twilio WhatsApp API.

It now also includes a mobile-first farmer website at `/`: upload one clear
leaf photo for an initial disease screen, view verified mandi prices, and get
a contextual crop-and-soil advisory from soil-test NPK, pH, location and a
short weather forecast.
continue the conversation on WhatsApp. The public API is rate-limited and
accepts JPG, PNG, and WEBP photos up to 8 MB.

Farmers message a WhatsApp number with **text, a voice note, or a photo of a
crop leaf**. The backend routes the message through the right pipeline —
speech-to-text + intent detection, computer-vision disease classification, or
live mandi price lookup — and replies in the farmer's own language.

## Architecture

```
Twilio WhatsApp  →  /webhook/whatsapp  →  route by media type
                                             ├─ audio → speech_service (ASR + intent)
                                             ├─ image → vision_service (OpenCV + CNN)
                                             └─ text  → speech_service (intent only)
                                                            │
                                             intent → market_service / disease result
                                                            │
                                             response_service → localized TwiML reply
```

The included EfficientNet leaf-disease model is trained on 38 PlantVillage
classes and runs locally. If its weights are missing, the application falls
back to a clearly logged demo classifier rather than failing at startup.
Mandi prices use the official public AGMARKNET 2.0 daily-report API first,
with the older data.gov.in feed retained as a fallback. The response always
shows the specific mandi and report date rather than inventing a price.

## Directory structure

```
KrishiMitr/
├── main.py                        # FastAPI app entrypoint
├── requirements.txt
├── .env.example
├── app/
│   ├── config.py                  # pydantic-settings, reads .env
│   ├── core/
│   │   └── constants.py           # Intent / MediaCategory / Language enums, commodity keywords
│   ├── models/
│   │   └── schemas.py             # Pydantic models shared across services
│   ├── ml_models/
│   │   └── disease_classifier.py  # EfficientNet-B0 leaf disease classifier
│   ├── routes/
│   │   ├── health.py              # GET /health
│   │   └── webhook.py             # POST /webhook/whatsapp — core routing logic
│   ├── services/
│   │   ├── speech_service.py      # Mock Bhashini/Sarvam ASR + keyword intent detection
│   │   ├── vision_service.py      # OpenCV preprocessing + CNN inference
│   │   ├── market_service.py      # Official AGMARKNET mandi price lookup
│   │   ├── response_service.py    # Builds the final localized message
│   │   └── twilio_service.py      # REST client for proactive/outbound messages
│   └── utils/
│       ├── language_utils.py      # Script-based language detection + message templates
│       ├── media_utils.py         # Twilio media download / temp-file handling
│       └── logger.py              # Centralized logger factory
```

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env               # fill in real Twilio creds when you have them
```

## Run locally

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Visit `http://localhost:8000/` for the farmer website, `http://localhost:8000/docs`
for interactive API docs, or `http://localhost:8000/health` for a liveness check.

### Container deployment

```bash
docker build -t krishimitr .
docker run --env-file .env -p 8000:8000 krishimitr
```

The Docker image includes the inference dependencies; keep `weights/` alongside
the source so the trained checkpoint is copied into the image.

## Public launch checklist

1. Copy `.env.example` to `.env`, set real Twilio/Sarvam credentials and a
   public `PUBLIC_BASE_URL`.
2. Set `CORS_ORIGINS` to your deployed HTTPS domain and keep
   `VERIFY_TWILIO_SIGNATURES=true`. It protects the WhatsApp webhook from
   forged requests.
3. Deploy behind HTTPS, then configure the exact
   `https://your-domain/webhook/whatsapp` URL in the Twilio Console.
4. Measure and publish validation accuracy, F1 score, and a confusion matrix
   from a held-out field-like test set before making accuracy claims.

## Wiring up Twilio's WhatsApp Sandbox

1. Expose your local server publicly, e.g. with ngrok:
   ```bash
   ngrok http 8000
   ```
2. In the [Twilio Console](https://console.twilio.com) → Messaging →
   Try it out → **WhatsApp Sandbox**, set **"WHEN A MESSAGE COMES IN"** to:
   ```
   https://<your-ngrok-domain>/webhook/whatsapp
   ```
3. Join the sandbox from your phone (send the `join <code>` message Twilio
   gives you), then message it — text, a voice note, or a leaf photo.

## Testing without Twilio

Since the webhook just needs standard form-encoded POST data, you can hit it
directly with curl:

```bash
# Text message — market price query
curl -X POST http://localhost:8000/webhook/whatsapp \
  -d "From=whatsapp:+919876543210" \
  -d "To=whatsapp:+14155238886" \
  -d "Body=what is the price of wheat" \
  -d "NumMedia=0"

# Text message — Hindi greeting
curl -X POST http://localhost:8000/webhook/whatsapp \
  -d "From=whatsapp:+919876543210" \
  -d "To=whatsapp:+14155238886" \
  -d "Body=namaste" \
  -d "NumMedia=0"
```

Both return a TwiML `<Response><Message>...</Message></Response>` payload —
exactly what Twilio expects back.

To exercise the image/audio pipelines without a live Twilio account, call
`app.services.vision_service.analyze_leaf_image(image_bytes, lang=...)` or
`app.services.speech_service.transcribe_audio(audio_bytes)` directly with
local file bytes in a Python shell. Image analysis runs locally; voice
transcription needs a configured Sarvam API key.

## External-service integration

The following components can be configured or extended independently:

| Component | File | Integration |
|---|---|---|
| ASR + language ID | `app/services/speech_service.py` | Bhashini / Sarvam AI speech API |
| Leaf disease CNN | `app/ml_models/disease_classifier.py` | Included trained EfficientNet-B0; retrain with `scripts/train_disease_model.py` |
| Mandi prices | `app/services/market_service.py` | Government of India OGD/AGMARKNET API |

The calling code (`vision_service`, `webhook.py`, `response_service`) is
already written against the final interfaces (`predict()`,
`fetch_market_price()`, `transcribe_audio()`), so swapping the internals
doesn't require touching any routing logic.

## Voice-note input and spoken replies

Voice notes use Sarvam Saaras speech-to-text and replies use Sarvam Bulbul
text-to-speech. Add these values to `.env` before testing voice notes:

```env
SARVAM_API_KEY=your_sarvam_api_key
PUBLIC_BASE_URL=https://your-ngrok-domain.ngrok-free.app
```

`PUBLIC_BASE_URL` must be the same public HTTPS tunnel used for the Twilio
webhook. A farmer who sends a voice note then receives both the text response
and a playable audio reply. If the key/service is unavailable, the app asks the
farmer to repeat the message rather than fabricating a transcript.

## Consent-first pilot and business foundation

The farmer website includes an optional personalised-advisory interest form.
It stores a one-way identifier, stated location/language and an explicit
opt-in choice in SQLite. It does not store phone numbers, messages or uploaded
leaf photos in the business database. Partner reporting returns only aggregate
counts after the configured minimum cohort and needs a bearer token.

The pilot foundation does not create a real payment, yield forecast, telecom
zero-rating or partner contract. Those require an external payment provider, a
validated agronomic model with local farm/weather data, and formal agreements.

### Pilot configuration

1. Set a strong `PARTNER_API_TOKEN` and a production `BUSINESS_DB_PATH` in
   `.env`. Leave the partner endpoint disabled until that token exists.
2. Start the service and let a test farmer submit the optional pilot form at
   `/`. Confirm that the partner endpoint requires the bearer token and returns
   only grouped data.
3. Use the aggregated metrics with a named FPO, NGO, government department,
   insurer or input-company pilot. Do not present a partnership as active until
   a written agreement exists.
4. Add a payment provider and a verified agronomist workflow before charging
   for personalised advisory. A plan request is only an interest record.

## Notes / known limitations

- Set `DATA_GOV_API_KEY` in `.env` before enabling mandi quotes. Results are
  wholesale minimum/maximum/modal prices for the returned state, mandi, variety,
  and data date; they are not retail prices or a price forecast.
- The disease model supports the 38 PlantVillage classes in the included
  checkpoint. The WhatsApp flow currently accepts tomato, potato, maize, and
  soybean labels; other crop support can be added by extending the crop map.
  The app rejects blurry, non-leaf-like, and low-confidence images rather than
  assigning an uncertain disease label. It remains an initial screening tool;
  confirm treatment with a local agricultural expert.
- `CROP_FROM_LABEL` in `disease_classifier.py` maps the `"Healthy"` label to
  `crop_guess="Unknown"` (it only splits labels containing `"___"`) — worth
  special-casing if you want a crop name shown on healthy results too.

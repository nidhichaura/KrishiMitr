# KrishiMitr Exotel IVR setup

## What the IVR does

1. A farmer calls the Exotel trial number.
2. Exotel plays the KrishiMitr language menu: **1 English, 2 Hindi, 3 another
   Indian language**.
3. The farmer speaks a state, then a crop.
4. The speech-to-text result is sent to KrishiMitr.
5. KrishiMitr uses the official AGMARKNET source and speaks the mandi quote.

Do not store a personal mobile number in source code. In the Exotel Dashboard,
add the desired verified trial recipient/agent number only where Exotel asks
for it. Keep Exotel API credentials in `.env`, never in a screenshot or Git.

## Before creating the flow

1. Rotate any Exotel API key or token that was pasted into chat.
2. Run KrishiMitr and expose it with a public HTTPS URL (ngrok for testing).
3. Set `EXOTEL_PUBLIC_BASE_URL` in `.env` to that exact base URL and restart
   the server.
4. Confirm `https://YOUR-URL/health` returns JSON with `"status":"ok"`.

## Exotel Dashboard flow

Create an **incoming voice flow** and attach it to your trial ExoPhone.

1. Add a **Passthru/ExoML** applet as the first applet, using GET:

   `https://YOUR-URL/webhook/exotel/ivr/start`

   This returns the language DTMF menu.
2. The language callback is built into the returned ExoML and reaches
   `/webhook/exotel/ivr/language`.
3. After language selection, add an **Exotel Voicebot** or **AgentStream**
   stage to collect the farmer's spoken state in the selected language.
4. Configure its completion callback to call:

   `https://YOUR-URL/webhook/exotel/ivr/state?call_id={{callsid}}&language={{language}}`

   Include the transcript as `transcript` (or map it to one of `speech`,
   `SpeechResult`, `utterance`, or `text`).
5. Add a second Voicebot/AgentStream stage for the spoken crop. Its callback:

   `https://YOUR-URL/webhook/exotel/ivr/crop?call_id={{callsid}}&language={{language}}&state={{state}}`

   Again map the recognized result to `transcript`.

The exact placeholders and transcript mapping names are chosen in your Exotel
Voicebot/AgentStream UI. The KrishiMitr endpoints accept several common field
names, but the Exotel flow must preserve the detected state into the crop step.
Ask Exotel support to enable/configure Voicebot or AgentStream for live Indian
language speech recognition if it is not visible in your account.

## Test without an Exotel call

Use the interactive API docs at `/docs` after starting the app. You can call:

`/webhook/exotel/ivr/state?transcript=उत्तर प्रदेश`

and then:

`/webhook/exotel/ivr/crop?state=Uttar+Pradesh&transcript=गेहूं`

Both return ExoML XML. The second endpoint will speak a quote only when the
official source has a verified record.

## SMS

Indian promotional/service SMS needs DLT sender/template compliance. Do not
promise a free public SMS fallback until the Exotel account has an approved DLT
entity, header, and template. The IVR flow above is independent of SMS.

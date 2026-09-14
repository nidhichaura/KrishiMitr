# KrishiMitr Hackathon Runbook

## One day before the event

1. Keep the project folder, `.venv`, `weights/efficientnet_leaf_disease.pt`,
   and two or three clear leaf photos on the laptop. The local disease model
   works without internet; do not depend on a downloaded image during the demo.
2. Verify the app once:

   ```powershell
   .\.venv\Scripts\python.exe -m unittest discover -s tests -v
   ```

3. Charge the laptop, carry the charger, and keep a phone hotspot ready.
   Internet is required for live mandi prices, Sarvam voice replies, and
   WhatsApp/Twilio. It is not required for the website or local photo model.
4. Set real values in `.env`: `TWILIO_*`, `SARVAM_API_KEY`, `PUBLIC_BASE_URL`,
   `PUBLIC_WHATSAPP_NUMBER`, and your deployed `CORS_ORIGINS`. Never show the
   `.env` file on the projector.
5. Deploy the app to an HTTPS domain before the event and set the exact URL
   `https://your-domain/webhook/whatsapp` in the Twilio WhatsApp Sandbox.
   Keep `VERIFY_TWILIO_SIGNATURES=true` in production.

## At the venue, after the laptop is turned on

Open PowerShell in this folder and run:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\START_DEMO.ps1
```

The script waits until the new server is healthy before opening the browser.
It opens `http://127.0.0.1:8000`; if an old server already uses that port, it
automatically uses `http://127.0.0.1:8010` so you never accidentally show an
outdated version. Keep the server PowerShell window open.

## Suggested 90-second demo

1. Say: “Farmers should not need to read English or learn an app.” Show the
   two large buttons and press the speaker icon.
2. Press **पत्ते की फोटो लें**, choose a prepared real leaf photo, and show
   the confidence, guidance, and expert-confirmation warning.
3. Press **आज का मंडी भाव**, choose a crop and state, and show the official
   price source and date. Use the hotspot first so this remains live.
4. Send a Hindi WhatsApp message or voice note to the Twilio number and show
   the same assistant on a phone.
5. If you have provisioned a voice-capable Twilio number, call it from a
   keypad phone and press **1** to demonstrate the Hindi IVR fallback. Explain
   that basic phones use call/SMS, while WhatsApp photo diagnosis needs a
   smartphone.
5. Close by saying: “The web app makes the service discoverable; WhatsApp
   keeps it usable for farmers who already know messaging.”

## If internet fails

Do not claim a live mandi quote. Demonstrate the local leaf-photo flow and
show the UI's honest unavailable-state for mandi/voice. This is better than
showing fabricated data.

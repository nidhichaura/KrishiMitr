# Business Model Implementation Status

This document maps the business-model slide to the product. It separates
software delivered in this repository from items that require a real external
agreement or regulated operational process.

## B2G Partnerships

Implemented: farmers can use web, WhatsApp, SMS and Hindi IVR; the pilot API
captures opt-in profile fields and supplies anonymised aggregate uptake metrics
to an authorised partner endpoint.

Still required outside code:

1. Choose one district/FPO pilot and define the target farmer cohort.
2. Sign a written pilot/MoU with the department, FPO or NGO. This is the only
   basis for claiming a government partnership or subsidised access.
3. Configure the partner's public WhatsApp/SMS/IVR number and deploy the app
   over HTTPS. Use real Twilio/Sarvam credentials in `.env`.
4. Run the pilot, measure opt-ins, completed disease screens, mandi lookups and
   farmer feedback. Use those actual metrics in any pitch.

## B2B Data Licensing

Implemented: a consent-first SQLite pilot store; one-way farmer identifiers;
minimum-cohort aggregation; token-protected partner insights. The service never
returns phone numbers, individual profiles, message text or leaf photos.

Still required outside code:

1. Write and publish consent text, privacy policy, retention/deletion policy
   and partner data-processing agreement.
2. Obtain legal/privacy review before sharing any aggregate report externally.
3. Build and validate the agronomic data model before claiming predictive
   insights. This repository has no yield model or ground-truth farm outcomes.
4. Use a managed encrypted database, role-based partner access and audit logs
   before production. SQLite is for the hackathon pilot only.

## B2C Freemium

Implemented: disease screening and verified mandi prices remain free. Farmers
can submit an interest request for a future personalised-advisory service.

Still required outside code:

1. Add a payment provider, GST/invoicing process and cancellation/refund flow.
2. Add authenticated accounts and a farmer-facing consent/history screen.
3. Provide a qualified agronomist escalation workflow.
4. Train and validate a location-aware yield forecast before advertising it.
   Do not convert a demand/request form into a paid forecast claim.

## Telecom Partnerships

Implemented: WhatsApp, SMS and keypad-phone IVR offer multi-channel access.

Still required outside code:

1. Approach a telecom operator's rural, CSR or innovation team with the pilot
   plan and uptake metrics.
2. Agree the commercial and technical zero-rating arrangement in writing.
3. Implement and test any operator-specific allow-list, charging and reporting
   integration after the operator provides its interface.

No code change can truthfully claim that access is zero-rated until an operator
has provisioned and tested it.

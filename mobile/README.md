# ROBIN Companion

Standalone Android/Expo source for the first ROBIN mobile interface.

## Run locally

1. Install Node.js and the Expo-compatible dependencies for this SDK.
2. From this directory, run `npm install` and then `npm start`.
3. Open the QR code with Expo Go.

This first screen is intentionally local-only. It does not pair with Windows, forward commands, store conversation history, or place calls. It reports those states explicitly. The Windows runtime and secure pairing flow are separate work; outbound calls remain disabled until Twilio is connected.

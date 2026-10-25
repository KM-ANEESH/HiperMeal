# HiperMeal phone test — version 0.3

Install HiperMeal-phone-test.apk on Android 8 or newer. Copy it by USB or open the temporary LAN download link while phone and laptop are on the same Wi-Fi. Android may ask you to allow installation from your browser or file manager. The package is locally signed for testing, not a Play Store release.

After installation, no laptop is required. Create your profile in Profile & connections. Diary, targets, water, workouts, weight readings, forecasts and ideas are saved on this phone. Grey light and dark themes are included. Uninstalling or clearing app storage removes these records; updates signed with the same local key retain them.

For AI, enter your own Gemini API key in Profile & connections, then tap Enable AI. Credentials are encrypted with Android Keystore and are never bundled into the APK. Internet is required. Google receives photos or questions with selected-day meal totals/titles only after the corresponding consent control is enabled. Provider quota and billing may apply. Remove Gemini key deletes the stored credential.

Barcode search uses Open Food Facts and does not require a key. Check the package label: entries may be incomplete or incorrect. The built-in ten-food catalog is illustrative, not a verified training database. Photo recognition suggests foods and rough portions for your review, not measured calories.

Fitness: manual workouts and daily CSV imports work offline. Strava requires your own activity:read access token; connect and manually sync the selected day. Tokens expire and must be replaced. Missing calorie values are skipped. Repeated sync replaces that day's Strava activities. Imported daily activity totals take precedence over individual workout calories to avoid double counting. Automatic Health Connect/watch sync is not implemented.

Community is a device-local idea board. Share suggestion opens the Android share sheet; you choose whether and where to send it. Public accounts/feed and a hosted shared API are future work.

Validation: signed APK build, emulator installation and launch, 16 Python tests, offline Android contract tests, and mocked standalone provider-routing tests passed. Native connection controls were visually checked. Live Gemini/Strava account requests have not been tested with your credentials. Forecasts and habit scores are experimental, not medical assessments.

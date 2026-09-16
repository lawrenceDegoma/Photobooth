# Assets

Static, non-code assets used by the photo booth application.

- `icons/` — UI button/icon images (e.g. shutter, retake, share, admin gear).
  If empty, the UI falls back to text labels / Qt built-in styling.
- `fonts/` — Bundled TrueType fonts used for photo strip text overlays and
  the on-screen UI. `app/processing/fonts.py` will prefer a bundled font
  here (e.g. `fonts/DejaVuSans-Bold.ttf`) before falling back to system
  fonts, which keeps rendering consistent between macOS (dev) and
  Raspberry Pi OS (production).
- `templates/` — Background images / overlays for photo strip templates
  (`app/processing/templates.py`) — e.g. a wedding frame PNG referenced by
  the `wedding` template.
- `branding/` — Event or venue branding (logo shown on the welcome screen,
  splash image, favicon for the sharing page).

None of these are required for the app to run — every consumer has a
sensible programmatic fallback — but dropping files in here lets an event
be customized without touching code.

# Christmas redesign

Work is confined to `wsdc-winter-redesign`.

## Architecture inspected

`config` contains Django settings and root routes. `core` owns models, forms,
admin-managed content, bookings, Dandiya registration, coupons and staff check-in.
Templates are server rendered; WhiteNoise serves static assets and Cloudinary
stores uploaded media. Payment verification is an existing staff workflow.
Coupon URLs use UUID tokens; paid coupons contain entry-code QR images. Check-in
requires staff access, verified payment and an unused registration, using an
atomic transaction and row locking.

## Changes

- Evergreen, burgundy and gold Christmas styling, editorial serif headings,
  improved highlight cards and Christmas footer. Existing local photography,
  Santa SVG and reduced-motion-aware snow are retained.
- Offerings use one scroll implementation, measured from corresponding cards
  across three sets. ResizeObserver recalculates the loop distance. Mouse drag,
  native touch scrolling, keyboard arrows, pause/play and interaction pauses
  coexist with automatic movement. Cloned links are excluded from keyboard order.
- Responsive navigation has an accessible disclosure button, Escape/outside/link
  dismissal and a usable fallback when JavaScript is unavailable.
- Gallery links open a native modal dialog with captions, previous/next controls,
  arrow keys, Escape and focus restoration. Links still work without JavaScript.
- Testimonials have horizontal scrolling, automatic advancement, manual controls,
  pause/play and reduced-motion support. Empty content states remain available.

Models, forms, views, admin payment verification, routes, Dandiya templates,
credentials and requirements were not changed. No migrations were generated or
run, and nothing was deployed or merged.

## Validation

- Exact requirements installed in an isolated virtual environment; `pip check`
  reported no broken requirements.
- `python manage.py check` passed.
- `python manage.py test` passed eight database-free regression tests: template
  rendering, gallery/testimonial markup, pending coupon/PDF gates, paid PDF/QR
  generation, staff restriction, payment/duplicate check-in behavior and
  registration calculation/session handling.
- `node --check static/js/winter.js` and `git diff --check` passed.
- `collectstatic` with an isolated temporary output directory passed including
  manifest processing.
- Headless Chromium/Playwright checks on rendered fixture content passed desktop
  autoplay, loop crossing, mouse dragging, lightbox navigation/close, testimonial
  controls, mobile disclosure, native touch swiping, mobile overflow and reduced
  motion. No JavaScript runtime errors were observed. Fixture content was used
  only in the temporary preview, not added to application data.

## Remaining validation limits

No database migrations were run. Tests mock persistence and transactions and do
not establish PostgreSQL concurrency behavior or full database-backed registration
integration. Production payments, Cloudinary credentials/media access and physical
camera QR scanning were not exercised. These existing integrations were left intact.

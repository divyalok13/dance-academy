# Photo and video showcase

## Design and data

The existing `GalleryImage` model and table are retained. Migration
`0009_gallery_video_url` adds one optional, blank-by-default HTTPS URL field.
Existing photo records, IDs, paths, titles, timestamps and visibility flags are
preserved. An empty video URL identifies a photo; a populated URL identifies a
video, with the existing required image used as its poster. The home view's
existing active-gallery query and ordering continue to serve both types.

Gallery CSS and JavaScript are isolated in `gallery.css` and `gallery.js`.
The Christmas hero, navigation, testimonials and Dandiya functionality are not
changed. The old photo-only modal handler was removed from `winter.js` to avoid
duplicate event handling.

Cards lift using transforms, preserving the grid footprint. Overflow and stacking
allow the enlarged card to appear over neighboring cards. Hover effects apply only
to fine pointing devices; keyboard focus remains visible, and reduced motion
removes transformations. All/Photos/Videos filters use pressed states, a live
result count and an empty state. Native modal focus containment, Escape, focus
restoration, image swipe navigation and touch-size controls support mobile and
keyboard use. Links work without JavaScript.

Photos load lazily. Video bytes are not requested by gallery cards; posters are
ordinary images. The modal uses native controls, inline mobile playback and
`preload="none"`. Opening a video does not autoplay or start a media download.
Closing or navigating away pauses playback, removes the source and releases the
previous media resource. Loading/failure messages and an original-media link
provide fallbacks. Native video keyboard controls retain seeking and volume keys.

## Local review

After fetching `wsdc-winter-redesign-review`, activate your local virtual environment
and install `requirements.txt`. Ensure the environment selects your **local**
database, then apply the approved additive migration locally:

```sh
python manage.py migrate core
python manage.py check
python manage.py test
python manage.py runserver
```

No migration was applied to a persistent or production database during this work.
Migration testing used a disposable Django test database only. No Render settings,
production credentials, deployments or main-branch merges were made.

## Add a video in Django Admin

1. Compress the clip to a browser-friendly MP4 (H.264 video / AAC audio, with
   fast-start enabled). Short 720p highlights of roughly 10–20 MB are a useful
   starting budget, rather than long original recordings.
2. Upload it to your existing Cloudinary Media Library as a video. Copy its public
   HTTPS delivery URL, typically `https://res.cloudinary.com/<cloud>/video/upload/...mp4`.
3. In Django Admin, add a Gallery image entry: title, **Photo or video poster**,
   **Video URL**, and active status. Save. Leave Video URL blank for a photo.
4. Test playback on desktop and mobile. Use captions/burned-in subtitles where
   spoken content needs them, and provide a meaningful title.

The URL must point directly to MP4, WebM or OGV media; watch pages such as YouTube
URLs are not video files and are rejected. MP4 is recommended for broad mobile
compatibility. The app does not fetch or transcode remote media on the server,
change Cloudinary upload presets, or accept video uploads through Render. Remote
availability, encoding, size and account quotas remain the administrator's
responsibility. Existing image uploads still use the configured Cloudinary image
storage backend.

## Free-tier budget (checked 7 November 2026)

Cloudinary currently advertises 25 shared monthly credits on its Free plan.
Storage, delivery bandwidth and transformations consume that shared allowance;
it is not 25 GB each of independent free storage and bandwidth. The plan comparison
lists a 100 MB maximum video file, while video-player documentation distinguishes
a 40 MB free-plan limit for on-the-fly transformations. Account-specific usage and
limits should be confirmed in the Cloudinary console before adding many clips.

Recommendation: retain the existing Cloudinary account, upload a small selection
of compressed clips, reuse poster images, avoid autoplay and limit transformation
variants. Larger libraries or frequent viewing require a separate capacity review;
no new storage service or streaming architecture is introduced here.

Official sources:

- https://cloudinary.com/pricing
- https://cloudinary.com/pricing/compare-plans
- https://cloudinary.com/documentation/billing_and_plans
- https://cloudinary.com/documentation/video_player_how_to_embed
- https://cloudinary.com/documentation/video_optimization

## Validation

- Django checks, migration consistency check and static collection/manifest processing passed.
- Thirteen Django tests passed, including actual admin video creation, HTTPS and
  direct-file validation, active mixed-media rendering, preservation of a preexisting
  photo across migration 0009, and the existing registration/payment/PDF/check-in tests.
- Chromium checks passed photo hover lift/layering with no neighboring layout shift,
  filters and empty states, full photo modal, keyboard/focus behavior, deferred media
  loading, actual MP4 playback, playback errors, cleanup on close, mobile modal and
  image swipes, responsive overflow, reduced motion and no-JavaScript fallback.
- JavaScript syntax and `git diff --check` passed.

Live Cloudinary uploads and delivery quotas were not tested, as no account credentials
were needed or changed. Browser tests used a temporary local MP4 fixture, not new
application or production records. Physical iOS/Android devices were not tested.

# Changelog

## 0.1.11

- Move the image-paths list to its own "Paths" tab instead of stacking it
  above the preview grid.

## 0.1.10

- Preview tab now lists the `/media/local/...` path for each dashboard
  image, with a one-click copy button, computed from the configured output
  folder — so you don't have to work out the paths by hand to build your
  Lovelace dashboard.

## 0.1.9

- Preview grid now shows 4 images per row instead of 3, so the 7 dashboard
  images lay out as 4+3 rather than 3+3+1.

## 0.1.8

- Fix the parking map looking stretched/distorted: it was resized directly
  to the card's box size regardless of aspect ratio. Now cropped-to-fill
  (same technique as the vehicle hero photos) so the map is never squished.

## 0.1.7

- Switch the parking map style from `toner-grey` (bright white/grey, clashed
  with the dark UI) to `dark-matter`, a documented dark-themed Geoapify
  style that actually fits the rest of the dashboard.

## 0.1.6

- Fix the Geoapify Static Maps request always failing with 400: the marker
  colour was double URL-encoded (`%23` manually written, then re-encoded to
  `%2523` by `urlencode()`), and `dark-matter` is not a valid style name.
  The marker/center values now use `urlencode(..., safe=":,;")` matching
  Geoapify's documented format, and the style is `toner-grey`.

## 0.1.5

- Serve the Web UI's index page and static assets (app.js, style.css) with
  `Cache-Control: no-cache`, so browsers always revalidate instead of
  silently reusing a stale copy after an add-on update. Previously the
  Preview tab could keep showing an old image count/copy after updating
  until a hard refresh.
- Made the preview subtitle generic ("all dashboard images") instead of
  hardcoding a count that drifts as image types are added.

## 0.1.4

- Show a real street map with a marker for the parking location (`parked.png`
  and the Location card in `dashboard_set.png`), fetched from Geoapify's
  Static Maps API using the same key as reverse geocoding. Falls back to a
  map-icon placeholder when no Geoapify key is set or the fetch fails.
- Fix `fit()` always appending an ellipsis even when the text already fit.

## 0.1.3

- Add `dashboard_set.png`, a seventh persistent image combining battery &
  range, security, charging, climate, tyre pressure and location into one
  complete overview dashboard.
- Hide the sunshade row on T03 (no sunshade equipment).

## 0.1.2

- Fix SUPERVISOR_TOKEN never reaching the app: the container's CMD now runs
  through `run.sh` with the `with-contenv bashio` shebang, which is required
  for s6-overlay to forward Supervisor-injected environment variables to the
  process. Previously `python3 -m main` ran directly and never saw the token,
  causing every Home Assistant Core API call to fail with 401.

## 0.1.1

- Log whether SUPERVISOR_TOKEN is present at startup, to diagnose 401 errors
  from the Home Assistant Core API

## 0.1.0

- Initial standalone Home Assistant add-on
- Ingress setup and preview interface
- Automatic vehicle and device discovery
- Six premium vehicle dashboard renderers
- Multi-device parking notifications
- Optional Geoapify reverse geocoding

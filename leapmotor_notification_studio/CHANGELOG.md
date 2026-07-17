# Changelog

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

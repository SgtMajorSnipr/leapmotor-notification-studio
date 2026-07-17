# Changelog

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

# Leapmotor Notification Studio

Leapmotor Notification Studio is a Home Assistant add-on that turns your
existing Leapmotor entities into premium 1080 × 1920 dashboard images and rich
Android Companion App parking notifications.

It does **not** sign in to the Leapmotor cloud. Use it alongside an entity
provider such as Leapmotor Mate or `leapmotor-ha`. This avoids duplicate
vehicle sessions and keeps cloud polling under the provider's control.

## Features

- Automatic Leapmotor vehicle and Companion App discovery
- Vehicle artwork for B10, C10, T03 and B05, across their official colour
  variants
- Six persistent images: overview, parking, charging, climate, tyres and
  security
- State-change detection with a configurable background refresh interval
- Multi-device parking notifications — optional, and independent from image
  rendering
- Optional Geoapify reverse geocoding for the parking location
- Settings are kept private to the add-on

## Installation

1. In Home Assistant, open **Settings → Add-ons → Add-on Store**.
2. Open the menu (**⋮**), choose **Repositories**, and add:
   `https://github.com/SgtMajorSnipr/leapmotor-notification-studio`
3. Install **Leapmotor Notification Studio** from the store.
4. Start the add-on and enable **Start on boot**.
5. Open its **Web UI** and select **Detect automatically**.
6. Choose your vehicle, appearance and receiving devices, save, then render a
   preview.

## Generated media

Images are saved to `/media/leapmotor-notification-studio/` and available to
dashboards as:

```text
/media/local/leapmotor-notification-studio/overview.png
/media/local/leapmotor-notification-studio/parked.png
/media/local/leapmotor-notification-studio/charging.png
/media/local/leapmotor-notification-studio/climate.png
/media/local/leapmotor-notification-studio/tyres.png
/media/local/leapmotor-notification-studio/security.png
```

## Swipe card example

```yaml
type: custom:swipe-card
parameters:
  spaceBetween: 8
cards:
  - type: picture
    image: /media/local/leapmotor-notification-studio/overview.png
  - type: picture
    image: /media/local/leapmotor-notification-studio/parked.png
  - type: picture
    image: /media/local/leapmotor-notification-studio/charging.png
  - type: picture
    image: /media/local/leapmotor-notification-studio/climate.png
  - type: picture
    image: /media/local/leapmotor-notification-studio/tyres.png
  - type: picture
    image: /media/local/leapmotor-notification-studio/security.png
```

`custom:swipe-card` is optional and must be installed separately. Standard
Home Assistant picture cards work without it.

## Notifications are optional

The **Notifications** tab has an **Enable notifications** switch. Turning it
off stops the add-on from sending anything to the Companion App while leaving
image rendering untouched — useful if you only want the dashboard images and
don't care about parking alerts.

## Privacy and security

- No vehicle credentials are requested or stored.
- Geoapify is optional; its key is masked in the UI and stored privately.
- Home Assistant access uses the short-lived token Supervisor gives the
  add-on.

## License

MIT.

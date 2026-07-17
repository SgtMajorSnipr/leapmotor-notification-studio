# Leapmotor Notification Studio

Leapmotor Notification Studio is a standalone Home Assistant add-on that turns
existing Leapmotor entities into premium 1080 × 1920 dashboard images and rich
Android Companion App parking notifications.

It does **not** sign in to the Leapmotor cloud. Use it alongside an entity
provider such as Leapmotor Mate or `leapmotor-ha`. This avoids duplicate vehicle
sessions and keeps cloud polling under the provider's control.

## Features

- Professional Home Assistant Ingress configuration screen
- Automatic Leapmotor vehicle and Companion App discovery
- Bundled B10, C10, T03 and B05 hero and tyre-view vehicle artwork
- Six persistent images: overview, parking, charging, climate, tyres and security
- Realistic European Deep Purple B10 visuals, including a tyre top view
- State-change detection with configurable background refresh interval
- Multi-device parking notifications with independent error handling
- Optional Geoapify reverse geocoding
- Persistent settings stored in the add-on's private `/data` directory
- Runs without AppDaemon, Node-RED, a browser renderer or external scripts

## Installation from GitHub

Before publishing, replace `YOUR_GITHUB_USERNAME` in `repository.yaml` and the
add-on metadata with the actual repository owner.

1. Create a public GitHub repository from this folder.
2. In Home Assistant, open **Settings → Add-ons → Add-on Store**.
3. Open the menu, choose **Repositories**, and add the repository URL.
4. Install **Leapmotor Notification Studio**.
5. Start the add-on and enable **Start on boot**.
6. Open its Web UI and select **Detect automatically**.
7. Choose the vehicle and receiving devices, save, then render a preview.

Home Assistant builds the appropriate container architecture during install.
Prebuilt GHCR images can be added later for faster installation.

## Generated media

The default output directory is:

```text
/media/leapmotor-notification-studio/
```

Images are available to dashboards as:

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

## Privacy and security

- No vehicle credentials are requested or stored.
- Geoapify is optional; its key is masked in the UI and stored under `/data`.
- Home Assistant access uses the short-lived Supervisor token supplied to the add-on.
- API keys, settings, output and logs are excluded from the repository.

## Development

The runtime is Python 3.12 with aiohttp and Pillow. All rendering is native
Pillow; there are no HTML screenshots or browser automation dependencies.

```bash
python -m compileall leapmotor_notification_studio/rootfs/app
```

## License

MIT. Vehicle imagery should be reviewed before redistribution to ensure the
publisher has appropriate rights for the intended repository and jurisdiction.

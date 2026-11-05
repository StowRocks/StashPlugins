# StowServerQR

Generate a QR code containing your Stash server credentials for easy setup in the [Stow](https://stow.rocks) iOS/macOS app.

## Installation

1. Add plugin source in Stash:
   - Go to **Settings → Plugins → Available Plugins**
   - Click **Add Source**
   - Enter: `https://plugins.stow.rocks/index.yml`
   - Click **Reload**

2. Find "StowServerQR" and click **Install**

## Usage

1. Navigate to **Settings → Security**
2. Find the "📱 Stow QR" button next to "Generate API Key"
3. Enter a friendly server name
4. Click **📱 Stow QR** to display the QR code
5. Scan it with a QR reader or a device camera
6. If Stow has registered the `stow://` URL scheme, the link opens the app; Stow should ask before adding or updating a server

## Security

⚠️ The QR code contains your API key. Only scan on devices you trust.

- QR code is hidden by default
- Visually hides the panel after 60 seconds
- Clear security warning displayed

The QR contains the API key in a deep link. Base64 is an encoding, not encryption. The plugin reads the key from the rendered API-key value on Stash's **Settings → Security** page; it does not read the server's configuration file. The hidden QR canvas currently remains in the page DOM after the panel is hidden.

## QR Code Data Format

The QR code contains a `stow://` URL. Its `data` query parameter is Base64-encoded JSON with these fields:

```json
{
  "name": "My Stash Server",
  "url": "http://192.168.1.10:9999",
  "apiKey": "eyJhbGciOiJIUzI1NiIs..."
}
```

The complete QR content has this form:

```text
stow://add-server?data=<base64-encoded-json>
```

The current browser implementation uses `btoa` on the JSON string. Server names containing characters outside Latin-1 can make QR generation fail; UTF-8-safe encoding is tracked in [`TODO.md`](../../TODO.md).

| Field    | Type   | Description                                   |
| -------- | ------ | --------------------------------------------- |
| `name`   | string | User-defined server display name              |
| `url`    | string | Stash server URL (auto-detected from browser) |
| `apiKey` | string | Stash API key (from Settings → Security)      |

## Requirements

- Stash v0.20.0 or later
- API key configured in Stash (Settings → Security → Generate API Key)

## License

The plugin is proprietary. No license is granted except under a separate written agreement; see the repository [LICENSE](../../LICENSE).

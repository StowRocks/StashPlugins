# Stow

Companion plugin for the [Stow](https://stow.rocks) iOS/macOS app. It has modules:

- **qr**: a QR code with your Stash server credentials for easy setup in the app (below).
- **operations**: server-side operations the app calls through Stash, see [Operations](#operations).

## Installation

1. Add plugin source in Stash:
   - Go to **Settings → Plugins → Available Plugins**
   - Click **Add Source**
   - Enter: `https://plugins.stow.rocks/index.yml`
   - Click **Reload**

2. Find "Stow" and click **Install**

## Usage

1. Navigate to **Settings → Security**
2. Find the "📱 Stow QR" button next to "Generate API Key"
3. Enter a friendly server name
4. Click **📱 Stow QR** to display the QR code
5. Scan it with a QR reader or a device camera
6. If Stow has registered the `stow://` URL scheme, the link opens the app; Stow should ask before adding or updating a server

## Operations

The app calls the plugin with the GraphQL mutation `runPluginOperation(plugin_id: "stow", args: {op: "<name>", ...})` and gets the plugin's JSON output back. There is one entry point per plugin, so the operation name travels in `args.op`. The operation part is `stow.py` (Python 3, standard library only, no dependencies); Stash starts it for each call.

| `op`       | Result                                                                                                                                                                                                                                                                                        |
| ---------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `status`   | `{"plugin": "stow", "version": "…", "capabilities": ["qr", "whisparr"], "whisparrConfigured": true}`. The app uses `version` and `capabilities` to decide what it may call, `whisparrConfigured` tells whether URL and key are set.                                                           |
| `whisparr` | Forwards one request to your Whisparr V3 instance and returns `{"status": 200, "contentType": "…", "body": "<raw reply>"}`. Arguments: `method`, `path` (relative, for example `api/v3/movie`), `query` (list of `[name, value]` pairs, repeated names keep their order), `body` (JSON text). |

### Whisparr module

Set **Whisparr URL** and **Whisparr API key** under **Settings → Plugins → Stow**. Stow then talks to Whisparr through Stash instead of directly, so the key stays on the Stash server and Whisparr only has to be reachable from the Stash host. Without the plugin settings the Stow app falls back to a direct connection if one is configured.

The operation is not an open proxy. It forwards only the requests the app makes: `ping`, `system/status`, `qualityprofile`, `rootfolder`, `tag`, `movie` (get, add, delete), `queue` (get, delete an entry), `performer` and `studio` (get, add, update). Everything else is refused before any request leaves the server. Status codes of Whisparr, including errors, are returned unchanged so the app keeps its own error handling.

Stash shows plugin settings as plain text on the settings page, so anyone who can open Stash settings can read the Whisparr key.

Errors come back as the GraphQL error of the mutation with a short message (`unknown operation`, `missing operation`).

Development: `pnpm test` runs the JavaScript tests and the Python tests (`python3 -m unittest`). When you change `version` in `stow.yml`, change `VERSION` in `stow.py` too; a test checks that they match.

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

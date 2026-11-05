# Stow App: QR Code Server Setup

The **StowServerQR** Stash plugin adds a button to **Settings → Security**. It creates a `stow://` deep link carrying a server name, URL, and API key. The Stow app must register the URL scheme and handle the link before scanning can open the app.

## Current plugin payload

The QR content is a URI, not raw JSON:

```text
stow://add-server?data=<base64-encoded-json>
```

After Base64 decoding, `data` contains JSON with these fields:

```json
{
  "name": "My Stash Server",
  "url": "http://192.168.1.10:9999",
  "apiKey": "<Stash API key>"
}
```

The plugin reads the API key from the rendered value in the Stash Security settings page DOM. It does not read the server's configuration file. The QR payload contains the API key in clear form after Base64 decoding; Base64 is not encryption.

The implementation encodes the JSON payload as UTF-8 before Base64, so Unicode server names are supported. The payload still contains a reusable API key and must be handled as a credential.

## Register the URL scheme

Add the `stow` scheme to the app's `Info.plist`:

```xml
<key>CFBundleURLTypes</key>
<array>
  <dict>
    <key>CFBundleURLName</key>
    <string>rocks.stow</string>
    <key>CFBundleURLSchemes</key>
    <array>
      <string>stow</string>
    </array>
  </dict>
</array>
```

## Decode and validate the link

Add an `.onOpenURL` handler to the app's root view on each platform:

```swift
RootView()
    .onOpenURL { url in
        guard let payload = parseStowURL(url) else { return }
        presentServerConfirmation(for: payload)
    }
```

The following parser validates the link shape, Base64 data, JSON, and server URL. It intentionally leaves persistence to the confirmation flow:

```swift
struct StowQRPayload: Decodable {
    let name: String
    let url: String
    let apiKey: String
}

func parseStowURL(_ url: URL) -> StowQRPayload? {
    guard url.scheme == "stow",
          url.host == "add-server",
          let components = URLComponents(url: url, resolvingAgainstBaseURL: false),
          let dataParam = components.queryItems?.first(where: { $0.name == "data" })?.value,
          let jsonData = Data(base64Encoded: dataParam),
          let payload = try? JSONDecoder().decode(StowQRPayload.self, from: jsonData),
          let serverURL = URLComponents(string: payload.url),
          ["http", "https"].contains(serverURL.scheme?.lowercased() ?? ""),
          serverURL.host != nil
    else { return nil }

    return payload
}
```

Before saving, show the server name and URL, mask the API key, and ask the user whether to add or update the server. Store the API key in the app's secure storage. Do not persist the payload automatically when the link opens.

## Security and behavior

- Anyone who can read the QR can recover the API key. Scan it only on trusted devices.
- The plugin displays a warning and visually hides its QR panel after 60 seconds. The generated canvas currently remains in the page DOM after hiding; DOM cleanup is listed in [`TODO.md`](TODO.md).
- The app should reject malformed payloads and server URLs that do not use HTTP or HTTPS.
- The QR feature requires an API key to be present on the Security settings page.

## Manual integration checks

1. Confirm the app registers the `stow` URL scheme.
2. Open Stash → Settings → Security and display the QR code.
3. Scan it and confirm the app receives `stow://add-server` with a decodable payload.
4. Verify the app shows a confirmation with the API key masked before adding or updating.
5. Try malformed Base64, malformed JSON, and a non-HTTP(S) server URL; the app should reject each.
6. Test a server name containing non-Latin characters after the plugin's UTF-8-safe encoding issue is resolved.

## Repository and license

Plugin source: [StowRocks/StashPlugins](https://github.com/StowRocks/StashPlugins). The project is proprietary. No license is granted except under a separate written agreement; see [LICENSE](LICENSE).

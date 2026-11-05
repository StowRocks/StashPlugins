# StashPlugins Repository

## Repository and published feed

- GitHub repository: [StowRocks/StashPlugins](https://github.com/StowRocks/StashPlugins)
- Plugin source feed: <https://plugins.stow.rocks/index.yml>
- Plugin archive: <https://plugins.stow.rocks/stowServerQR.zip>
- The Vercel project configuration builds the repository into `_site/`; the domain is `plugins.stow.rocks`.

The plugin manifest links to the GitHub repository above. To install it in Stash, add `https://plugins.stow.rocks/index.yml` under **Settings → Plugins → Available Plugins** and reload the source.

## Local development

Use Node.js 26, as recorded in `.nvmrc` and `package.json`:

```bash
npm install
npm run build
```

The build writes the plugin feed and archive to `_site/`. It also bundles each `*.src.js` file into its corresponding plugin `.js` file.

## StowServerQR behavior

The plugin adds a QR button to Stash's **Settings → Security** page. It reads the API key from the rendered page DOM; it does not access the Stash server configuration. Its QR content is `stow://add-server?data=<base64-encoded-json>`, where the JSON includes the server name, `location.origin`, and API key. The Stow app must register the `stow` URL scheme and implement the confirmation flow described in [`STOW_APP_INTEGRATION.md`](STOW_APP_INTEGRATION.md).

Base64 does not encrypt the API key. The plugin warns users and visually hides the QR panel after 60 seconds. Open issues, including Unicode-safe encoding and clearing the hidden QR canvas, are listed in [`TODO.md`](TODO.md).

## License status

The project is proprietary. No license is granted except under a separate written agreement; see [LICENSE](LICENSE).

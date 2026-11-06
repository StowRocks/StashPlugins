# Stash Plugins

Stash plugins for the Stow ecosystem, hosted at [plugins.stow.rocks](https://plugins.stow.rocks).

The canonical repository is hosted on
[git.schmieder.eu](https://git.schmieder.eu/StowRocks/StashPlugins). The
[GitHub repository](https://github.com/StowRocks/StashPlugins) remains a public
operational mirror for GitHub Actions.

## Installation

Add this plugin source to Stash:

1. Open Stash → **Settings → Plugins → Available Plugins**
2. Click **Add Source**
3. Enter URL: `https://plugins.stow.rocks/index.yml`
4. Click **Reload**
5. Browse and install available plugins

## Available Plugins

### StowServerQR

Generate a QR code containing your Stash server credentials for easy setup in the Stow iOS/macOS app.

**Features:**

- Auto-detects server URL
- Reads the API key displayed in Stash's Security settings page
- Shows a security warning and visually hides the QR panel after 60 seconds
- Encodes a `stow://add-server` handoff for the Stow app

[Documentation](plugins/stowServerQR/README.md)

## Development

Use Node.js 26 (`.nvmrc`):

```bash
# Install dependencies
pnpm install --frozen-lockfile

# Build plugins
pnpm build

# Output in _site/
```

## License

The project is proprietary. No license is granted except under a separate written agreement; see [LICENSE](LICENSE).

# Audit TODO

Open findings from the read-only audit, prioritized by impact. This list records work still needed; no remediation of these items is claimed here.

## P1

- [ ] **Use Unicode-safe QR encoding.** `stow-server-qr.src.js` passes serialized JSON directly to `btoa`. Server names containing characters outside Latin-1 make QR generation throw. Encode JSON as UTF-8 before Base64, and use URL-safe Base64 or correctly escape the query parameter. Keep the Stow app decoder in sync.

## P2

- [ ] **Clear the QR payload on hide.** `hideQR()` only sets the panel to `display: none`; the canvas containing the API-key QR remains in the page DOM. Clear or remove the canvas when hiding and when the timer expires.
- [ ] **Make generated artifacts reproducible.** `build.js` writes the current time into `index.yml`, derives the displayed version from the last committed plugin change, and archives files with checkout-dependent mtimes. Use deterministic metadata and archive timestamps if stable artifact hashes are required.
- [ ] **Add automated tests and CI.** There are no test scripts, test files, or CI workflows. Cover payload encode/decode compatibility, missing API keys, URL validation in the app integration, and clean build output from the lockfile.
- [ ] **Avoid shell interpolation for git metadata.** `build.js` inserts the plugin directory name into an `execSync` command string. Invoke git with an argument array (for example, `execFileSync`) so directory names are not interpreted by a shell.
- [ ] **Handle missing API keys and QR-generation failures.** The plugin currently falls back to an empty key and does not catch QR encoder errors; show a user-facing failure instead of rendering an unusable payload or leaving an unhandled rejection.
- [ ] **Re-evaluate Archiver's minimatch override.** The locked Archiver 8 dependency chain currently applies `minimatch@11.0.4` under `readdir-glob` (whose declared range is `^10.2.2`). Keep verifying compatibility and `npm audit` results after upgrades; remove the override only when upstream publishes a patched compatible range.

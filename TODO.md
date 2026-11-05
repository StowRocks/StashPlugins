# Audit TODO

Open findings from the read-only audit, prioritized by impact. This list records work still needed; no remediation of these items is claimed here.

## P1

- [x] **Use Unicode-safe QR encoding.** The shared payload encoder now converts JSON to UTF-8 before Base64 and has a Unicode regression test.

## P2

- [x] **Clear the QR payload on hide.** `hideQR()` now removes the credential-bearing canvas from the DOM.
- [x] **Make generated artifacts reproducible.** Build metadata and archive timestamps now derive from `SOURCE_DATE_EPOCH` or the checked-out commit timestamp.
- [x] **Add automated tests and CI.** CI now enforces formatting, lint, Unicode payload coverage, a reproducible bundle diff check, and a full-history secret scan.
- [x] **Avoid shell interpolation for git metadata.** `build.js` invokes git with an explicit argument array.
- [x] **Handle missing API keys and QR-generation failures.** The plugin now refuses empty keys and reports encoder failures to the user.
- [ ] **Re-evaluate Archiver's minimatch override.** The locked Archiver 8 dependency chain currently applies `minimatch@11.0.4` under `readdir-glob` (whose declared range is `^10.2.2`). Keep verifying compatibility and `pnpm audit` results after upgrades; remove the override only when upstream publishes a patched compatible range.
- [ ] Enable the `CI Success` branch rule after this workflow has landed on `main`; GitHub cannot require a status check before it exists on the default branch.

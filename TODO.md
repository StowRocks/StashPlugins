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
- [ ] **Re-evaluate scoped minimatch overrides.** Archiver 8's `readdir-glob`
      and ESLint 10.14.0's direct/config-array paths still declare vulnerable
      minimatch 10 ranges. They are pinned narrowly to tested `minimatch@11.0.4`;
      remove each override when its upstream range accepts a patched release.
- [ ] Enable the `CI Success` branch rule after this workflow has landed on `main`; GitHub cannot require a status check before it exists on the default branch.

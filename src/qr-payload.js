// SPDX-License-Identifier: GPL-3.0-only
export function encodeServerPayload(payload) {
  const bytes = new TextEncoder().encode(JSON.stringify(payload));
  let binary = "";
  for (const byte of bytes) binary += String.fromCharCode(byte);
  return btoa(binary);
}

export function buildServerDeepLink(payload) {
  return (
    "stow://add-server?data=" + encodeURIComponent(encodeServerPayload(payload))
  );
}

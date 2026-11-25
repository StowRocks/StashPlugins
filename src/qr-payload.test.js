import { describe, expect, it } from "vitest";

import { buildServerDeepLink, encodeServerPayload } from "./qr-payload.js";

describe("encodeServerPayload", () => {
  it("encodes Unicode server names as UTF-8 base64", () => {
    const encoded = encodeServerPayload({
      name: "München 🎬",
      url: "https://example.test",
      apiKey: "secret",
    });
    const decoded = new TextDecoder().decode(
      Uint8Array.from(atob(encoded), (character) => character.charCodeAt(0)),
    );
    expect(JSON.parse(decoded)).toEqual({
      name: "München 🎬",
      url: "https://example.test",
      apiKey: "secret",
    });
  });

  it("percent-encodes +, /, and = in server deep links", () => {
    const payload = {
      name: ">>>???",
      url: "https://stash.example:9999/sub?a=1",
      apiKey: "k+e/y=1234",
    };
    const deepLink = buildServerDeepLink(payload);
    expect(deepLink.startsWith("stow://add-server?data=")).toBe(true);
    const rawQuery = deepLink.slice("stow://add-server?data=".length);
    expect(rawQuery).not.toMatch(/[+/=]/);
    const param = new URL(deepLink).searchParams.get("data");
    const decoded = new TextDecoder().decode(
      Uint8Array.from(atob(param), (character) => character.charCodeAt(0)),
    );
    expect(JSON.parse(decoded)).toEqual(payload);
  });
});

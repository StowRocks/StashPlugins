import { describe, expect, it } from "vitest";

import { encodeServerPayload } from "./qr-payload.js";

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
});

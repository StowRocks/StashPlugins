import globals from "globals";

const rules = {
  "no-undef": "error",
  "no-unused-vars": ["error", { argsIgnorePattern: "^_" }],
  "no-var": "error",
  "prefer-const": "error",
};

export default [
  { ignores: ["_site/**", "coverage/**", "plugins/**/stow-server-qr.js"] },
  {
    files: [
      "build.js",
      "eslint.config.js",
      "vitest.config.js",
      "src/**/*.test.js",
    ],
    languageOptions: {
      ecmaVersion: "latest",
      sourceType: "module",
      globals: globals.node,
    },
    rules,
  },
  {
    files: ["plugins/**/*.src.js", "src/qr-payload.js"],
    ignores: ["plugins/**/stow-server-qr.js"],
    languageOptions: {
      ecmaVersion: "latest",
      sourceType: "module",
      globals: globals.browser,
    },
    rules,
  },
];

# SPDX-License-Identifier: GPL-3.0-only
"""Whisparr module of the Stow plugin.

The app speaks the Whisparr V3 REST API through Stash: one operation, `whisparr`, forwards a request to the
Whisparr instance that is configured in the plugin settings (whisparrUrl, whisparrApiKey). The key never leaves
the Stash server. This is not an open proxy: only the method and path pairs in ALLOWED are forwarded, and the
reply is returned as it came (status and raw body) so the app keeps its own error handling.
Standard library only.
"""

import json
import re
import urllib.error
import urllib.parse
import urllib.request

PLUGIN_ID = "stow"
# If Whisparr is not set up in this plugin, the access of the missing-scenes plugin is used: it holds the same two
# settings (whisparrUrl, whisparrApiKey) and is usually set up first.
FALLBACK_PLUGIN_ID = "missingScenes"
TIMEOUT_SECONDS = 20
MAX_RESPONSE_BYTES = 10 * 1024 * 1024

# The requests the app makes, nothing else. Paths are relative to the Whisparr base URL.
ALLOWED = [
    ("GET", r"ping"),
    ("GET", r"api/v3/system/status"),
    ("GET", r"api/v3/(qualityprofile|rootfolder|tag)"),
    ("GET", r"api/v3/movie"),
    ("POST", r"api/v3/movie"),
    ("DELETE", r"api/v3/movie/\d+"),
    ("GET", r"api/v3/queue"),
    ("DELETE", r"api/v3/queue/\d+"),
    ("GET", r"api/v3/(performer|studio)"),
    ("POST", r"api/v3/(performer|studio)"),
    ("GET", r"api/v3/(performer|studio)/\d+"),
    ("PUT", r"api/v3/(performer|studio)/\d+"),
]
_ALLOWED = [(method, re.compile(pattern, re.ASCII)) for method, pattern in ALLOWED]

# `ping` is anonymous in Whisparr, so the key is not sent with it.
_ANONYMOUS = {"ping"}


class _NoRedirectHandler(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


_NO_REDIRECT_OPENER = urllib.request.build_opener(_NoRedirectHandler)


def _read_bounded(reply, limit=MAX_RESPONSE_BYTES):
    raw = reply.read(limit + 1)
    if len(raw) > limit:
        raise ValueError(f"Whisparr response exceeded {limit} bytes")
    return raw


class WhisparrNotConfigured(Exception):
    pass


def is_allowed(method, path):
    return any(m == method and pattern.fullmatch(path) for m, pattern in _ALLOWED)


def stash_url(connection):
    """The URL of the Stash that started this call, for reading the plugin settings."""
    host = connection.get("Host") or "127.0.0.1"
    if host in ("0.0.0.0", "::", "[::]"):
        host = "127.0.0.1"
    return f"{connection.get('Scheme') or 'http'}://{host}:{connection.get('Port') or 9999}/graphql"


def read_all_settings(connection):
    """The settings of all plugins from Stash (`configuration.plugins`), by plugin id."""
    payload = json.dumps({"query": "{ configuration { plugins } }"}).encode()
    headers = {"Content-Type": "application/json"}
    cookie = connection.get("SessionCookie") or {}
    if cookie.get("Name"):
        headers["Cookie"] = f"{cookie['Name']}={cookie.get('Value', '')}"
    request = urllib.request.Request(stash_url(connection), data=payload, headers=headers, method="POST")
    with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS) as reply:
        data = json.load(reply)
    return ((data.get("data") or {}).get("configuration") or {}).get("plugins") or {}


def has_access(settings):
    return bool((settings.get("whisparrUrl") or "").strip() and (settings.get("whisparrApiKey") or "").strip())


def resolve(plugins):
    """The Whisparr access to use and where it comes from: this plugin first, then the fallback plugin.
    Address and key always come from the same plugin, never one from each."""
    own = plugins.get(PLUGIN_ID) or {}
    if has_access(own):
        return own, PLUGIN_ID
    other = plugins.get(FALLBACK_PLUGIN_ID) or {}
    if has_access(other):
        return {"whisparrUrl": other["whisparrUrl"], "whisparrApiKey": other["whisparrApiKey"]}, FALLBACK_PLUGIN_ID
    return own, None


def read_settings(connection):
    """The Whisparr settings to use (see `resolve`)."""
    return resolve(read_all_settings(connection))[0]


def source(connection):
    """The plugin whose Whisparr settings are used, or None. Never raises, `status` calls it."""
    try:
        return resolve(read_all_settings(connection))[1]
    except Exception:
        return None


def base_url(settings):
    url = (settings.get("whisparrUrl") or "").strip()
    key = (settings.get("whisparrApiKey") or "").strip()
    if not url or not key:
        raise WhisparrNotConfigured("Whisparr is not configured in the plugin settings")
    if not re.match(r"^https?://", url, re.IGNORECASE):
        raise WhisparrNotConfigured("whisparrUrl must start with http:// or https://")
    return url.rstrip("/") + "/", key


def forward(settings, args):
    """Sends the request of `args` ({method, path, query, body}) and returns {status, body, contentType}."""
    method = str(args.get("method") or "GET").upper()
    path = str(args.get("path") or "").strip("/")
    if not is_allowed(method, path):
        raise ValueError(f"{method} {path or '/'} is not allowed")
    base, key = base_url(settings)

    query = args.get("query") or []
    # a list of [name, value] pairs keeps repeated names (movieIds) in order
    pairs = [(str(name), str(value)) for name, value in query]
    url = base + path + ("?" + urllib.parse.urlencode(pairs) if pairs else "")

    body = args.get("body")
    data = body.encode() if isinstance(body, str) else None
    headers = {"Accept": "application/json"}
    if path not in _ANONYMOUS:
        headers["X-Api-Key"] = key
    if data is not None:
        headers["Content-Type"] = "application/json"

    request = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with _NO_REDIRECT_OPENER.open(request, timeout=TIMEOUT_SECONDS) as reply:
            return _result(reply.status, reply.headers, _read_bounded(reply))
    except urllib.error.HTTPError as error:
        with error:
            return _result(error.code, error.headers, _read_bounded(error))
    except urllib.error.URLError as error:
        raise ConnectionError(f"Whisparr is not reachable: {error.reason}") from error


def _result(status, headers, raw):
    return {
        "status": status,
        "contentType": headers.get("Content-Type", ""),
        "body": raw.decode("utf-8", errors="replace"),
    }


def op_whisparr(args, server_connection):
    return forward(read_settings(server_connection), args)


def read_state(server_connection):
    """Return (configured, source_plugin_id) from one Stash GraphQL settings query."""
    try:
        settings, src = resolve(read_all_settings(server_connection))
    except Exception:
        return False, None
    if src is None:
        return False, None
    try:
        base_url(settings)
        return True, src
    except WhisparrNotConfigured:
        return False, None


def configured(server_connection):
    """Whether url and key are set. Used by `status` so the app knows before it tries."""
    try:
        base_url(read_settings(server_connection))
        return True
    except Exception:
        return False

#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""Operations of the Stow plugin.

Stash starts this script for every call of runPluginOperation (or a task). It reads the plugin input as JSON
from stdin and writes {"output": ...} or {"error": "..."} to stdout. The operation is chosen with args["op"].
Standard library only, so the plugin works in the stock Stash image without installing anything.
"""

import json
import sys

import whisparr

# Keep in sync with `version` in stow.yml (a test checks it).
VERSION = "1.3.0"

# What the app can rely on. Every module that is added gets its name here.
CAPABILITIES = ["qr", "whisparr"]


def op_status(_args, server_connection):
    return {
        "plugin": "stow",
        "version": VERSION,
        "capabilities": CAPABILITIES,
        # whether Whisparr url and key are set in the plugin settings, so the app knows before it calls
        "whisparrConfigured": whisparr.configured(server_connection),
        # which plugin the Whisparr access comes from: "stow", "missingScenes" or null
        "whisparrSource": whisparr.source(server_connection),
    }


OPERATIONS = {
    "status": op_status,
    "whisparr": whisparr.op_whisparr,
}


def run(plugin_input):
    """Dispatch one call. Returns the dictionary to print."""
    args = plugin_input.get("args") or {}
    name = args.get("op")
    if not isinstance(name, str) or not name:
        return {"error": "missing operation: pass args.op"}
    operation = OPERATIONS.get(name)
    if operation is None:
        return {"error": f"unknown operation: {name}"}
    try:
        return {"output": operation(args, plugin_input.get("server_connection") or {})}
    except Exception as error:  # the app gets a message, Stash does not see a crash
        return {"error": f"{name} failed: {error}"}


def main():
    try:
        plugin_input = json.load(sys.stdin)
    except json.JSONDecodeError as error:
        print(json.dumps({"error": f"invalid plugin input: {error}"}))
        return
    print(json.dumps(run(plugin_input)))


if __name__ == "__main__":
    main()

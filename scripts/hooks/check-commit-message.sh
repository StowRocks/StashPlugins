#!/bin/sh
set -eu
body=$(sed -e '/^#/d' -e '/^diff --git /,$d' "${1:?missing message file}")
subject=$(printf '%s\n' "$body" | sed -e '/^[[:space:]]*$/d' -e 1q)
case "$subject" in "Merge "*|"Revert \""*|"fixup!"*|"squash!"*|"amend!"*) exit 0;; esac
printf '%s' "$subject" | grep -Eq '^(feat|fix|docs|style|refactor|perf|test|build|ci|chore|revert)(\([a-z0-9._/-]+\))?!?: .+' || exit 1
[ "${#subject}" -le 100 ] || exit 1
! printf '%s\n' "$body" | grep -Eiq 'co-authored-by:.*(claude|anthropic)|generated with .*claude'

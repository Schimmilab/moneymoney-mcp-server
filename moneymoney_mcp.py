#!/usr/bin/env python3
"""MoneyMoney MCP server (read-only).

Wraps MoneyMoney's official AppleScript export interface. MoneyMoney holds the
bank credentials; this server only READS via `osascript`. Same pattern as the
things3 MCP.

Requirements at runtime:
- MoneyMoney.app must be RUNNING and its database UNLOCKED (the export commands
  fail while the DB is locked). This is therefore an interactive server, not a
  headless/cron one.

Tools (all read-only):
- mm_accounts       -> accounts + balances
- mm_transactions   -> transactions for one account + date range
- mm_portfolio      -> securities/metals for one depot account
- mm_categories     -> category tree
"""
from __future__ import annotations

import plistlib
import subprocess
from typing import Any

from fastmcp import FastMCP

mcp = FastMCP("moneymoney")

# Keys whose values are bulky/binary and useless to an LLM -> dropped from output
# so a single export doesn't flood the context window (icons are base64 PNGs).
_DROP_KEYS = {"icon"}


class MoneyMoneyError(Exception):
    """Raised when the AppleScript export fails (locked DB, app not running, bad param)."""


def _run_export(applescript: str) -> Any:
    """Run an AppleScript export command and return the parsed, cleaned plist."""
    try:
        proc = subprocess.run(
            ["osascript", "-e", applescript],
            capture_output=True,
            timeout=30,
        )
    except FileNotFoundError:
        raise MoneyMoneyError("osascript not found — this server only runs on macOS.")
    except subprocess.TimeoutExpired:
        raise MoneyMoneyError("MoneyMoney did not respond within 30s. Is the app frozen?")

    if proc.returncode != 0:
        err = proc.stderr.decode("utf-8", "replace").strip()
        low = err.lower()
        if "-1728" in err or "isn't running" in low or "not running" in low:
            raise MoneyMoneyError("MoneyMoney is not running. Open the app first.")
        if "locked" in low or "password" in low:
            raise MoneyMoneyError("MoneyMoney database is locked. Unlock it in the app, then retry.")
        if "-1701" in err or "parameter is missing" in low:
            raise MoneyMoneyError("Missing parameter — this export needs an account name (use mm_accounts to list them).")
        raise MoneyMoneyError(f"MoneyMoney export failed: {err or 'unknown error'}")

    try:
        data = plistlib.loads(proc.stdout)
    except Exception as exc:  # noqa: BLE001
        raise MoneyMoneyError(f"Could not parse MoneyMoney output as plist: {exc}")
    return _clean(data)


def _clean(obj: Any) -> Any:
    """Recursively drop icon/binary blobs so tool output stays lean."""
    if isinstance(obj, dict):
        out = {}
        for k, v in obj.items():
            if k in _DROP_KEYS:
                continue
            if isinstance(v, (bytes, bytearray)):
                continue  # drop stray binary data
            out[k] = _clean(v)
        return out
    if isinstance(obj, list):
        return [_clean(x) for x in obj]
    if isinstance(obj, (bytes, bytearray)):
        return None
    return obj


def _q(value: str) -> str:
    """Quote a string for safe embedding inside an AppleScript double-quoted literal."""
    return value.replace("\\", "\\\\").replace('"', '\\"')


@mcp.tool()
def mm_accounts() -> list[dict]:
    """List all MoneyMoney accounts with balances, currency, type, IBAN and uuid.

    Read-only. Returns one entry per account/group (icons stripped). Use the
    `name` values as the account argument for mm_transactions / mm_portfolio.
    """
    return _run_export('tell application "MoneyMoney" to export accounts')


@mcp.tool()
def mm_transactions(account: str, from_date: str, to_date: str = "") -> dict:
    """Export transactions for ONE account within a date range (read-only).

    account:   account name exactly as shown by mm_accounts (e.g. "Girokonto").
    from_date: ISO date "YYYY-MM-DD" (inclusive).
    to_date:   optional ISO date "YYYY-MM-DD" (inclusive); omit for "up to today".
    """
    script = (
        f'tell application "MoneyMoney" to export transactions '
        f'from account "{_q(account)}" from date "{_q(from_date)}"'
    )
    if to_date:
        script += f' to date "{_q(to_date)}"'
    script += ' as "plist"'
    return _run_export(script)


@mcp.tool()
def mm_portfolio(account: str) -> dict:
    """Export the securities/precious-metals portfolio of ONE depot account (read-only).

    account: depot account name exactly as shown by mm_accounts
             (a securities or precious-metals account).
    """
    return _run_export(
        f'tell application "MoneyMoney" to export portfolio from account "{_q(account)}" as "plist"'
    )


@mcp.tool()
def mm_categories() -> list[dict]:
    """List the MoneyMoney category tree (read-only). Icons stripped."""
    return _run_export('tell application "MoneyMoney" to export categories')


if __name__ == "__main__":
    mcp.run()

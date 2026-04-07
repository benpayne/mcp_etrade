"""Local watch list storage.

E*TRADE's public API does not expose watch list endpoints, so watch lists are
persisted locally under the user config directory, scoped by account id.
"""
import json
import secrets
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from platformdirs import user_config_dir


_FILE = Path(user_config_dir("mcp-etrade")) / "watchlists.json"


def _load() -> Dict[str, Any]:
    try:
        return json.loads(_FILE.read_text())
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return {}


def _save(data: Dict[str, Any]) -> None:
    _FILE.parent.mkdir(parents=True, exist_ok=True)
    _FILE.write_text(json.dumps(data, indent=2))


def _now_ms() -> int:
    return int(time.time() * 1000)


def _account_bucket(data: Dict[str, Any], account_id: str) -> Dict[str, Any]:
    return data.setdefault(account_id, {})


def create(account_id: str, name: str, symbols: Optional[List[str]] = None) -> Dict[str, Any]:
    data = _load()
    bucket = _account_bucket(data, account_id)
    wl_id = "WL" + secrets.token_hex(6).upper()
    record = {
        "watchListId": wl_id,
        "accountId": account_id,
        "name": name,
        "symbols": list(symbols or []),
        "created": _now_ms(),
        "updated": _now_ms(),
        "itemCount": len(symbols or []),
    }
    bucket[wl_id] = record
    _save(data)
    return record


def list_for(account_id: str) -> Dict[str, Any]:
    data = _load()
    bucket = data.get(account_id, {})
    return {
        "accountId": account_id,
        "watchLists": list(bucket.values()),
    }


def update(
    account_id: str,
    watch_list_id: str,
    name: Optional[str] = None,
    symbols: Optional[List[str]] = None,
) -> Dict[str, Any]:
    data = _load()
    bucket = _account_bucket(data, account_id)
    if watch_list_id not in bucket:
        raise KeyError(f"Watch list {watch_list_id} not found for account {account_id}")
    record = bucket[watch_list_id]
    if name is not None:
        record["name"] = name
    if symbols is not None:
        record["symbols"] = list(symbols)
        record["itemCount"] = len(symbols)
    record["updated"] = _now_ms()
    _save(data)
    return record


def delete(account_id: str, watch_list_id: str) -> Dict[str, Any]:
    data = _load()
    bucket = data.get(account_id, {})
    removed = bucket.pop(watch_list_id, None)
    if removed is None:
        raise KeyError(f"Watch list {watch_list_id} not found for account {account_id}")
    _save(data)
    return {
        "watchListId": watch_list_id,
        "accountId": account_id,
        "deleted": True,
        "deletedTime": _now_ms(),
    }

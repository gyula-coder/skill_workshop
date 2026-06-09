#!/usr/bin/env python3
"""
统一配置管理。

仅支持 skill 根目录下的 config.yaml。

用法:
    from config import set_account, get_config, ConfigError
    set_account("小神仙")
    cfg = get_config()  # 返回当前账号的完整配置
"""

from pathlib import Path
from typing import Optional, Dict, List, Any

try:
    import yaml  # pyyaml
except ImportError:
    yaml = None


# ============================================================
# 异常
# ============================================================

class ConfigError(RuntimeError):
    """配置加载失败。由库函数抛出,CLI 层捕获后退出。"""


# ============================================================
# 全局激活账号
# ============================================================

_active_account: Optional[str] = None


def set_account(account_name: Optional[str]) -> None:
    """设置当前激活的账号(全局,影响后续所有调用)。"""
    global _active_account
    _active_account = account_name


def get_account_name() -> Optional[str]:
    """读取当前激活的账号名。"""
    return _active_account


# ============================================================
# 统一配置加载
# ============================================================

UNIFIED_CONFIG_NAME = "config.yaml"
PLACEHOLDER_SECRETS = {
    "",
    "your_app_secret_here",
    "your-app-secret-here",
    "replace_me",
    "changeme",
}


def _config_path() -> Path:
    return Path(__file__).parent.parent / UNIFIED_CONFIG_NAME


def _parse_scalar(value: str) -> Any:
    value = value.strip()
    if not value:
        return ""
    if value.startswith(("\"", "'")) and value.endswith(("\"", "'")):
        return value[1:-1]
    if value.startswith("[") and value.endswith("]"):
        inner = value[1:-1].strip()
        if not inner:
            return []
        return [_parse_scalar(item.strip()) for item in inner.split(",")]
    if value.lower() in {"true", "false"}:
        return value.lower() == "true"
    return value


def _simple_yaml_load(text: str) -> Dict[str, Any]:
    """Small YAML subset parser used when PyYAML is unavailable.

    Supports the config shape used by config.yaml.example:
    top-level scalars, top-level sections, nested account mappings, lists
    written as `[a, b]`, and literal block values introduced by `|`.
    """
    data: Dict[str, Any] = {}
    current_section: Optional[str] = None
    current_item: Optional[str] = None
    pending_block: Optional[tuple[Dict[str, Any], str, int, List[str]]] = None
    lines = text.splitlines()

    def flush_block() -> None:
        nonlocal pending_block
        if not pending_block:
            return
        target, key, _, collected = pending_block
        target[key] = "\n".join(collected).rstrip()
        pending_block = None

    for raw in lines:
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue

        indent = len(raw) - len(raw.lstrip(" "))
        stripped = raw.strip()

        if pending_block:
            target, key, block_indent, collected = pending_block
            if indent > block_indent:
                collected.append(raw[block_indent + 2:] if len(raw) > block_indent + 2 else "")
                continue
            flush_block()

        if indent == 0:
            current_item = None
            if stripped.endswith(":"):
                current_section = stripped[:-1]
                data[current_section] = {}
                continue
            if ":" in stripped:
                key, value = stripped.split(":", 1)
                data[key.strip()] = _parse_scalar(value)
                current_section = None
            continue

        if current_section is None:
            continue

        section = data.setdefault(current_section, {})
        if indent == 2:
            if stripped.endswith(":"):
                current_item = stripped[:-1]
                section[current_item] = {}
                continue
            if ":" in stripped:
                key, value = stripped.split(":", 1)
                section[key.strip()] = _parse_scalar(value)
            continue

        if indent >= 4 and current_item and isinstance(section.get(current_item), dict):
            if ":" not in stripped:
                continue
            key, value = stripped.split(":", 1)
            key = key.strip()
            value = value.strip()
            target = section[current_item]
            if value == "|":
                pending_block = (target, key, indent, [])
            else:
                target[key] = _parse_scalar(value)

    flush_block()
    return data


def _load_yaml(path: Path) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    if yaml is not None:
        data = yaml.safe_load(content)
    else:
        data = _simple_yaml_load(content)
    return data if isinstance(data, dict) else {}


def _find_unified_yaml() -> Optional[Path]:
    """仅查找 skill 根目录下的 config.yaml。"""
    path = _config_path()
    return path if path.exists() else None


def load_env() -> None:
    """
    兼容旧调用入口。当前草稿发布配置不需要额外环境变量。
    """
    return None


def _load_config_yaml(yaml_path: Optional[Path] = None) -> Optional[Dict[str, Any]]:
    """加载 skill 根目录 config.yaml。返回 None 表示找不到文件。"""
    if yaml_path is None:
        yaml_path = _find_unified_yaml()
    if yaml_path is None:
        return None
    return _load_yaml(yaml_path)


def list_accounts() -> List[Dict[str, Any]]:
    """
    列出所有已配置的账号。

    返回统一 schema:
        {"key": str, "name": str, "app_id": str(截短), "author": str, "is_default": bool}
    """
    config = _load_config_yaml()
    if not config or "accounts" not in config:
        return []

    default_name = config.get("default", "")
    result = []
    for key, acc in config["accounts"].items():
        app_id = acc.get("app_id", "") or ""
        result.append({
            "key": key,
            "name": acc.get("name", key),
            "app_id": (app_id[:8] + "...") if app_id else "",
            "author": acc.get("author", "") or "",
            "is_default": key == default_name,
        })
    return result


def get_report_config() -> Dict[str, Any]:
    """读取报告输出相关配置,缺失时返回最小默认值。"""
    yaml_config = _load_config_yaml() or {}
    report = yaml_config.get("report") or {}
    limits = report.get("limits") or {}
    return {
        "output_root": report.get("output_root", "./output") or "./output",
        "default_period": report.get("default_period", "daily") or "daily",
        "limits": {
            "daily": int(limits.get("daily", 10) or 10),
            "weekly": int(limits.get("weekly", 15) or 15),
            "monthly": int(limits.get("monthly", 20) or 20),
        },
    }


def get_publish_config() -> Dict[str, Any]:
    """读取发布流程配置,缺失时返回最小默认值。"""
    yaml_config = _load_config_yaml() or {}
    publish = yaml_config.get("publish") or {}
    try:
        image_upload_workers = int(publish.get("image_upload_workers", 4) or 4)
    except (TypeError, ValueError):
        image_upload_workers = 4
    return {
        "image_upload_workers": max(1, min(image_upload_workers, 16)),
    }


def get_config(account_name: Optional[str] = None) -> Dict[str, Any]:
    """
    获取当前账号的完整配置。

    优先级:
      1. account_name 参数
      2. set_account() 设置的全局账号
      3. config.yaml 的 `default` 字段

    Raises:
        ConfigError: 配置文件缺失、账号不存在、或缺少必要字段(app_id/app_secret)

    Returns:
        dict: {
            "app_id": str,
            "app_secret": str,
            "author": str,
            "account_key": str,
            "account_name": str,
            "theme": str,
        }
    """
    account_name = account_name or _active_account

    yaml_config = _load_config_yaml()
    if not yaml_config or "accounts" not in yaml_config or not yaml_config["accounts"]:
        raise ConfigError(
            "未找到 config.yaml 或文件为空。请参考 config.yaml.example 创建配置。"
        )

    if account_name is None:
        account_name = yaml_config.get("default")

    if account_name is None:
        available = ", ".join(yaml_config["accounts"].keys())
        raise ConfigError(
            f"未指定账号且 config.yaml 里无 default。可用账号: {available}"
        )

    if account_name not in yaml_config["accounts"]:
        available = ", ".join(yaml_config["accounts"].keys())
        raise ConfigError(
            f"未找到账号 '{account_name}'。可用账号: {available}"
        )

    acc = yaml_config["accounts"][account_name]
    app_id = acc.get("app_id", "")
    app_secret = acc.get("app_secret", "")
    if not app_id or not app_secret:
        raise ConfigError(
            f"账号 '{account_name}' 缺少 app_id 或 app_secret"
        )
    if app_secret.strip() in PLACEHOLDER_SECRETS:
        raise ConfigError(
            f"账号 '{account_name}' 的 app_secret 仍是示例占位值，请先替换为真实配置"
        )

    return {
        "app_id": app_id,
        "app_secret": app_secret,
        "author": acc.get("author", "") or "",
        "account_key": account_name,
        "account_name": acc.get("name", account_name),
        "theme": acc.get("theme", "") or "",
    }

from __future__ import annotations

from pathlib import Path


def _parse_scalar(value: str):
    value = value.split("#", 1)[0].strip()
    if not value:
        return ""
    if value.startswith("[") and value.endswith("]"):
        body = value[1:-1].strip()
        if not body:
            return []
        return [_parse_scalar(part.strip()) for part in body.split(",")]
    if (value.startswith('"') and value.endswith('"')) or (
        value.startswith("'") and value.endswith("'")
    ):
        return value[1:-1]
    lowered = value.lower()
    if lowered == "true":
        return True
    if lowered == "false":
        return False
    if lowered in {"null", "none"}:
        return None
    try:
        if any(ch in value for ch in ".eE"):
            return float(value)
        return int(value)
    except ValueError:
        return value


def load_config(path: str | Path) -> dict:
    """Load the project's simple two-level YAML config."""
    path = Path(path)
    try:
        import yaml  # type: ignore

        with path.open(encoding="utf-8") as f:
            return yaml.safe_load(f)
    except ModuleNotFoundError:
        cfg: dict[str, dict] = {}
        current: dict | None = None
        for raw in path.read_text(encoding="utf-8").splitlines():
            if not raw.strip() or raw.lstrip().startswith("#"):
                continue
            if not raw.startswith(" ") and raw.rstrip().endswith(":"):
                key = raw.split(":", 1)[0].strip()
                current = {}
                cfg[key] = current
                continue
            if current is not None and ":" in raw:
                key, value = raw.split(":", 1)
                current[key.strip()] = _parse_scalar(value)
        return cfg


def _format_scalar(value) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if value is None:
        return "null"
    if isinstance(value, str):
        if any(ch in value for ch in ":#[]{}") or "\\" in value or " " in value:
            return '"' + value.replace('"', '\\"') + '"'
        return value
    if isinstance(value, (list, tuple)):
        return "[" + ", ".join(_format_scalar(item) for item in value) + "]"
    return str(value)


def dump_config(config: dict, path: str | Path) -> None:
    """Write the project's simple two-level YAML config."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    lines: list[str] = []
    for section, values in config.items():
        lines.append(f"{section}:")
        if isinstance(values, dict):
            for key, value in values.items():
                lines.append(f"  {key}: {_format_scalar(value)}")
        else:
            lines.append(f"  value: {_format_scalar(values)}")
        lines.append("")
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")

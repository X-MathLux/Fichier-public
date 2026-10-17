#!/usr/bin/env python3
"""Validate the checked-in Codex resources without external dependencies."""
from __future__ import annotations

import json
from pathlib import Path
import re
import sys
import tomllib
from urllib.parse import unquote, urlparse


ROOT = Path(__file__).resolve().parents[1]
ROLES = {"researcher", "architect", "implementer", "verifier", "reviewer", "integrator"}
SKILLS = {"project-kickoff", "project-orchestrate", "project-research", "project-close"}
FEATURES = {"shell_tool", "apps", "plugins", "memories", "request_permissions_tool"}


def validate(root: Path) -> list[str]:
    errors = []

    def require(condition, message):
        if not condition:
            errors.append(message)

    def parse_toml(path):
        try:
            return tomllib.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            errors.append(f"{path.relative_to(root)}: {exc}")
            return {}

    try:
        project = json.loads((root / "project.json").read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        errors.append(f"project.json: {exc}")
        project = {}
    codex = parse_toml(root / ".codex/config.toml")
    require(codex.get("agents", {}).get("enabled") is True, "Codex agents must be enabled")
    require(codex.get("agents", {}).get("max_concurrent_threads_per_session") ==
            project.get("orchestration", {}).get("max_parallel_agents"),
            "Native Codex concurrency and project concurrency must match")
    roles = list((root / ".codex/agents").glob("*.toml"))
    names = []
    for path in roles:
        role = parse_toml(path)
        names.append(role.get("name"))
        require(role.get("name") == path.stem, f"{path.name}: name differs from filename")
        for key in ("name", "description", "developer_instructions"):
            require(isinstance(role.get(key), str) and bool(role[key].strip()), f"{path.name}: missing {key}")
        require(set(role) <= {"name", "description", "developer_instructions", "features"},
                f"{path.name}: unexpected setting; review current native agent schema")
        features = role.get("features", {})
        require(isinstance(features, dict) and set(features) <= FEATURES and
                all(type(value) is bool for value in features.values()), f"{path.name}: invalid capability overrides")
        require(features.get("memories") is False and features.get("request_permissions_tool") is False,
                f"{path.name}: specialist capability policy differs from documented policy")
    require(set(names) == ROLES and len(names) == len(ROLES), "Six distinct specialist roles are required")

    skills = list((root / ".agents/skills").glob("*/SKILL.md"))
    skill_names = []
    for path in skills:
        text = path.read_text(encoding="utf-8")
        match = re.match(r"\A---\r?\n(.*?)\r?\n---(?:\r?\n|$)", text, re.S)
        require(match is not None, f"{path.parent.name}: missing skill frontmatter")
        if match:
            frontmatter = match.group(1)
            name = re.search(r"^name:\s*([a-z0-9-]+)\s*$", frontmatter, re.M)
            description = re.search(r"^description:\s*(\S.+)$", frontmatter, re.M)
            require(name is not None and name.group(1) == path.parent.name,
                    f"{path.parent.name}: skill name differs from folder")
            require(description is not None, f"{path.parent.name}: missing skill description")
            if name:
                skill_names.append(name.group(1))
    require(set(skill_names) == SKILLS and len(skill_names) == len(SKILLS), "Four distinct project skills are required")

    instructions = root / "AGENTS.md"
    require(instructions.is_file() and instructions.stat().st_size <= 8192, "Keep AGENTS.md within 8 KiB")
    # Check local Markdown targets, including resource links inside skills.
    for path in root.rglob("*.md"):
        if any(part in {".git", ".local", "__pycache__"} for part in path.relative_to(root).parts):
            continue
        for raw in re.findall(r"\[[^\]]*\]\(([^)]+)\)", path.read_text(encoding="utf-8")):
            target = raw.strip().strip("<>")
            parsed = urlparse(target)
            if parsed.scheme or not parsed.path:
                continue
            resolved = (path.parent / unquote(parsed.path)).resolve()
            require(resolved.is_relative_to(root) and resolved.exists(),
                    f"{path.relative_to(root)}: missing or external local target {target}")
    workflow = root / ".github/workflows/ci.yml"
    if workflow.exists():
        text = workflow.read_text(encoding="utf-8")
        uses = re.findall(r"^\s*- uses:\s*(\S+)", text, re.M)
        require(bool(uses) and all(re.fullmatch(r"actions/[a-z-]+@[0-9a-f]{40}", use) for use in uses),
                "CI actions must use reviewed full commit pins")
    else:
        errors.append("Missing template CI workflow")
    return errors


def main():
    errors = validate(ROOT)
    for error in errors:
        print(f"ERROR: {error}", file=sys.stderr)
    if errors:
        return 1
    print("Template resources valid: roles, skills, configuration, local links and CI pins.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

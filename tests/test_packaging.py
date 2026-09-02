"""Packaging contract for the tools-only base install."""

from __future__ import annotations

import re
import subprocess
import sys
import tomllib
from pathlib import Path


ROOT = Path(__file__).parents[1]
TOOL_DEPENDENCIES = {
    "beautifulsoup4",
    "httpx",
    "lxml",
    "pydantic",
    "pymupdf",
    "rank-bm25",
    "tenacity",
    "tiktoken",
}
EVAL_DEPENDENCIES = {
    "click",
    "google-auth",
    "google-cloud-aiplatform",
    "litellm",
}


def _names(requirements: list[str]) -> set[str]:
    return {
        re.split(r"[<>=!~ ;\[]", requirement, maxsplit=1)[0].lower().replace("_", "-")
        for requirement in requirements
    }


def test_dependency_extras_preserve_tools_only_base() -> None:
    project = tomllib.loads((ROOT / "pyproject.toml").read_text())["project"]
    extras = project["optional-dependencies"]

    assert _names(project["dependencies"]) == TOOL_DEPENDENCIES
    assert "pydantic>=2.12.5,<3" in project["dependencies"]
    assert "tenacity>=9.1.4" in project["dependencies"]
    assert _names(extras["eval"]) == EVAL_DEPENDENCIES
    assert _names(extras["full"]) == EVAL_DEPENDENCIES | _names(extras["analysis"])


def test_tools_import_without_eval_provider_stack() -> None:
    """Catch accidental imports from tools into model/provider-only modules."""

    code = """
import sys

sys.modules["litellm"] = None
sys.modules["google"] = None

import big_finance_harness.tools
"""
    subprocess.run([sys.executable, "-c", code], cwd=ROOT, check=True)

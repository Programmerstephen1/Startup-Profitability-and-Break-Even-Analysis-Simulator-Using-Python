"""Scenario management: save and load simulation scenarios to/from JSON files."""
import json
import os
from pathlib import Path
from typing import Dict, List


SCENARIOS_DIR = Path(__file__).parent.parent / "scenarios"


def ensure_scenarios_dir():
    """Ensure the scenarios directory exists."""
    SCENARIOS_DIR.mkdir(exist_ok=True)


def save_scenario(name: str, params: Dict) -> str:
    """Save a scenario to disk. Returns the file path."""
    ensure_scenarios_dir()
    filepath = SCENARIOS_DIR / f"{name}.json"
    with open(filepath, 'w') as f:
        json.dump(params, f, indent=2)
    return str(filepath)


def load_scenario(name: str) -> Dict:
    """Load a scenario from disk by name."""
    ensure_scenarios_dir()
    filepath = SCENARIOS_DIR / f"{name}.json"
    if not filepath.exists():
        raise FileNotFoundError(f"Scenario '{name}' not found")
    with open(filepath, 'r') as f:
        return json.load(f)


def list_scenarios() -> List[str]:
    """Return list of saved scenario names (without .json extension)."""
    ensure_scenarios_dir()
    return [f.stem for f in SCENARIOS_DIR.glob("*.json")]


def delete_scenario(name: str) -> bool:
    """Delete a scenario file. Returns True if deleted, False if not found."""
    ensure_scenarios_dir()
    filepath = SCENARIOS_DIR / f"{name}.json"
    if filepath.exists():
        filepath.unlink()
        return True
    return False

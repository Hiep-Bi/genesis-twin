"""
Quick demo runner for the 3 core features.

Usage:
    python demo_core_features.py --base-url http://localhost:8000 \
        --email admin@genesis.ai --password admin123
"""
import argparse
import json
import sys
from pathlib import Path
from typing import Dict, Any

import requests

ROOT = Path(__file__).resolve().parent
DEMO_FILES = {
    "ai": ROOT / "demo_data_ai_predictions.json",
    "recovery": ROOT / "demo_data_recovery.json",
    "agv": ROOT / "demo_data_agv_fallback.json",
}


def load_json(path: Path) -> Any:
    if not path.exists():
        raise FileNotFoundError(f"Demo file not found: {path}")
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def login(base_url: str, email: str, password: str) -> str:
    resp = requests.post(
        f"{base_url}/api/v1/auth/login",
        json={"username": email, "password": password},
        timeout=15,
    )
    resp.raise_for_status()
    token = resp.json().get("access_token")
    if not token:
        raise RuntimeError("Login success but no access token returned")
    return token


def call_endpoint(base_url: str, token: str, path: str, payload: Any) -> Dict[str, Any]:
    resp = requests.post(
        f"{base_url}{path}",
        json=payload,
        headers={"Authorization": f"Bearer {token}"},
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()


def demo_ai_predictions(base_url: str, token: str):
    data = load_json(DEMO_FILES["ai"])
    result = call_endpoint(
        base_url, token, "/api/v1/ai/predictions/advanced-defect", data
    )
    first = result["predictions"][0]
    print("\n=== AI Predictions ===")
    print("Status:", first.get("status"))
    print("Root cause:", first["detailed_analysis"]["diagnosis"]["issue_detected"])
    print("Confidence:", first.get("confidence"))
    golden = (
        first["detailed_analysis"]
        .get("maintenance_recommendation", {})
        .get("optimal_scheduling", {})
        .get("golden_slot", {})
    )
    if golden:
        print(
            "Golden Slot:",
            golden.get("date"),
            golden.get("time_range"),
            "-", golden.get("reason"),
        )


def demo_recovery(base_url: str, token: str):
    data = load_json(DEMO_FILES["recovery"])
    result = call_endpoint(
        base_url, token, "/api/v1/factory/recovery/analyze", data
    )
    print("\n=== Production Line Recovery ===")
    for item in result.get("prioritized_lines", [])[:3]:
        print(
            f"Line {item['line_code']} - Score {item['priority_score']} "
            f"- Reason: {item.get('reasons', [''])[0]}"
        )


def demo_agv_fallback(base_url: str, token: str):
    data = load_json(DEMO_FILES["agv"])
    result = call_endpoint(
        base_url, token, "/api/v1/factory/agv-fallback/handle-failure", data
    )
    print("\n=== AGV Fallback ===")
    for item in result.get("prioritized_lines", [])[:3]:
        print(
            f"Line {item['line_code']} - Material source: "
            f"{item.get('material_strategy', 'unknown')}"
        )
    instructions = result.get("fallback_instructions", [])
    if instructions:
        print("Instruction:", instructions[0])


def main():
    parser = argparse.ArgumentParser(description="Demo core features quickly")
    parser.add_argument("--base-url", default="http://localhost:8000")
    parser.add_argument("--email", default="admin@genesis.ai")
    parser.add_argument("--password", default="admin123")
    parser.add_argument("--token", help="Existing JWT access token")
    args = parser.parse_args()

    token = args.token or login(args.base_url, args.email, args.password)

    try:
        demo_ai_predictions(args.base_url, token)
        demo_recovery(args.base_url, token)
        demo_agv_fallback(args.base_url, token)
    except requests.HTTPError as exc:
        print("Request failed:", exc.response.text, file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()


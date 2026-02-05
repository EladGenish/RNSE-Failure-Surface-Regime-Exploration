#!/usr/bin/env python3
"""
verify_replay.py — RNSE Failure Surface MSE Replay Validator (v1.0)

Surface-only verification:
- required files exist
- SHA-256 per retained artifact matches digests.json
- bundle digest matches bundle_manifest.json

NOTE: digests.json does NOT include a hash of itself or bundle_manifest.json
(to avoid circular hashing). Those are validated separately by this script.
"""

import hashlib
import json
import sys
from pathlib import Path

def sha256_file(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()

def canonical_json(obj) -> bytes:
    s = json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return (s + "\n").encode("utf-8")

def canonical_hash(obj) -> str:
    return hashlib.sha256(canonical_json(obj)).hexdigest()

REQUIRED = [
    "README.md",
    "config.json",
    "regime_summary.json",
    "digests.json",
    "bundle_manifest.json",
    "verify_replay.py",
]

def main(bundle_path: Path) -> int:
    errors = []
    mismatches = []

    for f in REQUIRED:
        if not (bundle_path / f).exists():
            errors.append(f"Missing required file: {f}")

    if errors:
        print(json.dumps({"valid": False, "errors": errors, "digest_mismatches": []}, indent=2))
        return 1

    try:
        digests = json.loads((bundle_path / "digests.json").read_text(encoding="utf-8"))
    except Exception as e:
        print(json.dumps({"valid": False, "errors": [f"Failed to read digests.json: {e}"], "digest_mismatches": []}, indent=2))
        return 1

    # Verify declared artifact hashes
    for fname, declared in digests.items():
        p = bundle_path / fname
        if not p.exists():
            mismatches.append(f"{fname}: declared but missing")
            continue
        h = sha256_file(p)
        if h != declared:
            mismatches.append(f"{fname}: {declared} != {h}")

    # Validate bundle manifest digest
    try:
        manifest = json.loads((bundle_path / "bundle_manifest.json").read_text(encoding="utf-8"))
    except Exception as e:
        errors.append(f"Failed to read bundle_manifest.json: {e}")
        manifest = None

    bundle_digest_ok = False
    recomputed_bundle_digest = None
    if manifest is not None:
        bundle_input = {
            "mse_version": manifest.get("mse_version"),
            "artifact_digests": manifest.get("artifact_digests"),
        }
        recomputed_bundle_digest = canonical_hash(bundle_input)
        bundle_digest_ok = (recomputed_bundle_digest == manifest.get("bundle_digest"))
        if not bundle_digest_ok:
            mismatches.append(f"bundle_digest: {manifest.get('bundle_digest')} != {recomputed_bundle_digest}")

        if manifest.get("artifact_digests") != digests:
            mismatches.append("manifest.artifact_digests != digests.json content")

    valid = (not errors) and (not mismatches) and bundle_digest_ok

    out = {
        "valid": valid,
        "errors": errors,
        "digest_mismatches": mismatches,
        "bundle_digest_recomputed": recomputed_bundle_digest,
        "sha256_digests_json": sha256_file(bundle_path / "digests.json"),
        "sha256_bundle_manifest_json": sha256_file(bundle_path / "bundle_manifest.json"),
    }
    print(json.dumps(out, indent=2))
    print("\nVALID:", valid)
    return 0 if valid else 2

if __name__ == "__main__":
    p = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
    raise SystemExit(main(p.resolve()))

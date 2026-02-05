#!/usr/bin/env python3
"""
verify_replay.py — RNSE Failure Surface MSE Replay Validator (v1.0)

Surface-only verification:
- checks required files exist
- verifies SHA-256 digests over raw bytes
- computes bundle digest over a canonicalized manifest object
- prints PASS/FAIL

No RNSE internals are required.
"""

import hashlib
import json
import sys
from pathlib import Path

MSE_VERSION = "1.0"

REQUIRED = [
    "README.md",
    "config.json",
    "regime_summary.json",
    "digests.json",
    "bundle_manifest.json",
    "verify_replay.py",
]

OPTIONAL = [
    "pitch_summary.json",
    "failure_surfaces.png",
    "phase_maps.png",
]

def sha256_file(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()

def canonical_json(obj) -> bytes:
    s = json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return (s + "\n").encode("utf-8")

def canonical_hash(obj) -> str:
    return hashlib.sha256(canonical_json(obj)).hexdigest()

def main(bundle_path: Path) -> int:
    errors = []

    # 1) Existence checks
    for f in REQUIRED:
        if not (bundle_path / f).exists():
            errors.append(f"Missing required file: {f}")

    if errors:
        print(json.dumps({"valid": False, "errors": errors}, indent=2))
        return 1

    # 2) Load digests.json
    try:
        digests = json.loads((bundle_path / "digests.json").read_text(encoding="utf-8"))
    except Exception as e:
        print(json.dumps({"valid": False, "errors": [f"Failed to read digests.json: {e}"]}, indent=2))
        return 1

    # 3) Compute digests for declared files
    mismatches = []
    computed = {}
    for fname, declared in digests.items():
        p = bundle_path / fname
        if not p.exists():
            mismatches.append(f"{fname}: declared but missing")
            continue
        h = sha256_file(p)
        computed[fname] = h
        if h != declared:
            mismatches.append(f"{fname}: {declared} != {h}")

    # 4) Validate bundle manifest digest
    try:
        manifest = json.loads((bundle_path / "bundle_manifest.json").read_text(encoding="utf-8"))
    except Exception as e:
        errors.append(f"Failed to read bundle_manifest.json: {e}")
        manifest = None

    bundle_digest_ok = False
    recomputed_bundle_digest = None
    if manifest is not None:
        # Recompute digest from canonicalized object with only mse_version + artifacts digests
        bundle_input = {
            "mse_version": manifest.get("mse_version"),
            "artifact_digests": manifest.get("artifact_digests"),
        }
        recomputed_bundle_digest = canonical_hash(bundle_input)
        bundle_digest_ok = (recomputed_bundle_digest == manifest.get("bundle_digest"))

        if not bundle_digest_ok:
            mismatches.append(f"bundle_digest: {manifest.get('bundle_digest')} != {recomputed_bundle_digest}")

    valid = (len(mismatches) == 0 and len(errors) == 0 and bundle_digest_ok)

    out = {
        "valid": valid,
        "mse_version": MSE_VERSION,
        "errors": errors,
        "digest_mismatches": mismatches,
        "bundle_digest_recomputed": recomputed_bundle_digest,
    }
    print(json.dumps(out, indent=2))
    print("\nVALID:", valid)
    return 0 if valid else 2

if __name__ == "__main__":
    p = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
    raise SystemExit(main(p.resolve()))

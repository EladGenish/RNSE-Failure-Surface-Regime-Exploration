# RNSE Failure Surface — MSE Replay Bundle (v1.0)

This folder is a **surface-only, portable replay spine** for verifying the *failure-surface / regime-summary* claim **without** RNSE internals.

RNSE is treated as a **black-box testbed**. The bundle locks **evidence**, not implementation.

## What you can verify from this bundle
- Byte-stable integrity of the retained artifacts (SHA-256)
- Bundle-level digest over a canonicalized manifest
- A deterministic verification pass/fail over the retained **surface outputs** (no regeneration)

## How to verify (any machine)
```bash
python verify_replay.py .
```

Expected output:
- `VALID: True/False`
- Per-file hash checks
- Bundle digest

## Retained artifacts
- `config.json` — run spec (seed64, T, constraint thresholds, method list)
- `regime_summary.json` — regime metrics by method (audit object)
- `pitch_summary.json` — headline admissible fractions (human-readable)
- `failure_surfaces.png` — visualization (optional for audit, useful for reviewers)
- `phase_maps.png` — additional visualization (optional)
- `digests.json` — SHA-256 per retained file
- `bundle_manifest.json` — canonical manifest + bundle digest
- `verify_replay.py` — self-contained validator

## Non-goals
This bundle does **not**:
- disclose engine internals
- require engine determinism
- regenerate plots or metrics
- define how RNSE works

It only verifies that the **surface evidence** is intact and matches the declared digests.

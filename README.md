# RNSE Failure Surface — MSE Replay Bundle (v1.0)

Surface-only verification bundle for the RNSE failure-surface / regime-summary outputs.
RNSE internals are out of scope. This bundle locks evidence, not implementation.

## Verify
```bash
python verify_replay.py .
```

Checks:
- required files exist
- SHA-256 per retained artifact matches `digests.json`
- bundle digest matches `bundle_manifest.json`

## Note on hashing
`digests.json` intentionally does NOT include hashes of itself or `bundle_manifest.json`
to avoid circular hashing. The verifier validates those separately.

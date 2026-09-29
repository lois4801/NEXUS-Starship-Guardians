"""Tests use explicit local-only mode; production fails closed without an admin key."""
import os
os.environ.setdefault("NEXUS_DEV_MODE", "true")

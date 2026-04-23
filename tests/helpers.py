"""Test helpers — shared utilities for the test suite."""


def auth_header(token: str) -> dict:
    """Helper to create Authorization header."""
    return {"Authorization": f"Bearer {token}"}

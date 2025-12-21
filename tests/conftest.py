"""Pytest configuration and shared fixtures."""

import pytest
from unittest.mock import patch


# Note: Each test file patches kubernetes config at import time.
# This conftest provides additional shared fixtures if needed.

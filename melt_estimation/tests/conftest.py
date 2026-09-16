import os
import tempfile
import pytest

@pytest.fixture
def tmp_run_dir():
    d = tempfile.TemporaryDirectory()
    yield d.name
    d.cleanup()
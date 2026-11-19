from pathlib import Path

import pytest


REPOSITORY = Path(__file__).resolve().parent.parent
ROOT = REPOSITORY / "ROOT"
ARCHIVE = REPOSITORY / "openmc_archive"
ARCHIVE_VERSIONS = sorted(path for path in ARCHIVE.iterdir() if path.is_dir())


@pytest.fixture(params=[ROOT, *ARCHIVE_VERSIONS], ids=lambda path: path.name)
def result_root(request):
    return request.param


@pytest.fixture(params=ARCHIVE_VERSIONS, ids=lambda path: path.name)
def archive_version(request):
    return request.param

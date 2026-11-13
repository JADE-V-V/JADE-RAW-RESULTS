import json
import subprocess

import pytest

from tests.checks.result_history_test import (
    check_openmc_archive,
    check_overwritten_versions,
    git_output,
)


@pytest.fixture
def history_repository(tmp_path):
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    benchmark = tmp_path / "ROOT" / "_mcnp_-_FENDL 3.2c_" / "Bench"
    benchmark.mkdir(parents=True)
    (benchmark / "metadata.json").write_text(
        json.dumps({"code_version": "6.2"}), encoding="utf-8"
    )
    (benchmark / "result.csv").write_text("value\n1\n", encoding="utf-8")
    git_output(tmp_path, "add", "ROOT")
    git_output(
        tmp_path, "-c", "user.name=Test", "-c", "user.email=test@example.com",
        "-c", "commit.gpgsign=false", "commit", "-q", "--no-verify", "-m", "baseline",
        "-m", "Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>",
    )
    return tmp_path, benchmark


@pytest.mark.parametrize(
    ("version", "should_fail"),
    [("6.2", False), ("6.10", False), ("6.1", True), ("unknown", True), (None, True)],
)
def test_overwritten_result_versions(history_repository, version, should_fail):
    repository, benchmark = history_repository
    (benchmark / "metadata.json").write_text(
        json.dumps({"code_version": version}), encoding="utf-8"
    )
    (benchmark / "result.csv").write_text("value\n2\n", encoding="utf-8")
    if should_fail:
        with pytest.raises(AssertionError):
            check_overwritten_versions(repository, "HEAD")
    else:
        check_overwritten_versions(repository, "HEAD")


def test_overwrites_compare_against_selected_git_revision(history_repository):
    repository, benchmark = history_repository
    base = git_output(repository, "rev-parse", "HEAD").decode().strip()
    (benchmark / "metadata.json").write_text(
        json.dumps({"code_version": "6.1"}), encoding="utf-8"
    )
    git_output(repository, "add", "ROOT")
    git_output(
        repository, "-c", "user.name=Test", "-c", "user.email=test@example.com",
        "-c", "commit.gpgsign=false", "commit", "-q", "--no-verify", "-m", "update",
        "-m", "Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>",
    )
    with pytest.raises(AssertionError, match="downgrade"):
        check_overwritten_versions(repository, base)
    check_overwritten_versions(repository, "HEAD")


def test_legacy_versions_are_only_accepted_when_unchanged(history_repository):
    repository, benchmark = history_repository
    metadata = benchmark / "metadata.json"
    metadata.write_text(json.dumps({"code_version": "d1suned411"}), encoding="utf-8")
    git_output(repository, "add", "ROOT")
    git_output(
        repository, "-c", "user.name=Test", "-c", "user.email=test@example.com",
        "-c", "commit.gpgsign=false", "commit", "-q", "--no-verify", "-m", "legacy",
        "-m", "Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>",
    )
    (benchmark / "result.csv").write_text("value\n2\n", encoding="utf-8")
    check_overwritten_versions(repository, "HEAD")
    metadata.write_text(json.dumps({"code_version": "d1suned412"}), encoding="utf-8")
    with pytest.raises(AssertionError, match="Cannot compare"):
        check_overwritten_versions(repository, "HEAD")


def test_openmc_result_must_match_archive(tmp_path):
    root = tmp_path / "ROOT"
    benchmark = root / "_openmc_-_FENDL 3.2c_" / "Bench"
    benchmark.mkdir(parents=True)
    (benchmark / "metadata.json").write_text(
        json.dumps({"code_version": "0.15.3"}), encoding="utf-8"
    )
    (benchmark / "result.csv").write_text("value\n1\n", encoding="utf-8")
    archive = tmp_path / "openmc_archive"
    with pytest.raises(AssertionError, match="Missing archived result"):
        check_openmc_archive(root, archive)

    archived = archive / "0.15.3" / benchmark.relative_to(root)
    archived.mkdir(parents=True)
    for file in benchmark.iterdir():
        (archived / file.name).write_bytes(file.read_bytes())
    check_openmc_archive(root, archive)

    (archived / "result.csv").write_text("value\n2\n", encoding="utf-8")
    with pytest.raises(AssertionError, match="differs from ROOT"):
        check_openmc_archive(root, archive)

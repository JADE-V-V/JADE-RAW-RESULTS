import json
import os
from pathlib import Path
import subprocess

from packaging.version import InvalidVersion, Version

from tests.conftest import ARCHIVE, REPOSITORY, ROOT


def git_output(repository, *args):
    return subprocess.run(
        ["git", "-C", str(repository), *args],
        check=True,
        stdout=subprocess.PIPE,
    ).stdout


def check_overwritten_versions(repository, base_ref):
    changes = git_output(
        repository, "diff", "--name-status", "-z", "--no-renames", base_ref,
        "--", "ROOT", "openmc_archive",
    ).split(b"\0")
    benchmarks = set()
    for status, raw_path in zip(changes[::2], changes[1::2]):
        if status not in (b"M", b"T"):
            continue
        path = Path(os.fsdecode(raw_path))
        parts = path.parts
        if parts[0] == "ROOT" and len(parts) == 4:
            if parts[1] == "_exp_-_exp_":
                continue
        elif parts[0] != "openmc_archive" or len(parts) != 5:
            continue
        if path.name == "metadata.json" or path.suffix.lower() == ".csv":
            benchmarks.add(path.parent)

    for benchmark in sorted(benchmarks):
        metadata_path = benchmark / "metadata.json"
        old_metadata = json.loads(
            git_output(repository, "show", f"{base_ref}:{metadata_path.as_posix()}")
        )
        with (repository / metadata_path).open(encoding="utf-8") as infile:
            new_metadata = json.load(infile)
        old_version = old_metadata.get("code_version")
        new_version = new_metadata.get("code_version")
        assert isinstance(old_version, str) and old_version.strip(), (
            f"Missing old code_version for {metadata_path} at {base_ref}"
        )
        assert isinstance(new_version, str) and new_version.strip(), (
            f"Missing new code_version for {metadata_path}"
        )
        if old_version == new_version:
            continue
        try:
            old_parsed = Version(old_version)
            new_parsed = Version(new_version)
        except InvalidVersion as exc:
            raise AssertionError(
                f"Cannot compare code versions for {metadata_path}: "
                f"{old_version!r} and {new_version!r}"
            ) from exc
        assert new_parsed >= old_parsed, (
            f"Code version downgrade for {metadata_path}: "
            f"{old_version!r} -> {new_version!r}"
        )


def check_openmc_archive(root, archive):
    for library in root.glob("_openmc_-_*"):
        if not library.is_dir():
            continue
        for benchmark in library.iterdir():
            if not benchmark.is_dir():
                continue
            metadata_file = benchmark / "metadata.json"
            with metadata_file.open(encoding="utf-8") as infile:
                metadata = json.load(infile)
            version = metadata["code_version"]
            assert (
                isinstance(version, str)
                and version.strip() == version
                and version not in ("", ".", "..")
            ), (
                f"Invalid code_version in {metadata_file}: {version!r}"
            )
            assert (
                Path(version).name == version and "/" not in version and "\\" not in version
            ), (
                f"Invalid code_version in {metadata_file}: {version!r}"
            )
            archived_metadata = (
                archive / version / benchmark.relative_to(root) / "metadata.json"
            )
            assert archived_metadata.is_file(), (
                f"Missing archived metadata: {archived_metadata}"
            )
            with archived_metadata.open(encoding="utf-8") as infile:
                archived_data = json.load(infile)
            assert archived_data == metadata, (
                f"Archived metadata differs from ROOT: {archived_metadata}"
            )


def test_overwritten_versions():
    check_overwritten_versions(REPOSITORY, os.environ.get("RESULTS_BASE_REF", "HEAD"))


def test_openmc_results_are_archived():
    check_openmc_archive(ROOT, ARCHIVE)

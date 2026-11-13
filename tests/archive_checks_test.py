import json

import pytest

from tests import consitency_across_csvs_test as csv_checks
from tests import metadata_test as metadata_checks


@pytest.fixture
def archive(tmp_path):
    version = tmp_path / "0.15.3"
    benchmark = version / "_openmc_-_FENDL 3.2c_" / "BenchA"
    benchmark.mkdir(parents=True)
    metadata = {
        "jade_version": "4.1",
        "code_version": "0.15.3",
        "library": "FENDL 3.2c",
        "benchmark_name": "BenchA",
        "benchmark_version": "1.0",
        "code": "openmc",
        "jade_run_version": "4.1",
    }
    (benchmark / "metadata.json").write_text(json.dumps(metadata), encoding="utf-8")
    (benchmark / "result.csv").write_text("bin,value\n1,1\n", encoding="utf-8")
    return version, benchmark, metadata


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("code_version", "0.15.2", "version mismatch"),
        ("code", "mcnp", "Not OpenMC"),
        ("jade_version", "", "Invalid jade_version"),
    ],
)
def test_archive_rejects_invalid_metadata(archive, field, value, message):
    version, benchmark, metadata = archive
    metadata[field] = value
    (benchmark / "metadata.json").write_text(json.dumps(metadata), encoding="utf-8")
    with pytest.raises(AssertionError, match=message):
        metadata_checks.check_archive_metadata(version)


def test_archive_requires_metadata_for_csv(archive):
    version, benchmark, _ = archive
    other = benchmark / "nested"
    other.mkdir()
    (other / "result.csv").write_text("bin,value\n1,1\n", encoding="utf-8")
    with pytest.raises(AssertionError, match="Missing metadata"):
        metadata_checks.check_archive_metadata(version)


def test_archive_requires_metadata_for_empty_benchmark(archive):
    version, benchmark, _ = archive
    (benchmark.parent / "BenchB").mkdir()
    with pytest.raises(AssertionError, match="Missing metadata"):
        metadata_checks.check_archive_metadata(version)


def test_archive_requires_documented_metadata_fields(archive):
    version, benchmark, metadata = archive
    del metadata["jade_run_version"]
    (benchmark / "metadata.json").write_text(json.dumps(metadata), encoding="utf-8")
    with pytest.raises(AssertionError, match="jade_run_version"):
        metadata_checks.check_archive_metadata(version)


def test_archived_benchmark_versions_are_scoped_per_snapshot(archive, tmp_path):
    version, benchmark, metadata = archive
    other = tmp_path / "0.16.0" / benchmark.parent.name / benchmark.name
    other.mkdir(parents=True)
    metadata["benchmark_version"] = "2.0"
    (other / "metadata.json").write_text(json.dumps(metadata), encoding="utf-8")
    metadata_checks.TestMetadata().test_same_benchmark_version(version)
    metadata_checks.TestMetadata().test_same_benchmark_version(other.parents[1])
    with pytest.raises(AssertionError, match="Different major benchmark versions"):
        metadata_checks.TestMetadata().test_same_benchmark_version(tmp_path)


def test_archive_csv_checks_use_matching_experimental_data(archive, tmp_path, monkeypatch):
    version, benchmark, _ = archive
    root = tmp_path / "ROOT"
    experiment = root / "_exp_-_exp_" / "BenchA"
    experiment.mkdir(parents=True)
    (experiment / "result.csv").write_text("bin,value\n1,1\n", encoding="utf-8")
    other_experiment = root / "_exp_-_exp_" / "BenchB"
    other_experiment.mkdir()
    (other_experiment / "result.csv").write_text("bin,value\n1,1\n", encoding="utf-8")
    monkeypatch.setattr(csv_checks, "ROOT", root)
    checks = csv_checks.TestCSVConsistency()
    checks.test_availability_csv(version)
    checks.test_same_length(version)

    (benchmark / "result.csv").write_text("bin,value\n1,1\n2,2\n", encoding="utf-8")
    with pytest.raises(AssertionError, match="differs from experimental"):
        checks.test_same_length(version)

    (experiment / "missing.csv").write_text("bin,value\n1,1\n", encoding="utf-8")
    with pytest.raises(AssertionError):
        checks.test_availability_csv(version)


def test_archive_csv_lengths_are_compared_across_libraries(archive, tmp_path, monkeypatch):
    version, benchmark, metadata = archive
    root = tmp_path / "ROOT"
    experiment = root / "_exp_-_exp_" / "BenchA"
    experiment.mkdir(parents=True)
    (experiment / "result.csv").write_text("bin,value\n1,1\n", encoding="utf-8")
    (benchmark / "extra.csv").write_text("bin,value\n1,1\n", encoding="utf-8")
    other = version / "_openmc_-_ENDFB-VIII.0_" / "BenchA"
    other.mkdir(parents=True)
    (other / "metadata.json").write_text(json.dumps(metadata), encoding="utf-8")
    (other / "result.csv").write_text("bin,value\n1,1\n", encoding="utf-8")
    (other / "extra.csv").write_text("bin,value\n1,1\n2,2\n", encoding="utf-8")
    monkeypatch.setattr(csv_checks, "ROOT", root)
    with pytest.raises(AssertionError):
        csv_checks.TestCSVConsistency().test_same_length(version)


def test_archive_csv_checks_match_benchmark_directory_exactly(archive, tmp_path, monkeypatch):
    version, _, _ = archive
    root = tmp_path / "ROOT"
    experiment = root / "_exp_-_exp_" / "Bench"
    experiment.mkdir(parents=True)
    (experiment / "different.csv").write_text("bin,value\n1,1\n", encoding="utf-8")
    monkeypatch.setattr(csv_checks, "ROOT", root)
    csv_checks.TestCSVConsistency().test_availability_csv(version)

import json
import os

import pandas as pd

LIB_NAMES = [
    "FENDL 2.1c",
    "FENDL 3.0",
    "FENDL 3.1d",
    "FENDL 3.2b",
    "FENDL 3.2c",
    "ENDFB VII.0",
    "ENDFB VIII.0",
    "IRDFF II",
    "JEFF 3.3",
    "D1SUNED (FENDL 3.2b+TENDL2017)",
    "D1SUNED (FENDL 3.1d+EAF2007)",
]

ALLOWED_KEYWORDS = [
    "jade_version",
    "code_version",
    "library",
    "benchmark_name",
    "benchmark_version",
    "code",
    "jade_run_version",
    "transport_lib",
]


class TestMetadata:
    def test_metadata_keys(self, result_root):
        """This test checks if all the metadata.json files across the different
        libraries have valid keys.
        """
        allfiles = []
        paths = []
        for path, _, files in os.walk(result_root):
            if "metadata.json" in files:
                with open(
                    os.path.join(path, "metadata.json"), "r", encoding="utf-8"
                ) as infile:
                    data = json.load(infile)
                    allfiles.append(data)
                    paths.append(path)

        df = pd.DataFrame(allfiles)
        for key in df.columns:
            assert key in ALLOWED_KEYWORDS

    def test_metadata_coherence(self, result_root):
        """This test checks the coherence of the metadata.json files.
        It ensures that the library, benchmark name and code match the
        ones specified in the folder structure.
        """
        for path, _, files in os.walk(result_root):
            if "metadata.json" in files:
                pieces = path.split(os.sep)
                if (
                    pieces[-2].split("-")[1].replace("_", "") == "JEFF"
                    or pieces[-2].split("-")[1].replace("_", "") == "ENDFB"
                ):
                    lib = (
                        pieces[-2].split("-")[1] + "-" + pieces[-2].split("-")[2]
                    ).replace("_", "")
                else:
                    lib = pieces[-2].split("-")[1].replace("_", "")
                benchmark = pieces[-1]
                code = pieces[-2].split("-")[0].replace("_", "")
                with open(
                    os.path.join(path, "metadata.json"), "r", encoding="utf-8"
                ) as infile:
                    metadata = json.load(infile)
                try:
                    assert metadata["library"] == lib
                    assert metadata["benchmark_name"] == benchmark
                    assert metadata["code"] == code
                except AssertionError as e:
                    print(lib, benchmark, code)
                    raise e

    def test_same_benchmark_version(self, result_root):
        """This test checks if all the metadata.json files across the different
        libraries have the same benchmark version for the same benchmark.
        """
        allfiles = []
        paths = []
        for path, _, files in os.walk(result_root):
            if "metadata.json" in files:
                with open(
                    os.path.join(path, "metadata.json"), "r", encoding="utf-8"
                ) as infile:
                    data = json.load(infile)
                    allfiles.append(data)
                    paths.append(path)

        df = pd.DataFrame(allfiles)
        benchmarks = df["benchmark_name"].unique()
        codes = df["code"].unique()
        for benchmark in benchmarks:
            for code in codes:
                versions = df[
                    (df["benchmark_name"] == benchmark) & (df["code"] == code)
                ]
                if len(versions) == 0:
                    continue  # code not available for this benchmark, skip

                version_numbers = versions["benchmark_version"].unique()
                # important differences are only if major version
                major_versions = [v.split(".")[0] for v in version_numbers]
                if len(set(major_versions)) > 1:
                    print(versions[["benchmark_version", "library"]])
                    raise AssertionError(
                        f"Different major benchmark versions for {benchmark} and {code}"
                    )


def check_archive_metadata(version_dir):
    required_keys = set(ALLOWED_KEYWORDS) - {"transport_lib"}
    metadata_files = list(version_dir.rglob("metadata.json"))
    assert metadata_files, f"No metadata found in {version_dir}"

    for library in version_dir.iterdir():
        if library.is_dir():
            for benchmark in library.iterdir():
                if benchmark.is_dir():
                    assert (benchmark / "metadata.json").is_file(), (
                        f"Missing metadata for {benchmark}"
                    )

    for csv in version_dir.rglob("*.csv"):
        assert (csv.parent / "metadata.json").is_file(), f"Missing metadata for {csv}"

    for metadata_file in metadata_files:
        relative = metadata_file.relative_to(version_dir)
        assert len(relative.parts) == 3, f"Unexpected metadata location: {metadata_file}"
        with metadata_file.open(encoding="utf-8") as infile:
            metadata = json.load(infile)
        missing = required_keys - metadata.keys()
        assert not missing, f"Missing metadata keys in {metadata_file}: {sorted(missing)}"
        for key in required_keys:
            value = metadata[key]
            assert isinstance(value, str) and value.strip(), (
                f"Invalid {key} in {metadata_file}: {value!r}"
            )
        assert metadata["code"] == "openmc", f"Not OpenMC metadata: {metadata_file}"
        assert metadata["code_version"] == version_dir.name, (
            f"OpenMC version mismatch in {metadata_file}: "
            f"{metadata['code_version']!r} != {version_dir.name!r}"
        )


def test_archive_metadata(archive_version):
    check_archive_metadata(archive_version)

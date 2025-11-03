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
    root = os.path.abspath(__file__)
    root = os.path.join(os.path.dirname(os.path.dirname(root)), "ROOT")

    def test_metadata_keys(self):
        """This test checks if all the metadata.json files across the different
        libraries have valid keys.
        """
        allfiles = []
        paths = []
        for path, _, files in os.walk(self.root):
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

    def test_metadata_coherence(self):
        """This test checks the coherence of the metadata.json files.
        It ensures that the library, benchmark name and code match the
        ones specified in the folder structure.
        """
        for path, _, files in os.walk(self.root):
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

                # Check the transport lib in an activation calculation
                try:
                    transport_lib = metadata["transport_lib"]
                    assert transport_lib in LIB_NAMES
                except KeyError:
                    if metadata["code"] == "d1s":
                        # for d1s it is mandatory
                        print("transport_lib is missing for d1s")
                        assert False

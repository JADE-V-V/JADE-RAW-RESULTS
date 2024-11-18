import os
import pandas as pd
import json


LIB_NAMES = {
    "21c": "FENDL 2.1c",
    "30c": "FENDL 3.0",
    "31c": "FENDL 3.1d",
    "32c": "FENDL 3.2b",
    "32d": "FENDL 3.2c",
    "70c": "ENDFB VII.0",
    "00c": "ENDFB VIII.0",
    "34y": "IRDFF II",
    "03c": "JEFF 3.3",
    "93c": "D1SUNED (FENDL 3.2b+TENDL2017)",
    "99c": "D1SUNED (FENDL 3.1d+EAF2007)",
    "exp": "experiment",
}

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

        allfiles = []
        for path, _, files in os.walk(self.root):
            if os.path.basename(path) == "Raw_Data":
                for file in files:
                    if file.endswith(".json"):
                        with open(
                            os.path.join(path, file), "r", encoding="utf-8"
                        ) as infile:
                            data = json.load(infile)
                            allfiles.append(data)

        df = pd.DataFrame(allfiles)
        for key in df.columns:
            assert key in ALLOWED_KEYWORDS

    def test_metadata_coherence(self):
        for path, _, _ in os.walk(self.root):
            if os.path.basename(path) == "Raw_Data":
                pieces = path.split(os.sep)
                lib = pieces[-4]
                benchmark = pieces[-3]
                code = pieces[-2]
                if lib != "exp":
                    with open(
                        os.path.join(path, "metadata.json"), "r", encoding="utf-8"
                    ) as infile:
                        metadata = json.load(infile)
                    try:
                        assert metadata["library"] == LIB_NAMES[lib]
                        assert metadata["benchmark_name"] == benchmark
                        assert metadata["code"] == code
                    except AssertionError as e:
                        print(lib, benchmark, code)
                        raise e

                    # Check the transport lib in an activation calculation
                    try:
                        transport_lib = metadata["transport_lib"]
                        assert transport_lib in LIB_NAMES.values()
                    except KeyError:
                        if metadata["code"] == "d1s":
                            # for d1s it is mandatory
                            print("transport_lib is missing for d1s")
                            assert False

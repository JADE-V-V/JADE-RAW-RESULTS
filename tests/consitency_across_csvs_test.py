import os
import warnings

import pandas as pd


class TestCSVConsistency:
    root = os.path.abspath(__file__)
    root = os.path.join(os.path.dirname(os.path.dirname(root)), "ROOT")

    def test_availability_csv(self):
        """This test checks if all the csvs that are available in the experiment
        are also in the libraries results.
        """
        exp_path = os.path.join(self.root, "_exp_-_exp_")
        for bench_name in os.listdir(exp_path):
            # Get all the csvs available in the experiment folder
            available_csvs = os.listdir(os.path.join(exp_path, bench_name))
            # Define a bool variable to ensure that all experimental benchmarks have some computational results
            flag_comp = False
            # Check if they are also in the libraries results
            for dirpath, dirnames, filenames in os.walk(self.root):
                if bench_name in dirpath:
                    for name in available_csvs:
                        try:
                            assert name in filenames
                        except AssertionError as e:
                            print(set(available_csvs) - set(filenames))
                            print(name, dirpath)
                            raise e
                    # If at least one library is found for the benchmark, set flag_comp to True
                    flag_comp = True
            if not flag_comp:
                raise ValueError(
                    f"The experimental benchmark {bench_name} has no computational results."
                )

    def test_same_length(self):
        """This test checks if all the csvs across the different libraries (including
        experimental data) have the same length.
        """
        all_benchmarks = []
        # Get all the benchmarks available
        for dirpath, dirnames, filenames in os.walk(self.root):
            if "d1s" not in dirpath and "metadata.json" in filenames:
                bench_name = os.path.basename(dirpath)
                # Exclude benchmarks which have coarse binning tallies and other which
                # we are already aware of inconsistencies(which are fixed by selecting
                # subsets in the web-app, as fixing it otherwise would require to re-run
                # the simulations or adding 0 to the experimental data)
                if (
                    bench_name
                    not in [
                        "Sphere",
                        "FNG-BKT",
                        "FNG-HCPB",
                        "FNG-W",
                        "IPPE-DT",
                        "Oktavian",
                        "RCR-Sphere",
                        "RCR-SS",
                        "Tiara-BC",
                        "Tiara-FC",
                    ]
                    and bench_name not in all_benchmarks
                ):
                    all_benchmarks.append(bench_name)

        for benchmark in all_benchmarks:
            flag_ref = False
            for dirpath, dirnames, filenames in os.walk(self.root):
                if benchmark in dirpath:
                    if flag_ref:
                        # Compare the length of the csvs with the reference
                        for name in filenames:
                            if name.endswith(".csv"):
                                try:
                                    df = pd.read_csv(os.path.join(dirpath, name))
                                    df = (
                                        df.set_index(df.columns[0])
                                        .drop("total", errors="ignore")
                                        .reset_index()
                                    )
                                    if name in csvs_reference:
                                        assert len(csvs_reference[name]) == len(df)
                                    else:
                                        warnings.warn(
                                            f"The csv file {name} is not present in all libraries for the benchmark {benchmark}."
                                        )
                                except AssertionError as e:
                                    print(name, dirpath)
                                    raise e
                    else:
                        # If it is the first library found, set the contents of the corresponding folder as a reference
                        flag_ref = True
                        csvs_reference = {}
                        for name in filenames:
                            if name.endswith(".csv"):
                                df = pd.read_csv(os.path.join(dirpath, name))
                                df = (
                                    df.set_index(df.columns[0])
                                    .drop("total", errors="ignore")
                                    .reset_index()
                                )
                                csvs_reference[name] = df

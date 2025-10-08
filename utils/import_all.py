"""This script can be used to import all the results contained in a JADE
installation.

user parameters are divided into optional and mandatory and are described
through comments. For experimental data, multiple processing can be done of the
same libraries. In this case, the script will only copy the newest data checking
the folder date of creation.
"""

import json
import os
import shutil

# --- Mandatory user parameters ---
# Source folder where the results are stored
SRC = r"R:\AC_ResultsDB\Jade\06_JADEv4\raw_data"
# Destination folder where the results will be copied
ROOT_DEST = "ROOT"
# if true the files are not copied but a preview of the missing results is printed
ONLY_SCREEN = False

# --- Optional user parameters ---
# exclude some libraries from the import. This libraries will be ignored
EXCLUDE_LIBRARIES = []  # e.g. ["_mcnp_-_FENDL 3.2c_", "_openmc_-_JEFF-3.3_"]
# This is used if an automatic metadata file needs to be added.

# This is used if an automatic metadata file needs to be added.
BASE_METADATA = {
    "jade_version": "4.3.0",
    "code_version": None,
    "benchmark_version": "1.0",
    "jade_run_version": "4.3.0",
}


def result_available(code_lib: str, benchmark: str) -> bool:
    """Check if the results are already present in ROOT

    Parameters
    ----------
    code_lib : str
        "_code_-_library_" combination
    benchmark : str
        benchmark name

    Returns
    -------
    bool
        True if the raw data folder is already present, False otherwise
    """
    path = os.path.join(ROOT_DEST, code_lib, benchmark)
    if os.path.exists(path):
        # If it is empty remove it
        if len(os.listdir(path)) == 0:
            shutil.rmtree(path)
            return False
        # if it is not empty return true
        return True
    else:
        # if it does not exist return false
        return False


def copy_results(src: str, code_lib: str, benchmark: str, metadata: dict = None):
    """Copy the results from the source to the destination.

    Parameters
    ----------
    src : str
        folder to be copied
    code_lib : str
        "_code_-_library_" combination
    benchmark : str
        benchmark name
    metadata : dict, optional
        if None, a metadata file will be added to the newly copied files, by default None
        if not None, the metadata file present in the source folder will be copied
    """
    dest = os.path.join(ROOT_DEST, code_lib, benchmark)
    shutil.copytree(src, dest)
    if metadata is None and code_lib != "_exp_-_exp_":
        # Perform your action here
        new_dict = {}
        new_dict["benchmark_version"] = BASE_METADATA["benchmark_version"]
        new_dict["jade_run_version"] = BASE_METADATA["jade_run_version"]
        new_dict["benchmark_name"] = benchmark
        if code_lib.split("-")[1] == "_ENDFB" or code_lib.split("-")[1] == "_JEFF":
            new_dict["library"] = (
                code_lib.split("-")[1].replace("_", "")
                + "-"
                + code_lib.split("-")[2].replace("_", "")
            )
        else:
            new_dict["library"] = code_lib.split("-")[1].replace("_", "")
        new_dict["code"] = code_lib.split("-")[0].replace("_", "")
        new_dict["jade_version"] = BASE_METADATA["jade_version"]
        new_dict["code_version"] = BASE_METADATA["code_version"]
        with open(os.path.join(dest, "metadata.json"), "w", encoding="utf-8") as f:
            json.dump(new_dict, f, indent=4)


def main() -> None:
    """Main function to import all the results from the source to the destination"""
    print("Importing computational results...")
    # First deal with computational benchmarks
    for code_lib in os.listdir(SRC):
        # skip libraries that should be ignored
        if code_lib in EXCLUDE_LIBRARIES:
            continue
        code_lib_path = os.path.join(SRC, code_lib)
        for benchmark in os.listdir(code_lib_path):
            bench_path = os.path.join(code_lib_path, benchmark)
            available = result_available(code_lib, benchmark)
            try:
                with open(
                    os.path.join(bench_path, "metadata.json"), encoding="utf-8"
                ) as f:
                    metadata = json.load(f)
            except FileNotFoundError:
                metadata = None
            if not available:
                # Print the missing results
                if ONLY_SCREEN:
                    print(
                        f"Missing results for {code_lib} {benchmark}. Since ONLY_SCREEN is set to True, no files will be imported."
                    )
                # copy the missing results
                else:
                    print(f"{code_lib} {benchmark}")
                    copy_results(
                        bench_path,
                        code_lib,
                        benchmark,
                        metadata,
                    )


if __name__ == "__main__":
    main()
    print("Import completed")

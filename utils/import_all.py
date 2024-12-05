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

from import_fng_sic import import_sic
from import_tiara_bs import import_bs
from import_tiara_fc import import_fc

# --- Mandatory user parameters ---
# Source folder where the results are stored
SRC = r"R:\AC_ResultsDB\Jade\04_JADE_latest_root\Tests\Post-Processing"
# Destination folder where the results will be copied
ROOT_DEST = "ROOT"
# if true the files are not copied but a preview of the missing results is printed
ONLY_SCREEN = False

# --- Optional user parameters ---
# exclude some libraries from the import. This libraries will be ignored
EXCLUDE_LIBRARIES = []  # e.g. ["33c", "99c", "40c"]
# This is used if an automatic metadata file needs to be added.
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
    "99c": "D1SUNED (FENDL 3.1d+EAF2007)",
    "93c": "D1SUNED (FENDL 3.2b+TENDL2017)",
    "exp": "experiment",
}
# This is used if an automatic metadata file needs to be added.
BASE_METADATA = {
    "jade_version": "3.0.1",
    "code": "MCNP",  # This will be replaced by the code name found in folder
    "code_version": "6.2",
    "library": "ENDF",  # This will be replaced by the lib name found in folder
    "benchmark_name": "JEFF 3.3",  # This will be replaced by the lib name found in folder
    "benchmark_version": "1.0",
    "jade_run_version": "2.0.0",
}


def result_available(lib: str, benchmark: str, code: str) -> bool:
    """Check if the results are already present in ROOT

    Parameters
    ----------
    lib : str
        library suffix
    benchmark : str
        benchmark name
    code : str
        code name

    Returns
    -------
    bool
        True if the raw data folder is already present, False otherwise
    """
    path = os.path.join(ROOT_DEST, lib, benchmark, code, "Raw_Data")
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


def sorted_listdir(directory) -> list[str]:
    """List the directory content sorted by creation time

    Parameters
    ----------
    directory : os.PathLike
        Path to the directory

    Returns
    -------
    list[str]
        List of items in the directory sorted by creation time
    """

    def get_creation_time(item):
        item_path = os.path.join(directory, item)
        return os.path.getctime(item_path)

    items = os.listdir(directory)
    sorted_items = sorted(items, key=get_creation_time, reverse=True)
    return sorted_items


def copy_results(
    src: os.PathLike, lib: str, benchmark: str, code: str, metadata: dict = None
):
    """Copy the results from the source to the destination. This accounts for
    specific benchmarks needs like in Tiara case.

    Parameters
    ----------
    src : os.PathLike
        folder to be copied
    lib : str
        library suffix
    benchmark : str
        benchmark name
    code : str
        code name
    metadata : dict, optional
        if not None, a metadata file will be added to the newly copied files, by default None
    """
    dest = os.path.join(ROOT_DEST, lib, benchmark, code, "Raw_Data")
    if benchmark == "Tiara-BS":
        if not os.path.exists(dest):
            os.makedirs(dest)
        import_bs(src, dest)
    elif benchmark == "Tiara-FC":
        if not os.path.exists(dest):
            os.makedirs(dest)
        import_fc(src, dest)
    elif benchmark == "FNG-SiC":
        if not os.path.exists(dest):
            os.makedirs(dest)
        import_sic(src, dest)
    else:
        shutil.copytree(src, dest)
    if metadata is not None:
        # Perform your action here
        new_dict = metadata.copy()
        new_dict["code"] = code
        new_dict["benchmark_name"] = benchmark
        new_dict["library"] = LIB_NAMES[lib]
        with open(os.path.join(dest, "metadata.json"), "w", encoding="utf-8") as f:
            json.dump(new_dict, f)


def main() -> None:
    """Main function to import all the results from the source to the destination"""
    print("Importing computational results...")
    # First deal with computational benchmarks
    comp_path = os.path.join(SRC, "Single_Libraries")
    for lib in os.listdir(comp_path):
        # skip libraries that should be ignored
        if lib in EXCLUDE_LIBRARIES:
            continue
        lib_path = os.path.join(comp_path, lib)
        for benchmark in os.listdir(lib_path):
            bench_path = os.path.join(lib_path, benchmark)
            for code in os.listdir(bench_path):
                raw_data_folder = os.path.join(bench_path, code, "Raw_Data")
                available = result_available(lib, benchmark, code)
                if not available:
                    # Print the missing results
                    if ONLY_SCREEN:
                        print(f"{lib} {benchmark} {code}")
                    # copy the missing results
                    else:
                        print(f"{lib} {benchmark} {code}")
                        copy_results(
                            raw_data_folder,
                            lib,
                            benchmark,
                            code,
                            metadata=BASE_METADATA,
                        )

    # Then deal with experimental benchmarks

    # get the list of folders by creation date. In this way the folder will be
    # copied the first time it is found (newer) and if repeated in older assessments
    # it will be ignored as it is already present
    print("Importing experimental results...")
    already_printed = []
    exp_path = os.path.join(SRC, "Comparisons")
    for comparison_folder in sorted_listdir(exp_path):
        # Only interesterd in experimental benchmarks here
        if comparison_folder[:3] != "Exp":
            continue
        comparison_path = os.path.join(exp_path, comparison_folder)
        for benchmark in os.listdir(comparison_path):
            bench_path = os.path.join(comparison_path, benchmark)
            for code in os.listdir(bench_path):
                raw_data_folder = os.path.join(bench_path, code, "Raw_Data")
                for lib in os.listdir(raw_data_folder):
                    if lib in EXCLUDE_LIBRARIES:
                        continue
                    available = result_available(lib, benchmark, code)
                    if not available:
                        # Print the missing results
                        if ONLY_SCREEN:
                            stringa = f"{lib} {benchmark} {code}"
                            if stringa not in already_printed:
                                already_printed.append(stringa)
                                print(stringa)
                        # copy the missing results
                        else:
                            print(f"{lib} {benchmark} {code}")
                            copy_results(
                                os.path.join(raw_data_folder, lib),
                                lib,
                                benchmark,
                                code,
                                metadata=BASE_METADATA,
                            )


if __name__ == "__main__":
    main()
    print("Import completed")

"""Import the Tiara-BS benchmark from JADE results to the WebbApp format.

The Tiara-BS benchmark in JADE has a .csv raw data structure that is not 
directly compatible with the WebbApp. The following scritp needs to be run to
import JADE's raw data into the WebbApp format. Do not forget to manually add
or copy the metadata.json file associated to the raw data that is being imported.

SOURCE: path to the JADE raw data .csv files.
DEST: path to the destination folder in the JADE RAW RESULTS repository.
"""

import os
import pandas as pd

# In Tiara BS, of each csv, only the total is needed. Hence, we need to re-compact them into a single csv for the plot
SOURCE = r"R:\AC_ResultsDB\Jade\04_JADE_latest_root\Tests\Post-Processing\Comparisons\Exp_Vs_33c_Vs_32c\Tiara-BS\mcnp\Raw_Data\32c"
DEST = (
    r"D:\DATA\laghida\Documents\GitHub\JADE-RAW-RESULTS\ROOT\32c\Tiara-BS\mcnp\Raw_Data"
)


def import_bs(source: os.PathLike, dest: os.PathLike) -> None:
    """Import the Tiara-BS benchmark from JADE results to the WebbApp format.

    Parameters
    ----------
    source : os.PathLike
        original path to the JADE raw data .csv files.
    dest : os.PathLike
        destination path to the WebbApp format.
    """
    # dictionary for .csv
    tallies = {"14": "Bare", "24": "15 mm", "34": "30 mm", "44": "50 mm", "54": "90 mm"}
    thicknesses = {
        "cc": {"43": ["25-40", "50-40", "100-00", "150-00"], "68": ["50-00", "100-00"]},
        "fe": {"43": ["20-00", "40-00", "100-00"], "68": ["20-00", "40-00", "100-00"]},
    }
    for material in ["cc", "fe"]:
        for energy in ["43", "68"]:
            for thickness in thicknesses[material][energy]:
                rows = []
                for tally in ["14", "24", "34", "44", "54"]:
                    file = f"{material}-{energy}-{thickness} {tally}.csv"
                    df = pd.read_csv(os.path.join(source, file))
                    df["Cells"] = tallies[tally]
                    df = df.iloc[-1]
                    rows.append(df)
                df = pd.concat(rows, axis=1).T
                simp_thick = thickness.split("-")[0]
                outfile = os.path.join(dest, f"{material}-{energy}-{simp_thick}.csv")
                df.to_csv(outfile, index=False)


if __name__ == "__main__":
    import_bs(SOURCE, DEST)

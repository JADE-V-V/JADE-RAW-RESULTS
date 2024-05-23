"""Import the Tiara-FC benchmark from JADE results to the WebbApp format.

The Tiara-FC benchmark in JADE has a .csv raw data structure that is not 
directly compatible with the WebbApp. The following scritp needs to be run to
import JADE's raw data into the WebbApp format. Do not forget to manually add
or copy the metadata.json file associated to the raw data that is being imported.

SOURCE: path to the JADE raw data .csv files.
DEST: path to the destination folder in the JADE RAW RESULTS repository.
"""

import os
import pandas as pd

# In Tiara BS, of each csv, only the total is needed. Hence, we need to re-compact them into a single csv for the plot
SOURCE = r"R:\AC_ResultsDB\Jade\04_JADE_latest_root\Tests\Post-Processing\Comparisons\Exp_Vs_33c_Vs_32c\Tiara-FC\mcnp\Raw_Data\32c"
DEST = (
    r"D:\DATA\laghida\Documents\GitHub\JADE-RAW-RESULTS\ROOT\32c\Tiara-FC\mcnp\Raw_Data"
)


def import_fc(source: os.PathLike, dest: os.PathLike):
    """Import the Tiara-FC benchmark from JADE results to the WebbApp format.

    Parameters
    ----------
    source : os.PathLike
        original path to the JADE raw data .csv files.
    dest : os.PathLike
        destination path to the WebbApp format.
    """
    # dictionary for .csv
    tallies = {
        "14": {"mat": "U238", "offset": "00"},
        "24": {"mat": "Th232", "offset": "00"},
        "34": {"mat": "U238", "offset": "20"},
        "44": {"mat": "Th232", "offset": "20"},
    }
    thicknesses = {
        "cc": {
            "43": {"20": ["25", "50", "100"], "00": ["25", "50", "100"]},
            "68": {"20": ["25", "50", "100", "150"], "00": ["25", "50", "100", "150"]},
        },
        "fe": {
            "43": {
                "20": ["00", "10", "20", "40", "70"],
                "00": ["00", "10", "20", "40", "70"],
            },
            "68": {
                "20": ["20", "40", "70", "100", "130"],
                "00": ["00", "20", "40", "70", "100"],
            },
        },
    }

    for material in ["cc", "fe"]:
        for energy in ["43", "68"]:
            for tally in ["14", "24", "34", "44"]:
                offset = tallies[tally]["offset"]
                detector = tallies[tally]["mat"]
                rows = []
                for thickness in thicknesses[material][energy][offset]:
                    file = f"{material}-{energy}-{thickness}-00 {tally}.csv"
                    try:
                        df = pd.read_csv(os.path.join(source, file))
                    except FileNotFoundError as e:
                        if file in ["fe-43-00-00 44.csv", "fe-43-10-00 44.csv"]:
                            continue
                        else:
                            raise e
                    df["Cells"] = thickness
                    df = df.iloc[-1]
                    rows.append(df)
                df = pd.concat(rows, axis=1).T
                outfile = os.path.join(
                    dest, f"{material}-{energy}-{detector}-{offset}.csv"
                )
                df.to_csv(outfile, index=False)


if __name__ == "__main__":
    import_fc(SOURCE, DEST)

"""Import the FNG-SiC benchmark from JADE results to the WebbApp format.

The data from the TLD measurement files in the FNG-SiC benchmark is missing a
normalization factor and some other corrections. The following script imports JADE's raw
data into the WebbApp format and applied this missing normalization and correction factors.

SOURCE: path to the JADE raw data .csv files.
DEST: path to the destination folder in the JADE RAW RESULTS repository.
"""

import os

import pandas as pd

# In FNG SiC, of each csv, only the total is needed. Hence, we need to re-compact them into a single csv for the plot
SOURCE = r"R:\AC_ResultsDB\Jade\05_JADE_alex_bmarks\JADE-bmark_addition_1\Tests\Post-Processing\Comparisons\Exp_Vs_43c_Vs_42c_Vs_03c_Vs_32c_Vs_00c\FNG-SiC\mcnp\Raw_Data\00c"
DEST = (
    r"D:\DATA\campmar\Documents\GitHub\JADE-RAW-RESULTS\ROOT\00c\FNG-SiC\mcnp\Raw_Data"
)

# FNG SiC specific corrections/normalisations
fngsic_k = [0.212, 0.204, 0.202, 0.202]  # Neutron sensitivity of TL detectors
fngsic_norm = 1.602e-13 * 1000  # J/MeV * g/kg


def import_sic(source: os.PathLike, dest: os.PathLike) -> None:
    """Import the FNG-SiC benchmark from JADE results to the WebbApp format.

    Parameters
    ----------
    source : os.PathLike
        original path to the JADE raw data .csv files.
    dest : os.PathLike
        destination path to the WebbApp format.
    """

    for detector in ["TLD", "Al", "Au", "Nb", "Ni"]:
        if detector == "TLD":
            values = {}
            errors = {}
            for tally in ["16", "26"]:
                file = f"{detector} {tally}.csv"
                df = pd.read_csv(os.path.join(source, file))
                errors[tally] = df["Error"].values
                if tally == "16":
                    values[tally] = [
                        df["Value"].values[i] * fngsic_norm * fngsic_k[i]
                        for i in range(len(df["Value"].values))
                    ]
                else:
                    values[tally] = [
                        df["Value"].values[i] * fngsic_norm
                        for i in range(len(df["Value"].values))
                    ]
            df["Value"] = [
                float("{:.5g}".format(values["16"][i] + values["26"][i]))
                for i in range(len(df["Value"].values))
            ]
            df["Error"] = [
                float(
                    "{:.5g}".format(
                        (
                            values["16"][i] * errors["16"][i]
                            + values["26"][i] * errors["26"][i]
                        )
                        / (values["16"][i] + values["26"][i])
                    )
                )
                for i in range(len(df["Value"].values))
            ]
            file = f"{detector} 6.csv"
            df.to_csv(os.path.join(dest, file), index=False)

        else:
            file = f"{detector} 4.csv"
            df = pd.read_csv(os.path.join(source, file))
            df.to_csv(os.path.join(dest, file), index=False)


if __name__ == "__main__":
    import_sic(SOURCE, DEST)

import os
from pathlib import Path
import pandas as pd


def test_error_relative():
    """test that all errors in exp_results are relative errors (i.e. less than 1)"""
    absolute_errors = []
    for folder in os.listdir("ROOT/_exp_-_exp_"):
        for file in os.listdir(Path("ROOT/_exp_-_exp_", folder)):
            file = Path("ROOT/_exp_-_exp_", folder, file)
            df = pd.read_csv(file)
            if df["Error"].max() > 1:
                absolute_errors.append(folder)
    absolute_errors = list(set(absolute_errors))
    assert len(absolute_errors) == 0, f"Folders with absolute errors: {absolute_errors}"

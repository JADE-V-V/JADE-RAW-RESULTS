import os
import pandas as pd

class TestCSVConsistency():
    root = os.path.abspath(__file__)
    root = os.path.join(os.path.dirname(os.path.dirname(root)), "ROOT")

    def test_availability_csv(self):
        """This test checks if all the csvs that are av available in the experiment
        are also in the libraries results.
        """
        exp_path = os.path.join(self.root, 'exp')
        for bench_name in os.listdir(exp_path):
            available_csvs = os.listdir(os.path.join(exp_path, bench_name, 'experiment', 'Raw_Data'))
            for dirpath, dirnames, filenames in os.walk(self.root):
                if 'Raw_Data' in dirpath and bench_name in dirpath:
                    for name in available_csvs:
                        try:
                            assert name in filenames
                        except AssertionError as e:
                            print(set(available_csvs) - set(filenames))
                            print(name, dirpath)
                            raise e

    def test_same_length(self):
        """This test checks if all the csvs across the different libraries (including
        experimental data) have the same length.
        """
        all_benchmarks = []
        for dirpath, dirnames, filenames in os.walk(self.root):
            if 'mcnp' in dirnames:
                bench_name = os.path.basename(dirpath)
                if bench_name not in ['Sphere', 'FNG-BKT']:
                    all_benchmarks.append(bench_name)
        
        for benchmark in all_benchmarks:
            flag_ref = False
            for dirpath, dirnames, filenames in os.walk(self.root):
                if benchmark in dirpath and 'Raw_Data' in dirpath:
                    if flag_ref:
                        for name in filenames:
                            if name.endswith('.csv'):
                                try:
                                    df = pd.read_csv(os.path.join(dirpath, name))
                                    df = df.set_index(df.columns[0]).drop("total", errors="ignore").reset_index()
                                    assert len(csvs_reference[name]) == len(df)
                                except AssertionError as e:
                                    print(name, dirpath)
                                    raise e
                    else:
                        flag_ref = True
                        csvs_reference = {}
                        for name in filenames:
                            if name.endswith('.csv'):
                                df = pd.read_csv(os.path.join(dirpath, name))
                                df = df.set_index(df.columns[0]).drop("total", errors="ignore").reset_index()
                                csvs_reference[name] = df
                    
               
                    

    
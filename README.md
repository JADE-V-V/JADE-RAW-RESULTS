[![Metadata-check](https://github.com/JADE-V-V/JADE-RAW-RESULTS/actions/workflows/metadata_check.yml/badge.svg?branch=main)](https://github.com/JADE-V-V/JADE-RAW-RESULTS/actions/workflows/metadata_check.yml)

# JADE-RAW-RESULTS
This repo hosts the raw data coming from the post-processing of JADE assessments.

## Uploading new results
For the vast majority of cases, adding data to this repository is pretty straightforward, the .csv files that are output by JADE in the
`Raw_Data` folders, can be directly copied in the corresponding folder in this repository structure, which looks like the following:
```
ROOT
  |-----<lib1>
  |       |-----<>
  |
  |-----<lib2>
          |-----<benchmark_name>
                      |-----------<mcnp>
                      |             |------<Raw_Data>
                      |                        |--------<raw_data1>.csv
                      |                        |--------<raw_data2>.csv
                      |                        |--------<...>
                      |                        |--------metadata.json
                      |
                      |-----------<openmc>
                      |-----------<...>
```

Some sanity checks are performed on the `metadata.json` keywords and values to ensure they are consistent with the allowed library names and with the folder structure they are inserted into (for more details check the [CI tests](./tests/metadata_test.py)).

If a large set of data needs to be added, copying by hand each folder can become a tedious operation. [import_all.py](./utils/import_all.py) can be used to automatically scan a JADE > v3.0.0 post-processing folder, identify which set of raw data are not currently available in the
database and add them to it.

> [!NOTE]  
> If a new library is added, remember to update the [import_all.py](./utils/import_all.py) and [metadata_test.py](./tests/metadata_test.py) files to provide the default name for the new library.

### Exceptions
#### Tiara-BS
The .csv raw data structure in this benchmark is not compatible with JADE results. To correctly import them into this repository use this [import_tiara_bs.py](./utils/import_tiara_bs.py). 

#### Tiara-FC
The .csv raw data structure in this benchmark is not compatible with JADE results. To correctly import them into this repository use this [import_tiara_fc.py](./utils/import_tiara_fc.py). 

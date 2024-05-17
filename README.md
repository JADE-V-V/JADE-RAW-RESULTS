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

### Exceptions
#### Tiara-BS
The .csv raw data structure in this benchmark is not compatible with JADE results. To correclty import them into this repository use this [script](./utils/import_tiara_bs.py). 

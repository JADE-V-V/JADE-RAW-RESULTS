import json
import os
import urllib.request

IAEA_OPEN_BENCHMARKS_API = (
    "https://api.github.com/repos/IAEA-NDS/open-benchmarks/contents/"
    "jade_open_benchmarks/exp_results"
)


def test_experimental_open():
    """Test that no experimental data for any IAEA open benchmark is present in this
    repository (it should be added to the IAEA open benchmarks repo instead)."""
    with urllib.request.urlopen(IAEA_OPEN_BENCHMARKS_API, timeout=10) as response:
        iaea_folders = {
            item["name"]
            for item in json.loads(response.read())
            if item["type"] == "dir"
        }
    conflicts = iaea_folders.intersection(os.listdir("ROOT/_exp_-_exp_"))
    assert not conflicts, (
        f"Experimental data for the following open benchmarks should not be added "
        f"to this repository: {sorted(conflicts)}"
    )

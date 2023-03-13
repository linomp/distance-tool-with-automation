import os

import pytest

from app import start_processing_loop


@pytest.mark.asyncio
async def test_processing_loop():
    if os.path.exists("data/test_output.csv"):
        os.remove("data/test_output.csv")
    if os.path.exists("data/test_input.txt"):
        os.remove("data/test_input.txt")

    with open("data/test_input.txt", "w") as f:
        f.write('\"Via Livorno 60, Torino (TO)\"' + '\t' + '\"Corso Umberto I, 29, 28838 Stresa VB\"' + '\n')
        f.write("Environment Park Torino" + "\t" + "Hotel Regina Palace Stresa" + "\n")

    await start_processing_loop(
        input_file="data/test_input.txt",
        input_delimiter="\t",
        output_file="data/test_output.csv",
        output_delimiter="\t"
    )
    with open("data/test_output.csv", "r") as f:
        lines = f.readlines()
        assert len(lines) >= 2
        for line in lines:
            assert len(line.split("\t")) == 3
            assert "ERROR" not in line
            last_element = line.split("\t")[-1].strip()
            if last_element != "driving_distance_km":
                assert last_element.isdigit()

    os.remove("data/test_output.csv")
    os.remove("data/test_input.txt")

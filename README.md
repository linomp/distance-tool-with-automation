# distance-tool-with-automation

## Installation

Pre-requisites:

- Python 3.10+
- pip 22.3+

```commandline
git clone https://github.com/linomp/distance-tool-with-automation.git
python -m venv venv
pip install -u pip
pip install -r requirements.txt
playwright install
```

## How to use:

1. Provide a .txt file and the delimiter used in the file. The file should contain two addresses per line (origin and
   destination), separated by
   the delimiter.

   Here is an example of tab-delimited input file (`<TAB>` added for readability, normally they are not visible in the
   file):

    ```json
    Via Livorno 60, Torino (TO)<TAB>Corso Umberto I, 29, 28838 Stresa VB
    Environment Park Torino<TAB>Hotel Regina Palace Stresa
    Via Livorno 60, Torino (TO)<TAB>Via Lincoln, 2, 90133 Palermo PA
    Environment Park Torino<TAB>Orto botanico Palermo
    Torino<TAB>Palermo
    ```

   _Note: from Excel you can export as tab-delimited .txt file_


2. Invoke the tool:
    ```bash
    python main.py -i input.txt -d "\t"
    ```

2. The tool will process the input file line-by-line, calculating the distance between the two addresses and writing the
   result in the output file, which will look like this:

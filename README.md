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

1. Create an input `.txt` file containing two addresses per line (origin and
   destination), separated by a delimiter (e.g. comma, tab, semicolon).

   Here is an example of tab-delimited input file (`<TAB>` added for readability, normally they are not visible in the
   file):

    ```text
    Via Livorno 60, Torino (TO)<TAB>Corso Umberto I, 29, 28838 Stresa VB
    Environment Park Torino<TAB>Hotel Regina Palace Stresa
    Via Livorno 60, Torino (TO)<TAB>Via Lincoln, 2, 90133 Palermo PA
    Environment Park Torino<TAB>Orto botanico Palermo
    Torino<TAB>Palermo
    ```

   _Note: from Excel you can export an .xlsx as a tab-delimited .txt file_



2. Invoke the tool:
    ```bash
    python main.py -i input.txt -d "\t"
    ```

2. The tool will process the input file line-by-line, calculating the distance between every pair of addresses and writing the
   result in the output file. The final result will look like this:
   
   ![output](https://user-images.githubusercontent.com/40581019/223180449-9546dba8-ce92-4505-a840-382b33e82a0c.png)
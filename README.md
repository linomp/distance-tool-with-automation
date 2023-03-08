# distance-tool-with-automation

[![CI](https://github.com/linomp/distance-tool-with-automation/actions/workflows/CI.yml/badge.svg)](https://github.com/linomp/distance-tool-with-automation/actions/workflows/CI.yml)

## Installation

Pre-requisites:

- Python 3.10+
- pip 22.3+

Run the following commands to clone the project, create a virtual environment and install the project dependencies:

   ```shell
   git clone https://github.com/linomp/distance-tool-with-automation.git
   cd distance-tool-with-automation
   
   # Windows
   python -m venv venv
   call venv\Scripts\activate.bat
   
   # MacOS/Linux
   python3 -m venv venv
   source ./venv/bin/activate
      
   pip install --upgrade pip
   pip install -r requirements.txt
   playwright install chromium
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
    # Windows
    python main.py -i data/input.txt -d "\t"
    
    # MacOS/Linux
    python3 main.py -i data/input.txt -d "\t"
    ```

2. The tool will process the input file line-by-line, calculating the distance between every pair of addresses and
   writing the
   result in the output file. The final result will look like this:

   ![output](https://user-images.githubusercontent.com/40581019/223180449-9546dba8-ce92-4505-a840-382b33e82a0c.png)

## Alternative

This [other version](https://github.com/linomp/distance-tool) gets the distances using the Google Maps Distance Matrix API. 

It offers a web-based UI and allows you to upload an excel file. However, it requires a Google Maps API key. The service is free up to [~40K requests per month](https://mapsplatform.google.com/pricing/) but after that Google will start charging you.

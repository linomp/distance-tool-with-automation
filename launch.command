#!/bin/bash
cd -- "$(dirname "$0")"
source ./venv/bin/activate && pip install -r requirements.txt && streamlit run app_ui.py

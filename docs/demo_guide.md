# Run milestone 1
1. Open the extracted `factoryguard` folder in PyCharm.
2. Select or create a Python 3.10+ virtual environment.
3. In the project terminal run `python -m pip install -e .`.
4. Open `run_step1.py` and run it, or use `python run_step1.py`.
5. Open the printed results folder: validation.json, summary.json and sensor_readings.png.
Every default run creates a fresh timestamped output directory.
Custom input: `python run_step1.py --input data/raw/your_readings.csv`.
Tests: `python -m unittest discover -s tests -v`.
No private PyCharm settings or machine-specific interpreter paths are included.
PyCharm will create its own .idea directory when you open the folder.

The real-data forecasting/local-dashboard prototype has separate [setup and runnable commands](forecast_demo.md). Use its already saved artifact to start a replay without fitting again. No extra Python dependency is needed. The synthetic milestone above remains independent; its injected trends have no verified industrial failure labels.

The latest bounded model-selection workflow and selected exponential-smoothing dashboard use [selection_demo.md](selection_demo.md). Install updated project dependencies (now including scikit-learn) through `python -m pip install -e .`. For the completed replay, save/open `reports/local/selection-v2/dashboard.html`; it needs no server or network connection.

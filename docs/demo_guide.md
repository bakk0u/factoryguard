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

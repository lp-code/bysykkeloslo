Bysykkel Oslo
==============================
![Bysykkel Oslo Project Logo](/docs/bike_gh2.jpg)

Analyse the trip data from the bicycle sharing scheme in Oslo and create a
machine-learning-based net demand predictor.


Prerequisites
-------------

The code has been developed under Windows using the
[Anaconda Python distribution](https://www.anaconda.com/download/),
with Python version 3.6. Package dependencies for Anaconda and pip can be found
in the `<requirements_*.txt>` files in the repository.


Data sources and processing pipeline
------------------------------------

Preparations:
1. Download the bicycle trip data as csv files from https://developer.oslobysykkel.no/data
1. Get a client ID for the Norwegian Meteorological office's Frost API, see the instructions
   [here](https://frost.met.no/auth/requestCredentials.html); assign the string to the
   variable `<client_id>` in the file `<frost_account.py>` in the `<src/data>` directory.


data directory:| raw (10_get_data.py)            | interim (20_process_raw2interim.py)                                | processed (30_process_interim2processed.py)
---------------| --------------------------------|--------------------------------------------------------------------|--------------------------------------------
bike           | csv.gz files dowloaded manually | trips.feather: cleaned negative time trips; duration limit; sorted | obs_netflow.csv/feather: net flow data
meteorological | downloaded from API             | blindern_interim.csv/feather: joined with days.csv+solar elevation | (included in the above)
calendar       | -                               | days.csv with delta time; hour is local time; no non-service hours | (included in the above)
stations       | -                               |           | stations.csv: first day/time each station is used (written by 31_station_start2processed)



Project Organization
------------

    ├── LICENSE
    ├── Makefile           <- Makefile with commands like `make data` or `make train`
    ├── README.md          <- The top-level README for developers using this project.
    ├── data
    │   ├── interim        <- Intermediate data that has been transformed.
    │   ├── processed      <- The final, canonical data sets for modeling.
    │   └── raw            <- The original, immutable data dump.
    │
    ├── docs               <- A default Sphinx project; see sphinx-doc.org for details
    │
    ├── models             <- Trained and serialized models, model predictions, or model summaries
    │
    ├── notebooks          <- Jupyter notebooks. Naming convention is a number (for ordering),
    │                         the creator's initials, and a short `-` delimited description, e.g.
    │                         `1.0-jqp-initial-data-exploration`.
    │
    ├── references         <- Data dictionaries, manuals, and all other explanatory materials.
    │
    ├── reports            <- Generated analysis as HTML, PDF, LaTeX, etc.
    │   └── figures        <- Generated graphics and figures to be used in reporting
    │
    ├── requirements_conda.txt <- The requirements files for reproducing the environment,
    ├── requirements_pip.txt   <- conda is leading.
    │
    ├── setup.py           <- makes project pip installable (pip install -e .) so src can be imported
    └── src                <- Source code for use in this project.
        ├── __init__.py    <- Makes src a Python module
        │
        ├── data           <- Scripts to download or generate data
        │   └── make_dataset.py
        │
        ├── features       <- Scripts to turn raw data into features for modeling
        │   └── build_features.py
        │
        ├── models         <- Scripts to train models and then use trained models to make
        │   │                 predictions
        │   ├── predict_model.py
        │   └── train_model.py
        │
        └── visualization  <- Scripts to create exploratory and results oriented visualizations
            └── visualize.py


--------
<!--
<p><small>Project based on the <a target="_blank" href="https://drivendata.github.io/cookiecutter-data-science/">cookiecutter data science project template</a>. #cookiecutterdatascience</small></p>
-->
# The Chempiler

This repo contains the Chempiler library. To start a new experiment please refer to [this](http://datalore.chem.gla.ac.uk/Chemputer/example-experiment) repository. Unless you are looking to contribute to Chempiler development you won't need to explicitly clone this repo.

### Authors

* **Cronin Group**

### Prerequisites

* Python 3.6+
* networkx
* pyserial
* OpenCV

### Developing

The following instructions are intended for Chempiler developers (as opposed to Chempiler users). If you simply want to use the Chempiler in your synthesis, please follow the link above.

To make enhancements to the Chempiler, you will want to install it in development mode. By doing this, you `chempiler` package is kept up-to-date with the changes that you make to the code so you won't have to re-install the package to make your changes visible.

```bash
git clone <git URL for this repo>
cd Chempiler
pip install -r requirements.txt
pip install -e .
```

To run the unit tests that come with the Chempiler, you will need to install the `ChemputerAPI` and `SerialLabware` packages as well.

## Project structure

This repository contains the following subfolders and files in the `chempiler` folder. The `docs` folder contains Sphinx documentation. The actual HTML output is [here](/docs/_build/html/index.html).

### tools

This subfolder holds all the technical stuff under the hood. The file `scheduler.py` implements the Chempiler scheduler, which is responsible for planning and executing liquid handling commands. `constants.py` holds a number of global constants and literals. Those are read only, and shouldn't require editing. `vlogging.py` deals with recording log videos.

The subfolder `module_execution` contains all the Executioners. Those are convenience wrapper classes that allow common chemical manipulations, e.g. stirring, to be specified in a more chemically meaningful way.


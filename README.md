# RESPIGHI-fews-adapter

This is the RESPIGHI adapter for FEWS. This adapter is created by D2Hydro (Daniel Tollenaar) for water authority Hoogheemraadschap De Stichtse Rijnlanden (HDSR, ordered by Joost Heijkers). The adapter makes RESPIGHI generally 
applicable for donwscaling MODFLOW phreatic groundwater heads as part of a FEWS workflow.

RESPIGHI is developped by Deltares (Huite Bootsma) and Advies voor Water (Jacco Hoogewoud): https://gitlab.com/deltares/imod/RESPIGHI.git. Rescaling Surface Water and PhreatIc Groundwater Head Interaction
(RESPIGHI) is an open source Python package for rescaling the results of regional iMODFLOW groundwater models to finer resolutions, using surface water data.

## Installation

### Python installation
Make sure you have an Miniconda or Anaconda installation. You can download these here:
 - https://www.anaconda.com/products/individual
 - https://docs.conda.io/en/latest/miniconda.html

During installation, tick the box “Add Anaconda to PATH”, even though it is not advised

### Create a RESPIGHI environment
Use the environment.yml in the repository to create the proper python environment for RESPIGHI in command prompt

*conda env create -f environment.yml*

After installation you can activate your environment in command prompt

*conda activate RESPIGHI*

### Install RESPIGHI
In the activated environment you will clone the RESPIGHI repository and install it in the environment by executing the following three commands in command prompt:

*git clone https://gitlab.com/deltares/imod/RESPIGHI.git*<br>
*cd respighi*<br>
*pip install .*

If you open python in your RESPIGHI environment you will be able to import RESPIGHI:

*import respighi*

### Install the RESPIGHI fews-adapter
It is recommended to install the RESPIGHI fews-adapter in your RESPIGHI invironment as well. In the command prompt with activated environment you can install it by:

*pip install .*

If you open python in your RESPIGHI environment you will be able to import RESPIGHI-fews now:

*import respighifews*

If preferred the adapter-script can be included in the FEWS moduleDataSet or any other location as long as you include both adapter.py and untilities.py in the same folder.

## Run an example
You can test RESPIGHIfews with the example fews-config in examples\vidente
1. Get a copy of FEWS: https://oss.deltares.nl/web/delft-fews
2. Create a FEWS shortcut via the FEWS bin-folder: bin\windows\createShortcuts.exe
3. Put the FEWS-patch in examples\vidente\patch.jar
4. Update the path to your newly created RESPIGHI python environment in sa_global.properties. Assuming you have an anaconda installation on the C-drive that would be:

*PYTHON_ENV = c:/Anaconda3/envs/RESPIGHI*

5. Start FEWS. If all is good you will be able to run the workflow *Downscaling HYDROMEDAH (RESPIGHI)*. That should take +/- 15 mins to complete
6. You will find your results in the gridDisplay at *RESPIGHI Grondwaterstand [cm tov mv]*
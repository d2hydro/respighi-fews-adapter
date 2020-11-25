# respighi-fews-adapter

## python installation
Make sure you have an Miniconda or Anaconda installation. You can download these here:
 - https://www.anaconda.com/products/individual
 - https://docs.conda.io/en/latest/miniconda.html

During installation, tick the box “Add Anaconda to PATH”, even though it is not advised

## create a respighi environment
Use the environment.yml in the repository to create the proper python environment for respighi in command prompt

*conda env create -f environment.yml*

After installation you can activate your environment in command prompt

*conda activate respighi*


## install respighi
In the activated environment you will clone the respighi repository and install it in the environment by executing the following three commands in command prompt
*git clone https://gitlab.com/deltares/imod/respighi.git*
*cd respighi*
*pip install .*

If you open python in your respighi environment you will be able to import respighi
*import respighi

## use or install the respighi fews-adapter
In example\vidente we keep the respighi python scripts in the ModuleDataSet as part of FEWS. In the repository a setup is available to include it in the respighi environment.
If you prefer the respighi fews-adapter in your environment you can activate your respighi environment and install this module by:
*pip install .*


# -*- coding: utf-8 -*-

__title__ = 'fews_adapter'
__description__ = 'fews adapter for Respighi downscaling module'
__version__ = '0.9.0'
__author__ = 'Daniel Tollenaar'
__author_email__ = 'daniel@d2hydro.nl'
__license__ =  'MIT License'

# import os-modules
import os
from pathlib import Path
import sys

# set python environment (similar to: conda activate "env_name")
python_exe = Path(sys.executable)
python_env = python_exe.parent
env = os.environ

env['PATH'] = ('{python_env};'
                '{python_env}\\Library\\mingw-w64\\bin;'
                '{python_env}\\Library\\usr\\bin;'
                '{python_env}\\Library\\bin;'
                '{python_env}\\Scripts;'
                '{python_env}\\bin;'
                '{path}').format(path=env['PATH'],
                                python_env=python_env  
                                            )
env['VIRTUAL_ENV'] = str(python_env)

# now safely import the rest
import click
import datetime
import dask
from utilities import xml_to_dict
import imod
import logging
from lxml import etree as ET
import numpy as np
import pyproj
from respighi import chunked, util
import traceback
from schema import And, Optional, Use
import warnings
import xarray as xr

warnings.filterwarnings('ignore')

# pi_diagnostics properties
diag_xml = 'pi_diagnostics.xml'
nsmap = {None: 'http://www.wldelft.nl/fews/PI',
         'xsi':'http://www.w3.org/2001/XMLSchema-instance'}
schema = attr_qname = ET.QName(nsmap['xsi'], 'schemaLocation')
diag = ET.Element('Diag',
                  {schema:'http://www.wldelft.nl/fews/PI http://fews.wldelft.nl/schemas/version1.0/pi-schemas/pi_diag.xsd'},
                  nsmap=nsmap)

# conversion-dict for log function 
log_levels = {'error':'1',
              'warning':'2',
              'info':'3',
              'debug':'4'}

# logger and its properties
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
sh = logging.StreamHandler()
sh.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(levelname)s: %(message)s')
sh.setFormatter(formatter)
logger.addHandler(sh)

# toml schema extension
FEWS_SCHEMA = {
            'fews': {
                'input_type': str,
                Optional('input_file', default=None): And(str, Use(util._to_path)),
                Optional('state_config', default=None): And(str, Use(util._to_path)),
                'crs': str,
                Optional('surface_idf', default=None): And(str, Use(util._to_path)),
                'result': str
                }
            }

EXTENDED_SCHEMA = {**FEWS_SCHEMA, **util.CONFIG_SCHEMA}

#%% functions
def _flush_diag():
    '''flushes diagnostics to drive'''
    
    tree = ET.ElementTree(diag)
    tree.write(diag_xml,
               xml_declaration=True,
               encoding='utf-8',
               pretty_print=True)
    
    
def _log(level,msg):
    '''adds a log-message to logger and xml'''
    
    # screen logger
    screen_logger = getattr(logger, level, None)
    screen_logger(msg)
    
    # diagnostics
    ET.SubElement(diag , 'line', level=log_levels[level], description=msg)
    
def set_environment():
    '''sets all environment variables relative to running python.exe'''
    
    python_exe = Path(sys.executable)
    python_env = python_exe.parent
    env = os.environ
    
    env['PATH'] = ('{python_env};'
                    '{python_env}\\Library\\mingw-w64\\bin;'
                    '{python_env}\\Library\\usr\\bin;'
                    '{python_env}\\Library\\bin;'
                    '{python_env}\\Scripts;'
                    '{python_env}\\bin;'
                    '{path}').format(path=env['PATH'],
                                    python_env=python_env  
                                                )
    env['VIRTUAL_ENV'] = str(python_env)
    
def get_config(ini):
    '''returns config for fews-adapter'''
    
    return util.read_toml(ini, schema_dict=EXTENDED_SCHEMA)

def pre_adapter(config):
    '''converts FEWS-export to RESPIGHI input'''
    
    if config['fews']['input_type'] == 'imod_state':   
        #get time
        _log('debug','read datetime from state-config')
        state_config = xml_to_dict(config['fews']['state_config'])
        date = state_config['State']['dateTime']['date']
        time = state_config['State']['dateTime']['time']
        date_time = datetime.datetime.strptime('{} {}'.format(date,time),'%Y-%m-%d %H:%M:%S')
        date_time = np.array([date_time]).astype('datetime64[ns]')
        
    else:
        _log('error',f'{config["fews"]["input_type"]} is not a valid input_type [use: imod_state]')
        raise Exception()
        
    return config, date_time

def run_respighi(config):
    '''runs respighi'''
    data = util.load_data(config)
    _log('debug','Generating chunks')
    chunks = chunked.create_chunks(
        data, config['general']['cellsize'], config['general']['chunksize']
    )
    # parallel computation
    chunks_result = dask.compute(chunked.rescale_submodels(chunks, config['general']))[
        0
    ]
    # combine into a single DataArray
    _log('debug','Merging...')
    spatial_ref = list(imod.util.spatial_reference(data['phreatic_head']))
    spatial_ref[0] = config['general']['cellsize']
    spatial_ref[3] = -1.0 * config['general']['cellsize']
    
    return chunked.merge_chunks(chunks_result, spatial_ref)

def post_adapter(head, config, date_time):
    '''processes results to netCDF'''
    
    #add time to head
    head.name = 'head'
    ds = head.to_dataset()
    ds['head'].assign_attrs(units='m', long_name='groundwater level')
    
    if config['fews']['surface_idf']:
        _log('debug','computing groundwater depths')
        with imod.idf.open(config['fews']['surface_idf']) as surface:
            ds['depth_m'] = surface - head
            ds['depth_cm'] = ds['depth_m'] * 100
            ds['depth_m'].assign_attrs(units='m', long_name='groundwater depth (m below surface)')
            ds['depth_cm'].assign_attrs(units='cm', long_name='groundwater depth (cm below surface)')
    
    #add time dimension
    _log('debug','adding time')
    ds = ds.expand_dims({'time': 1})
    ds = ds.assign_coords({'time': date_time})
     
    #add crs
    _log('debug','adding crs')
    crs = pyproj.CRS(config['fews']['crs'])
    crs_name = crs.name
    crs = xr.DataArray(data=0,
                       name='crs',
                       attrs={'standard_name':'coordinate reference system',
                              'crs_wkt':crs.to_wkt(),
                              'proj4_params':crs.to_proj4(),
                              'epsg_code':f'EPSG:{crs.to_epsg()}'})
    ds['crs'] = crs
    
    #add metadata (attributes)
    _log('debug','adding meta-data')
    ds['x'] = ds['x'].assign_attrs(
        units='m',
        long_name='x coordinate',
        standard_name='projection_x_coordinate',
        axis='X',
        )
    ds['y'] = ds['y'].assign_attrs(
        units='m',
        long_name='y coordinate',
        standard_name='projection_y_coordinate',
        axis='Y',
    )
    ds['time'] = ds['time'].assign_attrs(standard_name='time', axis='T')
    ds['dx'] = ds['dx'].assign_attrs(units='m', long_name='cell size along x dimension')
    ds['dy'] = ds['dy'].assign_attrs(units='m', long_name='cell size along y dimension')
    
    # add metadata attributes to make it more CF compliant
    ds = ds.assign_attrs(Conventions='CF-1.6',
                             title='RESPIGHI gridded output',
                             institution='Deltares',
                             references='http://www.delft-fews.com',
                             summary='RESPIGHI gridded model output',
                             date_created=datetime.datetime.utcnow().replace(microsecond=0).isoformat(' ')
                             + ' GMT',
                             coordinate_system=crs_name,
                             )

    # forecast reference time for Delft-FEWS
    # https://publicwiki.deltares.nl/display/FEWSDOC/NetCDF+formats+that+can+be+imported+in+Delft-FEWS
    analysis_time = [np.datetime64('now', 'ms')]
    ds['analysis_time'] = xr.DataArray(data=analysis_time,
                                       name='analysis_time',
                                       coords={'analysis_time': analysis_time},
                                       dims=['analysis_time'],
                                       attrs={'standard_name':'forecast_reference_time'})

    Path(config['fews']['result']).parent.mkdir(exist_ok=True)
        
    ds.to_netcdf(config['fews']['result'])

    return ds     
    
#%% main function called by adapter
@click.command()
@click.option('-configtoml', help='Path to the adapter .toml file.')

def main(configtoml):
    ''' main adapter function if script is run by cmd '''
    try:
        _log('info','adapter intializing')
        _log('debug','setting python environment')
        set_environment()
        
        _log('debug','read config')
        
        config = get_config(configtoml)
        
        #run pre-adapter, possibly updating the phreatic_head idf
        _log('info','running pre-adapter')
        config, date_time = pre_adapter(config)
        
        _log('info','running RESPIGHI')
        head = run_respighi(config)
        
        _log('info','running post-adapter')
        post_adapter(head, config, date_time)
                            
        _log('info','finished')
        _flush_diag()
        logging.shutdown()
        
    except Exception as e: 
        _log('error',f'FEWS adapter failed with error: {e}')
        _flush_diag()
        traceback.print_exc()

if __name__ == '__main__':
    main()
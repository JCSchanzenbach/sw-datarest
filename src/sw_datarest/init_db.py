"""Support for dynamic model creation.
"""

import collections
import json
import sys
import attrdict
from pydantic import create_model, Field
from typing import List 
from . import tableschema
from . import database_sqlalchemy
import subprocess
import csv
import pathlib
import sys


# local imports
from .app_config import config

# adding configuration to model
#factory function for creating tuple subclasses with named fields
ModelCombo = collections.namedtuple(
    'ModelCombo',
    ['resource_name', 'resource_model', 'resource_collection_model', 'dbtable',
     'id_column'])



def create_db_table(model_name, model_def):
    """Dynamically create pydantic model from config model definition.
    
    FastAPI uses pydantic models to describe endpoint input/output data.
    
    Parameters:
       model_name: resource name string
       model_def: model definition from config file (AttrDict)
    Returns: A ModelCombo object
    """
    # Create resource + collection model class names using standard Python conventions
    model_name_title = model_name.title()
    model_cls_name = '{}Model'.format(model_name_title)    
    collection_model_cls_name = '{}CollectionModel'.format(model_name_title)
  
    # use database-sqlalchemy as the default profile 
    profile = getattr(model_def, 'profile', 'database-sqlalchemy') 
    #if profile == 'table-schema':
    #    id_column, model = tableschema.create_model_from_tableschema(
    #        model_cls_name, model_def.schema)
    #    collection_model = create_model(
    #        collection_model_cls_name, **{model_name: (List[model], ...)})
    #    return ModelCombo(
    #        resource_name=model_name,
    #        resource_model=model,
    #        resource_collection_model=collection_model,
    #        dbtable=model_def.dbtable,
    #        id_column=id_column)
        
    if profile == 'database-sqlalchemy':
        #import_cmd = ".import {model_name}.csv t_{model_name}".format(model_name=model_name)
        #import_cmd = f".import {model_name}.csv t_{model_name}"
        csv_filename = f"{model_name}.csv"
        db_tablename = f"t_{model_name}"
        import_cmd = f".import {csv_filename} {db_tablename}"
        file_name = "app.db"

        #use scv.read to read header line
        reader = csv.reader(open(csv_filename))
        col_names = next(reader)

        #generate column DDL nisppes, all type TEXT, 1st col. primary key
        col_defs = [f'"{col}" TEXT' for col in col_names]
        col_defs[0] += ' NOT NULL PRIMARY KEY'
        col_defs_str = ', '.join(col_defs)

        # construct table, create PathName
        path_name = f"CREATE TABLE {db_tablename}({col_defs_str});"

        subprocess.run(['/opt/subtools/current/bin/sqlite3', f'{file_name}',f'{path_name}', '.mode csv', '.separator ,', f'{import_cmd}'])
    
        return

    raise ValueError('Unsupported data profile')


def create_db_tables(config):
    """Loop over config data resources to create pydantic models.
        Parameters:
        config: config dictionary (AttrDict)
        Returns: (model_name, model)-dictionary
    """
    for model_name, model_def in config.datarest.data.items():
        # AttrDict.items() does not return AttrDict-wrapped dicts for values
        # that are dicts
        model_def = attrdict.AttrDict(model_def)
        create_db_table(model_name, model_def)


def init(args):
    create_db_tables(config)

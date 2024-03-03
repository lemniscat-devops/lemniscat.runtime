# importing module.py file
import importlib 
from lemniscat.core.util.helpers import LogUtil
from importlib import resources as impresources
  
logger = LogUtil.create()
pkg = importlib.import_module('lemniscat.plugin.terraform')
myClass = getattr(pkg, 'Action')
myClass(logger).info()

# Opens the NWB conversion GUI
# authors: Luiz Tauffer and Ben Dichter
# written for Jaeger Lab
# ------------------------------------------------------------------------------
from nwbn_conversion_tools.gui.nwbn_conversion_gui import nwbn_conversion_gui
from ndx_fret import FRET, FRETSeries

metafile = 'metafile.yml'
conversion_module = 'conversion_module.py'

source_paths = {}
source_paths['file1'] = {'type': 'file', 'path': ''}
source_paths['file2'] = {'type': 'file', 'path': ''}

kwargs_fields = {}

nwbn_conversion_gui(
    metafile=metafile,
    conversion_module=conversion_module,
    source_paths=source_paths,
    kwargs_fields=kwargs_fields
)

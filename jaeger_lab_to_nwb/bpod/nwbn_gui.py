# Opens the NWB conversion GUI
# authors: Luiz Tauffer and Ben Dichter
# written for Jaeger Lab
# ------------------------------------------------------------------------------
from nwbn_conversion_tools.gui.nwbn_conversion_gui import nwbn_conversion_gui

import os


def main():
    here = os.path.dirname(os.path.realpath(__file__))
    metafile = os.path.join(here, 'metafile.yml')
    conversion_module = os.path.join(here, 'conversion_module.py')

    # Source paths
    source_paths = dict()
    source_paths['file_behavior_bpod'] = {'type': 'file', 'path': ''}

    # Lab-specific kwargs
    kwargs_fields = {
        'add_bpod': True,
    }

    nwbn_conversion_gui(
        metafile=metafile,
        conversion_module=conversion_module,
        source_paths=source_paths,
        kwargs_fields=kwargs_fields,
    )


if __name__ == '__main__':
    main()
# authors: Luiz Tauffer and Ben Dichter
# written for Jaeger Lab
# ------------------------------------------------------------------------------
from pynwb import NWBFile, NWBHDF5IO
from pynwb.file import Subject

from jaeger_lab_to_nwb.resources.add_ecephys import add_ecephys_rhd
from jaeger_lab_to_nwb.resources.add_behavior import add_behavior_treadmill

import pandas as pd
import yaml
import copy
import os


def conversion_function(source_paths, f_nwb, metadata, add_ecephys,
                        add_behavior, **kwargs):
    """
    Copy data stored in a set of .npz files to a single NWB file.

    Parameters
    ----------
    source_paths : dict
        Dictionary with paths to source files/directories. e.g.:
        {'dir_ecepys_rhd': {'type': 'dir', 'path': ''},
         'file_electrodes': {'type': 'file', 'path': ''},
         'dir_behavior': {'type': 'dir', 'path': ''}}
    f_nwb : str
        Path to output NWB file, e.g. 'my_file.nwb'.
    metadata : dict
        Metadata dictionary
    **kwargs : key, value pairs
        Extra keyword arguments
    """

    # Source files and directories
    dir_ecephys_rhd = None
    file_electrodes = None
    dir_behavior = None
    for k, v in source_paths.items():
        if v['path'] != '':
            if k == 'dir_ecephys_rhd':
                dir_ecephys_rhd = v['path']
            if k == 'file_electrodes':
                file_electrodes = v['path']
            if k == 'dir_behavior':
                dir_behavior = v['path']

    # Get initial metadata
    meta_init = copy.deepcopy(metadata['NWBFile'])

    # Initialize a NWB object
    nwbfile = NWBFile(**meta_init)

    # Add subject metadata
    experiment_subject = Subject(
        age=metadata['Subject']['age'],
        subject_id=metadata['Subject']['subject_id'],
        species=metadata['Subject']['species'],
        description=metadata['Subject']['description'],
        genotype=metadata['Subject']['genotype'],
        date_of_birth=metadata['Subject']['date_of_birth'],
        weight=metadata['Subject']['weight'],
        sex=metadata['Subject']['sex']
    )
    nwbfile.subject = experiment_subject

    # Adding ecephys
    if add_ecephys:
        nwbfile = add_ecephys_rhd(
            nwbfile=nwbfile,
            metadata=metadata,
            source_dir=dir_ecephys_rhd,
            electrodes_file=file_electrodes,
        )

    # Adding behavior
    if add_behavior:
        # Detect relevant files: trials summary, treadmill data and nose data
        all_files = os.listdir(dir_behavior)
        trials_file = [f for f in all_files if ('_tr.csv' in f and '~lock' not in f)][0]
        treadmill_file = trials_file.split('_tr')[0] + '.csv'
        nose_file = trials_file.split('_tr')[0] + '_mk.csv'

        trials_file = os.path.join(dir_behavior, trials_file)
        treadmill_file = os.path.join(dir_behavior, treadmill_file)
        nose_file = os.path.join(dir_behavior, nose_file)

        # Add trials
        df_trials_summary = pd.read_csv(trials_file)

        nwbfile.add_trial_column(name='fail', description='')
        nwbfile.add_trial_column(name='reward_given', description='')
        nwbfile.add_trial_column(name='total_rewards', description='')
        nwbfile.add_trial_column(name='init_dur', description='')
        nwbfile.add_trial_column(name='light_dur', description='')
        nwbfile.add_trial_column(name='motor_dur', description='')
        nwbfile.add_trial_column(name='post_motor', description='')
        nwbfile.add_trial_column(name='speed', description='')
        nwbfile.add_trial_column(name='speed_mode', description='')
        nwbfile.add_trial_column(name='amplitude', description='')
        nwbfile.add_trial_column(name='period', description='')
        nwbfile.add_trial_column(name='deviation', description='')

        t_offset = df_trials_summary.loc[0]['Start Time']
        for index, row in df_trials_summary.iterrows():
            nwbfile.add_trial(
                start_time=row['Start Time'] - t_offset,
                stop_time=row['End Time'] - t_offset,
                fail=row['Fail'],
                reward_given=row['Reward Given'],
                total_rewards=row['Total Rewards'],
                init_dur=row['Init Dur'],
                light_dur=row['Light Dur'],
                motor_dur=row['Motor Dur'],
                post_motor=row['Post Motor'],
                speed=row['Speed'],
                speed_mode=row['Speed Mode'],
                amplitude=row['Amplitude'],
                period=row['Period'],
                deviation=row['+/- Deviation'],
            )

        # Add continuous behavioral data
        nwbfile = add_behavior_treadmill(
            nwbfile=nwbfile,
            metadata=metadata,
            treadmill_file=treadmill_file,
            nose_file=nose_file
        )

    # Saves to NWB file
    with NWBHDF5IO(f_nwb, mode='w') as io:
        io.write(nwbfile)
    print('NWB file saved with size: ', os.stat(f_nwb).st_size / 1e6, ' mb')


# If called directly fom terminal
if __name__ == '__main__':
    """
    Usage: python conversion_module.py [output_file] [metafile] [dir_ecephys_rhd]
    [file_electrodes] [dir_behavior] [-add_ecephys] [-add_behavior]
    """
    import argparse
    import sys

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "output_file", help="Output file to be created."
    )
    parser.add_argument(
        "metafile", help="The path to the metadata YAML file."
    )
    parser.add_argument(
        "dir_ecephys_rhd", help="The path to the directory containing rhd files."
    )
    parser.add_argument(
        "file_electrodes", help="The path to the electrodes info file."
    )
    parser.add_argument(
        "dir_behavior", help="The path to the directory containing behavior data files."
    )
    parser.add_argument(
        "--add_ecephys",
        action="store_true",
        default=False,
        help="Whether to add the ecephys data to the NWB file or not",
    )
    parser.add_argument(
        "--add_behavior",
        action="store_true",
        default=False,
        help="Whether to add the behavior data to the NWB file or not",
    )

    if not sys.argv[1:]:
        args = parser.parse_args(["--help"])
    else:
        args = parser.parse_args()

    source_paths = {
        'dir_ecephys_rhd': {'type': 'dir', 'path': args.dir_ecephys_rhd},
        'file_electrodes': {'type': 'file', 'path': args.file_electrodes},
        'dir_behavior': {'type': 'dit', 'path': args.dir_behavior},
    }

    f_nwb = args.output_file

    # Load metadata from YAML file
    metafile = args.metafile
    with open(metafile) as f:
        metadata = yaml.safe_load(f)

    # Lab-specific kwargs
    kwargs_fields = {
        'add_ecephys': args.add_ecephys,
        'add_behavior': args.add_behavior
    }

    conversion_function(source_paths=source_paths,
                        f_nwb=f_nwb,
                        metadata=metadata,
                        **kwargs_fields)
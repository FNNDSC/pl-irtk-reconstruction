#
# irtk ds ChRIS plugin app
#
# (c) 2021 Fetal-Neonatal Neuroimaging & Developmental Science Center
#                   Boston Children's Hospital
#
#              http://childrenshospital.org/FNNDSC/
#                        dev@babyMRI.org
#
#
# upstream:
# https://github.com/ilegorreta/Automatic-Fetal-Brain-Reconstruction-Pipeline/blob/main/reconstruction.sh

from chrisapp.base import ChrisApp
import csv
from glob import iglob
from os import path
import logging
import sys
import subprocess as sp


Gstr_title = r"""
 ___________ _____ _   __ ______                         _                   _   _
|_   _| ___ \_   _| | / / | ___ \                       | |                 | | (_)
  | | | |_/ / | | | |/ /  | |_/ /___  ___ ___  _ __  ___| |_ _ __ _   _  ___| |_ _  ___  _ __
  | | |    /  | | |    \  |    // _ \/ __/ _ \| '_ \/ __| __| '__| | | |/ __| __| |/ _ \| '_ \
 _| |_| |\ \  | | | |\  \ | |\ \  __/ (_| (_) | | | \__ \ |_| |  | |_| | (__| |_| | (_) | | | |
 \___/\_| \_| \_/ \_| \_/ \_| \_\___|\___\___/|_| |_|___/\__|_|   \__,_|\___|\__|_|\___/|_| |_|
"""

description = r"""
A ChRIS ds plugin wrapper around IRTK reconstruction for fetal brain MRI.
This plugin's input is tightly coupled to the output of pl-fetal-brain-assessment v1.3.0.
"""

logger = logging.getLogger(__name__)


class IrtkRecon(ChrisApp):
    """
    Fetal brain MRI Reconstruction
    """
    PACKAGE                 = __package__
    TITLE                   = 'IRTK Reconstruction'
    CATEGORY                = 'Reconstruction'
    TYPE                    = 'ds'
    ICON                    = ''   # url of an icon image
    MIN_NUMBER_OF_WORKERS   = 1    # Override with the minimum number of workers as int
    MAX_NUMBER_OF_WORKERS   = 1    # Override with the maximum number of workers as int
    MIN_CPU_LIMIT           = 1000 # Override with millicore value as int (1000 millicores == 1 CPU core)
    MIN_MEMORY_LIMIT        = 200  # Override with memory MegaByte (MB) limit as int
    MIN_GPU_LIMIT           = 0    # Override with the minimum number of GPUs as int
    MAX_GPU_LIMIT           = 0    # Override with the maximum number of GPUs as int

    # Use this dictionary structure to provide key-value output descriptive information
    # that may be useful for the next downstream plugin. For example:
    #
    # {
    #   "finalOutputFile":  "final/file.out",
    #   "viewer":           "genericTextViewer",
    # }
    #
    # The above dictionary is saved when plugin is called with a ``--saveoutputmeta``
    # flag. Note also that all file paths are relative to the system specified
    # output directory.
    OUTPUT_META_DICT = {}

    def define_parameters(self):
        """
        Define the CLI arguments accepted by this plugin app.
        Use self.add_argument to specify a new app argument.
        """
        self.add_argument(
            '-p', '--inputPathFilter',
            dest='inputPathFilter',
            help='Input files selection.',
            default='Best_Images_crop/*.nii',
            type=str,
            optional=True
        )
        self.add_argument(
            '-c', '--csv',
            dest='csv',
            help='Location of CSV file containing quality assessment and slice thickness data. '
                 'Typically, this would be the output from pl-fetal-brain-assessment v1.3.0.',
            default='quality_assessment.csv',
            type=str,
            optional=True
        )
        self.add_argument(
            '-o', '--output',
            dest='output',
            help='Output filename.',
            default='recon.nii',
            type=str,
            optional=True
        )
        self.add_argument(
            '-d', '--debug',
            dest='debug',
            help='Save intermediate results.',
            default=False,
            type=bool,
            optional=True
        )

    def run(self, options):
        """
        Define the code to be run by this plugin app.
        """
        input_pattern = path.join(options.inputdir, options.inputPathFilter)
        input_file_map = {}
        for filename in iglob(input_pattern):
            input_file_map[path.basename(filename)] = filename

        """
        File names from pl-fetal-brain-assessment will come in the form of:
        /share/incoming/T2_HASTE_123456_brain_crop.nii
        So we need to map the basenames to what we find in this input dir.
        """
        logger.setLevel(logging.DEBUG)

        csv_filename = path.join(options.inputdir, options.csv)
        qa = []

        with open(csv_filename, 'r') as f:
            for row in csv.DictReader(f):
                if 'filename' not in row:
                    logger.error('%s (a CSV file) does not contain the column "filename"'
                                 '\nYou must run pl-fetal-brain-assessment before pl-irtk-reconstruction'
                                 ' to create the correct CSV file.', csv_filename)
                    sys.exit(1)

                key = path.basename(row['filename'])
                logger.info(key)
                if key not in input_file_map:
                    logger.info('not found')
                    continue
                row['filename'] = input_file_map[key]
                del input_file_map[key]
                qa.append(row)

        if input_file_map:
            logging.error('The following files were not mentioned in %s:', csv_filename)
            for _, input_filename in input_file_map.items():
                logging.error(input_filename)
            sys.exit(1)

        print(Gstr_title, flush=True)
        logger.setLevel(logging.DEBUG)

        # for whatever reason, we should be giving the arguments to reconstruction
        # sorted by best to worst quality
        qa = sorted(qa, key=lambda row: row['quality'], reverse=True)

        cmd = [
            'reconstruction',
            path.join(options.outputdir, options.output),
            str(len(qa)),
            *[row['filename'] for row in qa],
            '-thickness',
            *[row['slice_thickness'] for row in qa],
            '-packages',
            *(['1'] * len(qa))
        ]

        if options.debug:
            cmd.append('-debug')

        logger.info(' '.join(cmd))

        try:
            sp.run(cmd, cwd=options.outputdir, check=True)
        except sp.CalledProcessError as e:
            sys.exit(e.returncode)

    def show_man_page(self):
        self.description = description  # argparse description
        self.print_help()

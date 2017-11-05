#!/usr/bin/env python
#
import sys, argparse, logging
logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.DEBUG)

import config, datafiles
from runner import process_data_task

# we need to connect to proper ampq server in order to submit tasks:
from celery import Celery
celery = Celery('task', broker=config.CELERY_BROKER_URL)


def main(args):
    """Main function that traverses data repo, splits data on "per-patient" tasks
    and submits tasks into a task queue to be processed in parallel
    """
    logging.debug("Starting to parse: %s" % args.directory)
    # parse directory specified at command line
    patient_list = datafiles.parse_data_dir(args.directory)

    # NOTE: for this demo we will break down data we have into 'per-patient' chunks
    # and process each in a separate task. we can run all tasks in parallel
    for single_patient_files in patient_list: # each row in list.csv is a "patient"
        #
        # NOTE: at this point we would push files to some data storage (ex: AWS)
        # for celery task to pickup. In this demo we will just pass filepaths
        # (instead of bucket id) to celery tasks

        # submit single_patient_files for processing to celery task
        celery_task = process_data_task.delay(single_patient_files)
        logging.debug('Submitted celery task %s' % (celery_task.id))


# program entry point
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Data dir with dicom/contour files')
    parser.add_argument('-d','--directory', help='Directory to process', required=True)
    args = parser.parse_args()
    main(args)

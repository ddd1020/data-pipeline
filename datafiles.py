"""Code for parsing data directory (ie: dir with contours/dicoms/link files) """

import os, csv, logging
import config
logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.DEBUG)

def get_files(dirname, split_string, split_index):
    """Helper function that actually calls os.listdir()

    :param dirname: directory to parse
    :param split_string: string to split filename
    :param split_index: index of ID portion of split filename
    :return: dictionary of file IDs and filepaths
    """
    if not os.path.isdir(dirname):
        logging.error('dir does not exist %s' % dirname)
        return None

    logging.debug('processing dir: %s' % dirname)
    dir_dic = {}
    for f in os.listdir(dirname):
        filename_split = f.split(split_string)  #extract the ID part of filename
        try: # in case some non-pattern file is in directory, skip it.
            dir_dic[int(filename_split[split_index])] = os.path.abspath(os.path.join(dirname, f))
        except ValueError:
            logging.error('could not process filename %s' % f)
    return dir_dic

def get_dicom_files(dirname):
    """Gets dic of dicom files in a given dirname

    :param dirname: dicom directory to parse
    :return: dictionary of dicom file IDs and filepaths
    """
    return get_files(dirname, ".", 0)  # TODO: hardcoded file ID index


def get_contour_files(dirname):
    """Gets dic of contour files in a given dirname

    :param dirname: contour directory to parse
    :return: dictionary of contour file IDs and filepaths
    """
    return get_files(dirname, "-", 2)  # TODO: hardcoded file ID index


def get_available_file_pairs(dicom_dic, countour_dic):
    """Return list of available dicom-contour file pairs

    NOTE: file pairing strategy is quite simple: we are trying to pair INTs in
    filenames of contour and dicom files. For example, this is considered a pair:

    final_data/contourfiles/SC-HF-I-1/i-contours/IM-0001-0048-icontour-manual.txt
    final_data/dicoms/SCD0000101/48.dcm

    because both files have INT ID = 48 (and linked in link.csv)

    :param dicom_dic: dictionary of dicom file IDs and filepaths
    :param countour_dic: dictionary of contour file IDs and filepaths
    :return: list of matched dicom-contour file pairs (matched by file ID)
    """
    available_file_pairs_list = []

    for dicom_file_id, dicom_file_path in dicom_dic.iteritems():
        if dicom_file_id in countour_dic:
            available_file_pairs_list.append((dicom_file_path, countour_dic[dicom_file_id]))

    return available_file_pairs_list


def parse_link_file(filename):
    """Parse given link.csv file into a list of patient file IDs

    :param filename: path to link.csv
    :return: dictionary of mapped contour-dicom directories
    """
    links = []

    try:
        with open(filename) as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                 links.append((row[config.CSV_DICOM_COLUMN_NAME], row[config.CSV_CONTOUR_COLUMN_NAME]))
    except Exception, e:
        logging.error('Can not load link file %s' % e)
    return links


def parse_data_dir(dirname):
    """Parse given data directory and return a dictionary of mapped
    contour-dicom file pairs.

    NOTE: we will assume that there are no nested dirs inside dicom/contour dirs

    :param dirname: directory containing contours/dicoms/link files
    :return: dictionary with mapped contour-dicom filepaths
    """

    result_list = []

    logging.debug('Starting to process data dir: "%s"' % dirname)

    # load link.csv into a dictionary
    links = parse_link_file(os.path.join(dirname, config.LINK_FILE_NAME))

    # process each row (aka patient) in link.csv
    for ddir, cdir in links:
        logging.debug('processing link dir pair: "%s" and "%s"' % (ddir, cdir))

        # get dicom files
        dicom_dic = get_dicom_files(os.path.join(dirname, config.DICOM_DIR_NAME, ddir))
        if not dicom_dic:
            continue
        # get contour files
        countour_dic = get_contour_files(os.path.join(dirname, config.CONTOUR_DIR_NAME, cdir, config.COUNTOUR_TYPE))
        if not countour_dic:
            continue
        # find intersection of dicom/contour dics (list of available pairs)
        paired_link_files = get_available_file_pairs(dicom_dic, countour_dic)
        logging.debug('total pairs found: %d' % len(paired_link_files))
        result_list.append(paired_link_files)

    #logging.debug('Parse result: %s' % result_list)
    return result_list

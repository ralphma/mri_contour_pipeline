import os
import re

_DICOM_FILE_ID_EXTRACTION_RE = "(?P<id>[0-9]+).dcm"
_CONTOUR_FILE_ID_EXTRACTION_RE = "IM-0001-(?P<id>[0-9]+)-icontour-manual.txt"

def extract_dicom_id_from_dicom_filepath(dicom_filepath):
    """Parses the dicom file id from an absolute dicom filepath.

    :param dicom_filepath: string filepath of the dicom file.
    :return: int id of the dicom. -1 if filepath is misformated.
    """
    file = os.path.basename(dicom_filepath)
    match = re.search(_DICOM_FILE_ID_EXTRACTION_RE, file)
    if not match:
        return -1
    return int(match.group("id"))
    

def extract_dicom_id_from_contour_filepath(contour_filepath):
    """Parses the dicom file id from an absolute dicom filepath.

    :param contour_filepath: string filepath of the contour file.
    :return: int id of the matching dicom file. -1 if filepath is misformated.
    """
    file = os.path.basename(contour_filepath)
    match = re.search(_CONTOUR_FILE_ID_EXTRACTION_RE, file)
    if not match:
        return -1
    return int(match.group("id"))
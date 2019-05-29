import pytest

import util

class TestExtractIdFromDicomFile(object):
    def test_correct_id_extracted(self):
        """Tests the correct id can be extracted from correctly formated file."""
        test_string = "/test/data/dicom/SCD0000101/2.dcm"
        assert util.extract_dicom_id_from_dicom_filepath(test_string) == 2
        
class TestExtractIdFromContourFile(object):
    def test_correct_id_extracted(self):
        """Tests the correct id can be extracted from correctly formated file."""
        test_string = "/test/data/contour/SC-HF-I-1/IM-0001-0048-icontour-manual.txt"
        assert util.extract_dicom_id_from_contour_filepath(test_string) == 48
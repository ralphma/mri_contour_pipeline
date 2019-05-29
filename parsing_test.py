import numpy as np
import pytest

import parsing

_TEST_CONTOUR_FILE = "./test_data/parsing/test_contour"
_TEST_DICOM_FILE = "./test_data/parsing/test.dcm"

class TestContourParsing(object):
    def test_correct_contour(self):
        """Tests a correct vertices list can be parsed."""
        tuple_list = parsing.parse_contour_file(_TEST_CONTOUR_FILE)
        assert tuple_list == [(1.0, 2.0), (3.0, 4.0)]
        
class TestDicomParsing(object):
    def test_pixel_data_parsed(self):
        """Tests an image can be parsed into 'pixel_data' and the image size is expected."""
        dicom_map = parsing.parse_dicom_file(_TEST_DICOM_FILE)
        assert "pixel_data" in dicom_map
        assert np.array_equal(dicom_map["pixel_data"].shape, np.array([256, 256]))
        
class TestPolyToMask(object):
    def test_simple_rect(self):
        """Tests the inside of a triangle is marked with True."""
        test_rect = parsing.poly_to_mask([(0,0), (3,0), (0, 3)], width=3, height=3)
        expected = np.zeros((3,3)).astype(bool)
        expected[1,1] = True
        assert np.array_equal(test_rect, expected)
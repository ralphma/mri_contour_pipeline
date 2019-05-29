import collections
import pytest

import dataset

_TEST_CSV_LINK = "./test_data/dataset/link.csv"
_TEST_CONTOUR_DIR = "./test_data/dataset/contours"
_TEST_DICOMS_DIR = "./test_data/dataset/dicoms"

class TestDataset(object):
    def setup_method(self):
        """Make sure every test has a fresh Dataset.
        
        The dataset has 2 datapoints.
        """
        self.dataset = dataset.Dataset(shuffle_data=False, return_indefinitely=False)
        self.dataset.parse_from_csv(_TEST_CSV_LINK, dicom_dir=_TEST_DICOMS_DIR, contour_dir=_TEST_CONTOUR_DIR)
        
    def test_dataset_parsed_correctly_from_csv(self):
        """Tests there should be two elements in dataset."""
        data = [x for x in self.dataset]
        assert len(data) == 2
        assert data[0].dicom_path == "./test_data/dataset/dicoms/DC-3/100.dcm"
        assert data[0].contour_path == "./test_data/dataset/contours/AB-2/i-contours/IM-0001-0100-icontour-manual.txt"
        assert data[1].dicom_path == "./test_data/dataset/dicoms/DC-3/101.dcm"
        assert data[1].contour_path == "./test_data/dataset/contours/AB-2/i-contours/IM-0001-0101-icontour-manual.txt"        
        
    def test_dataset_shuffles(self):
        """Tests whether the dataset is shuffled per epoch. Has 1/(2^50) chance of failure.
        
        If the dataset is being shuffled, the first element of every epoch should be different
        with probability 1/2.
        """
        self.dataset.shuffle_data = True
        self.dataset.return_indefinitely = True
        dicom_path = set()
        i = 0
        for data in self.dataset:
            if i == 50: break
            i += 1
            if i % 2 == 0: continue
            dicom_path.add(data.dicom_path) 
        assert i == 50
        assert len(dicom_path) != 1
        
    def test_data_shuffle_is_per_epoch(self):
        """Tests the dataset will return indefinitely."""
        self.dataset.shuffle_data = True
        self.dataset.return_indefinitely = True
        i = 0
        all_dicom_path = []
        for data in self.dataset:
            if i == 50: break
            i += 1
            all_dicom_path.append(data.dicom_path) 
        counter = collections.Counter(all_dicom_path)
        assert counter["./test_data/dataset/dicoms/DC-3/100.dcm"] == counter["./test_data/dataset/dicoms/DC-3/101.dcm"]
                
            

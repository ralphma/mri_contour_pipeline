"""Dataset class for loading and matching DICOM image file to all contour files."""
import os
import random

import glob
import pandas as pd
import re

import parsing
import util

_DICOM_FILE_GLOB = "*.dcm"
_I_CONTOUR_GLOBS = "i-contours/*.txt"

"""Represents a single datapoint."""
class DataPoint(object):
    def __init__(self, dicom_path, contour_path, dicom_image, contour_image):
        self.dicom_path = dicom_path
        self.contour_path = contour_path
        self.dicom_image = dicom_image
        self.contour_image = contour_image   
    
    def is_valid(self):
        """Placeholder validate function for subclasses to override."""
        return True

"""Represents a dataset determined by a 'link.csv' file. Can be iterated indefinitely."""
class Dataset(object):   
    def __init__(self, shuffle_data, return_indefinitely):
        self._data_points = []
        
        # Whether each epoch should have different shuffle of the data
        self.shuffle_data = shuffle_data
        
        # Whether to return datapoints indefinitely
        self.return_indefinitely = return_indefinitely
       
    def _add_datapoints_for_patient(self, dicom_files, contour_files):
        """Match available contour files to dicom files to add an datapoint.
        
        :param dicom_files: list of all dicom files.
        :param contour_files: list of all contour files.
        """   
        dicom_id_to_contour_file = dict()
        for contour_file in contour_files:
            dicom_id = util.extract_dicom_id_from_contour_filepath(contour_file)
            if dicom_id == -1:
                continue
            dicom_id_to_contour_file[dicom_id] = contour_file
        for dicom_file in dicom_files:
            dicom_id = util.extract_dicom_id_from_dicom_filepath(dicom_file)
            if dicom_id == -1:
                continue
                
            # Check if there is a matching contour file with the dicom id.
            # Create a datapoint if there is.
            if dicom_id in dicom_id_to_contour_file:
                contour_file = dicom_id_to_contour_file[dicom_id]
                contour_list = parsing.parse_contour_file(contour_file)
                if not contour_list:
                    continue
                dicom_data = parsing.parse_dicom_file(dicom_file)
                if not dicom_data or 'pixel_data' not in dicom_data:
                    continue
                dicom_image = dicom_data['pixel_data']
                
                try:
                    mask = parsing.poly_to_mask(contour_list, dicom_image.shape[1],
                                                dicom_image.shape[0])
                except parsing.MaskConversionError:
                    mask = None
                if mask is None:
                    continue
                new_data = DataPoint(dicom_file, contour_file, dicom_image, mask)
                if new_data.is_valid():
                    self._data_points.append(new_data)
                
    
    def parse_from_csv(self, link_csv, dicom_dir, contour_dir):
        """Parses a dataset by matching dicom files to contour files.
        
        :param link_csv: filepath of csv that matches patient_id to original_id.
        :param dicom_dir: directory of all dicom files.
        :param contour_dir: directory of all contour files.
        """
        dicom_to_contour = pd.read_csv(link_csv, sep=',')
        for index, row in dicom_to_contour.iterrows():
            patient_id = row['patient_id']
            original_id = row['original_id']
            all_dicom_files = glob.glob(os.path.join(dicom_dir, patient_id, _DICOM_FILE_GLOB))
            all_contour_files = glob.glob(os.path.join(contour_dir, original_id, _I_CONTOUR_GLOBS))
            if not all_dicom_files or not all_contour_files:
                continue
            self._add_datapoints_for_patient(all_dicom_files, all_contour_files)
    
    def size(self):
        """Returns size of the dataset."""
        return len(self._data_points)
    
    def _shuffle(self):
        """Shuffles the data points."""
        random.shuffle(self._data_points)
    
    def _reset(self):
        """Resets the iterator."""
        self._count = 0
        if self.shuffle_data:
            self._shuffle()
            
    def __iter__(self):
        """Resets the count, returns self which is an iterator."""
        self._reset()
        return self
    
    def __next__(self):
        """Iterates through the dataset.
        
        Will iterate indefinitely if return_indefinitely is True. Will shuffle
        every epoch is shuffle_data is true.
        """
        if not self._data_points:
            raise StopIteration
        if self._count == len(self._data_points):
            if self.return_indefinitely:
                self._reset()
            else:
                raise StopIteration
        datapoint = self._data_points[self._count]
        self._count+=1
        return datapoint
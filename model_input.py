import numpy as np

import parsing

class ModelInput(object):
    def __init__(self, dataset, batch_size):
        self._dataset_iter = iter(dataset)
        self._batch_size = batch_size
        
    def get_input(self):
        """Returns the training image and segmentation map.

        :return: A tuple used for training with the following
                  [batch_size, image_width, image_height] numpy array of the image
                  [batch_size, contour_image_width, contour_image_height] numpy array of contour file
        """
        batch_image = []
        batch_contour = []
        for i in range(self._batch_size):
            datapoint = next(self._dataset_iter)
            batch_image.append(datapoint.dicom_image)
            batch_contour.append(datapoint.contour_image)
        return np.stack(batch_image), np.stack(batch_contour)
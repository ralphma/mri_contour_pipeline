import pytest
from unittest.mock import MagicMock
import numpy as np

import dataset
import model_input

class TestCorrectModelInput(object):
    def test_correct_output(self):
        """Tests the the datapoints are flattened and combined into a single batch arrays."""
        a = dataset.DataPoint("a", "b", np.array([[1,2],[3,4]]), np.array([[True,False],[False,True]]))
        b = dataset.DataPoint("c", "d", np.array([[10,20],[30,40]]), np.array([[False,False],[False,False]]))
        input_data = MagicMock()
        input_data.__iter__.return_value = [a, b]
        input_queue = model_input.ModelInput(input_data, batch_size=2)
        x, y = input_queue.get_input()
        assert np.array_equal(x, np.array([[[1,2],[3,4]],[[10,20],[30,40]]]))
        assert np.array_equal(y, np.array([[[True,False],[False,True]],[[False,False],[False,False]]]))
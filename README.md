## Overview ##  
This data processing pipeline contains the following libraries  
  
1. `parsing.py` - mostly provided code that handles parsing dicom and contour files.  
1. `dataset.py` - handles parsing a dataset from a link.csv and dataset directory. Implemented as an iterable that can be iterated infinitely and supports shuffling.  
1. `model_input.py` - given a dataset, handles the batching by iterating over the dataset.  
  
To get an infinite stream of (x,y) training, use the following snippet  
  
```python  
import dataset  
import model_input  
data = dataset.Dataset(shuffle_data=True, return_indefinitely=True)  
data.parse_from_csv(link_csv="final_data/link.csv",   
 dicom_dir="final_data/dicoms",   
 contour_dir="final_data/contourfiles")  
input_runner = model_input.ModelInput(dataset=data, batch_size=8)  
x, y = input_runner.get_input()  
```  
  
I included the python notebook `dicom_image_pipeline_exploration.ipynb` which shows all pytests passing, loading of the data, and visualization of sample batches.  
  
To test run `pytest -v` from main directory.  
  
# Phase 1 #  
## Part 1 ##  
### How did you verify that you are parsing the contours correctly? ###  
In order to make sure the contours are parsed correctly, I added unit tests both for the code for parsing each individual contour and dicom files, but also for matching contour files to dicom files. Please see `parsing_test.py` and `dataset_test.py` which have documentation inside. Also, visualizing the images in the ipython notebook helped me verify that the contours match the blood pool in the decom image.   
  
A possible next step would be to add data validation tests that make sure the contour files are correctly formatted. This would make sure the vertices of the polygon are in order such that a valid polygon is formed.  
  
### What changes did you make to the code, if any, in order to integrate it into our production code base? ###  
For the parsing code, I changed very little. I added checks for existence of files being passed into `parse_contour_file` and `parse_dicom_file`. As for `poly_to_mask`, I added some checks for the validity of the polygon. If the polygon is not valid, an MaskConversionError is thrown.  
  
For the matching of dicom and contour files, I created the Dataset class which handles parsing from a link csv (see usage above). It stores the data as `DataPoint` which has matching dicom path, contour path and the processed images. To make sure the module work, I created unit tests using pytest to test the component.  
  
## Part 2 ##  
### Did you change anything from the pipelines built in Parts 1 to better streamline the pipeline built in Part 2? If so, what? If not, is there anything that you can imagine changing in the future? ###  
To make part 2 easier, I implemented `Dataset` class as an iterable that can iterate indefinitely. The main design decision here is whether the image files should be parsed while initially loading up the `Dataset` or by the individual `ModelInput` input runner when loading a batch.   
  
1. Design 1 (the one I went with): `Dataset` matches contour to dicom files. Loads the files and store the image in memory. `ModelInput` then receive the images directly when iterating the dataset.  
1. Design 2: `Dataset` matches contour to dicom files and store the filepaths in memory. When loading batches, `ModelInput` get the paths and can then load the images.  
  
Advantages of design 1:  
1. Images do not have to be parsed again every epoch, which wastes IO time.   
  
Disadvantages of design 1:  
1. When the dataset gets bigger, all the images will no longer be able to fit in memory. At this point design 2 will still support a full shuffle of the dataset (since it would still be possible to store all the filenames in memory).  
  
A future improvement would be for `Dataset` to match dicom and contour, parse the matching images, and then save all the `DataPoint` to disk. This solves not being able to store all `DataPoint` in memory. Then when iterating over the dataset, `Dataset` can then load `DataPoint` from disk. To support shuffling, `Dataset` will need a shuffle pool which determines how many `DataPoint` to load and shuffle at once. Greater the shuffle pool, the better the shuffling.   
  
### How do you/did you verify that the pipeline was working correctly? ###  
Through unit tests in `dataset_test.py` and `model_input_test.py`. Also ran on the final_data given (see `dicom_image_pipeline_exploration.ipynb`).  
  
### Given the pipeline you have built, can you see any deficiencies that you would change if you had more time? If not, can you think of any improvements/enhancements to the pipeline that you could build in? ###  
One improvement I can make is to speed up the batching. Currently, batching is done by iterating one by one through the dataset and stacking the numpy image arrays. Retrieving batch-size chunks from the dataset could be faster if the entire dataset is stored as a single numpy array or a pandas table. I decided to store each pair of images as `DataPoint` to set up an object oriented design so future data point classes can subclass `DataPoint` and override the `is_valid` function. Then `Dataset` can work with different types of `DataPoint`.   
  
Also in terms of speed, Dataset can use multiple threads for `parse_form_csv` since each (patient_id, original_id) pair can be handled by a different thread. In the code, each thread can run a separate `_add_datapoints_for_patient` with proper locking mechanism on `self._data_points`.   
  
# Phase 2 #  
## Part 1 ##  
My code from phase 1 can already handle matching of dicom files to contour files. The only part I needed to change was the hard coding of the contour file directory.  I made this change by treating the `contour_file_glob` as an input for initializing datasets. With that change, I am able to load a `Dataset` with all the o-contour.

In Part 2 of this problem, I need to match corresponding i-contour and o-contour images. In my design, the easiest way to do this is to allow joining of an i-contour `Dataset` and an o-contour `Dataset` based on the dicom_path that the contour files are related to. To support this, I added a `as_panda_dataframe` function to `Dataset` that allows the `Dataset` to be returned as a Pandas dataframe indexed by dicom_path (added corresponding unit test). This allows easy joining of two `Dataset` as illustrated in Part 2 and `LV_analysis.ipynb`. 
  
## Part 2 ##
For my analysis of the Heuristic based LV Segmentation, please see `LV_analysis.ipynb`. I added inline notes that explain how I generated the appropriate threshold, how I evaluated the method, and how I improved upon the basic heuristic method. With my heuristics, I achieved a mean intersection over union (MIOU) of .72 over the dataset.

With a large amount of data, we can pose this as a supervised learning problem and leverage CNNs. The learning task would be a binary classification of each pixel. The input of the model can be the H x W MRI image and the output would be H x W boolean mask of where the blood pool should be. For the architecture, we can use [U-Net]([https://arxiv.org/abs/1505.04597](https://arxiv.org/abs/1505.04597))  - need to resize input image to 512x512. I found a [Keras U-Net implementation]([https://github.com/zhixuhao/unet](https://github.com/zhixuhao/unet)) that would work pretty easily with my implementation of `Dataset`. For training, it seems like pixel-wise cross entropy loss or dice loss would work. 

If availability of data is a problem, it might be useful to employ transfer learning by warm-starting the model based on U-Net trained on other datasets. Also, data augmentation can be employed by rotation/scaling of the existing dataset to generate more data.

Finally, if o-contour data is already available, we would want to incorporate it. We can incorporate it as a post processing, filtering out model predictions that lie outside the o-contour. A better technique would be to incorporate the o-contour data as input features. We can concat the boolean mask of the o-contour as another channel of the initial input data. This makes warm-starting harder, as the filters of the first layer would have different sizes than before. However, the o-contour channel will help the model better localize the blood pool.

| Advantages of Deep Learning       | Disadvantages of Deep Learning           
| ------------- |:-------------:| 
| Accuracy - On most segmentation benchmarks, the best model has employed deep learning.     | Data - Deep learning models require an abundance of data in order to train. That might not be available. As seen in my exploration, simple heuristics can achieve pretty good accuracy with little training data.
| Transfer - Weights/Embeddings trained in a segmentation model can be used for other learning tasks. For instance, if we later want to find the different structures in the heart (object detection), we can reuse intermediate-layers of our segmentation model      | Speed/Resources - Training a deep learning model requires a lot of computation power compare to heuristics. Also, heuristics (such as thresholding) may be much faster during inference time. 

One additional note is that the deep learning model might be harder to debug if something goes wrong. Understanding why a pixel is classified a certain way is much easier with explicit heuristics that can be examined. CNNs are often blackboxes - although there has been a lot recent pushes into model interpretability.



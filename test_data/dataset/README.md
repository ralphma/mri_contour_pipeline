## Test Dataset
This is a test dataset file structure that is used for unit testing parsing code. `link.csv` matches up patient **DC-3** and original id **AB-2**. There are other patients and original id in *dicoms* and *contours* respectively for testing purposes. In `dicoms/DC-3` and `contours/AB-2/i-contours`, the following pairs have the same dicom id.

1. 10.dcm - IM-0001-0010-icontour-manual.txt
1. 100.dcm - IM-0001-0100-icontour-manual.txt
1. 101.dcm - IM-0001-0101-icontour-manual.txt

`10.dcm` and `IM-0001-0010-icontour-manual.txt` are empty files, so should be invalidated. Thus there should only be 2 valid data points when this test directory and link csv is loaded.
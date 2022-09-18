# EXIFtoKMZ
Python script created for my DFS-510 Course at Champlain College. Just a simple script to take a folder of images and create a KMZ file from the EXIF metadata. The KMZ file could assist in visualizing and creating a timeline from the images.

![Screenshot of EXIFtoKMZ Output](https://github.com/ogmini/EXIFtoKMZ/raw/main/Screenshot.PNG)

## Requirements
- Python 3.x
- exif 1.3.5 (https://pypi.org/project/exif/)
- Google Earth Pro/KMZ Viewer

## EXIF Metadata
Parses and displays the following:
- GPS Date
- GPS Time
- GPS Longitude
- GPS Latitude
- GPS Altitude
- Datetime Original
- Datetime Digitized
- Device Make
- Device Model

## Example Command
EXIFtoKMZ.py -d "\path\to\images" -o "\output\path\out.kmz"

## Possible Enhancements
- Expansion on EXIF Metadata that is parsed
- Change EXIF library
- Output CSV file 
- More customized icons on the KMZ file indicating starting photo
- Expand to support other files that contain GPS Metadata

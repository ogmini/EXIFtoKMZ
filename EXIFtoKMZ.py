'''
OG Mini
August 23, 2022
Final Project - EXIF to KMZ Parser 
Version 1.0
DFS 510 - Digital Forensics

Purpose:
This program will extract and parse the EXIF data from images in a given folder. This information will
be written to a KMZ file that can be opened in Google Earth. The map will display pins of where the images
where taken. Each pin has details showing the image and all timestamps associated with the image. A lined
path will also be shown between the pins showing the progression of photos.

This script can be useful in creating a timeline of photos mapped to their GPS coordinates. The photos could
be compared to the geography around the location on Google Earth and assist in locating more evidence.

Test Photos obtained from:
https://github.com/ianare/exif-samples/tree/master/jpg/gps

'''

import os
import argparse
from zipfile import ZipFile
from dataclasses import dataclass
from datetime import datetime
from math import trunc
from math import ceil

try:
    from exif import Image
    exif = True
except:
    print("EXIF Library Not Installed - run 'pip install exif'")
    exif = False

# dataclass object to store EXIF data and image    
@dataclass
class ImageEXIF:
    fileName: str
    descLong: str
    gpsTimestamp: str
    gpsLongitude: float
    gpsLatitude: float
    gpsAltitude: float
    

# Class to process images 
class ImageReader:
    def __init__(self, rootPath):
        self.rootPath   = os.path.abspath(rootPath)
        self.resultList = []
        self.imagesProcessedCount = 0
    
    # Read in images from folder
    def ProcessImages(self):
        for root, dirs, files in os.walk(self.rootPath):
            for nextFile in files:
                fullPath = os.path.join(root, nextFile)
                result = self.ExamineImage(fullPath)

                if result is True:
                    self.imagesProcessedCount += 1
        
        return self.resultList
    
    # Check file for EXIF Data. Process it and add information to be processed later. Returns True is successful                   
    def ExamineImage(self, theFile):
        if os.path.exists(theFile):
            if not os.path.islink(theFile):
                if os.path.isfile(theFile):
                    with open(theFile, 'rb') as imgFile:
                        imgExif = Image(imgFile)
                    
                    if (imgExif.has_exif):
                        fileName = os.path.split(theFile)[1]

                        # Format expected by KML file for timestamp 2007-01-14T21:05:02Z                   
                        dObj = datetime.strptime(imgExif.get('gps_datestamp', '1900:1:1') + ' ' 
                                                 + str(trunc(imgExif.get('gps_timestamp', (0,0,0))[0])) + ':' 
                                                 + str(trunc(imgExif.get('gps_timestamp', (0,0,0))[1])) + ':' 
                                                 + str(ceil(imgExif.get('gps_timestamp', (0,0,0))[2])), 
                                                 '%Y:%m:%d %H:%M:%S')
                        gpsTimestamp = dObj.strftime('%Y-%m-%dT%H:%M:%SZ')

                        # Equation to convert Degrees Minutes Seconds to Decimal Degrees for KML DD = d + (min/60) + (sec/3600)
                        # Convert Longitude
                        gpsDMSLong = imgExif.get('gps_longitude', (0,0,0))                        
                        gpsDDLong = gpsDMSLong[0] + (gpsDMSLong[1]/60) + (gpsDMSLong[2]/3600)
                        longRef = 1
                        if (imgExif.get('gps_longitude_ref', 'E') == 'W'):
                            longRef = -1
                        gpsLongitude = longRef * gpsDDLong

                        # Convert Latitude
                        gpsDMSLat = imgExif.get('gps_latitude', (0,0,0))
                        gpsDDLat = gpsDMSLat[0] + (gpsDMSLat[1]/60) + (gpsDMSLat[2]/3600)
                        latRef = 1
                        if (imgExif.get('gps_latitude_ref', 'N') == 'S'):
                            latRef = -1;                           
                        gpsLatitude = latRef * gpsDDLat
                        
                        # Altitude
                        gpsAltitude = imgExif.get('gps_altitude', 0)
                        
                        # HTML Description
                        # Display the three possible timestamps
                        dateTimeOriginal = imgExif.get('datetime', 'N/A')
                        dateTimeDigitized = imgExif.get('datetime_digitized', 'N/A')
                        dateGPS = imgExif.get('gps_datestamp', 'N/A') 
                        timeGPS = imgExif.get('gps_timestamp', 'N/A')
                        deviceMake = imgExif.get('make', 'N/A')
                        deviceModel = imgExif.get('model', 'N/A')
                        if (timeGPS != 'N/A'):
                            timeGPS = str(trunc(imgExif.get('gps_timestamp', (0,0,0))[0])) + ':' + str(trunc(imgExif.get('gps_timestamp', (0,0,0))[1])) + ':' + str(ceil(imgExif.get('gps_timestamp', (0,0,0))[2]))                        
                        descLong = '<hr><p>Device Information</p><ul><li>Make - ' + deviceMake + '</li><li>Model - ' + deviceModel + '</li></ul><p>Image Timestamps</p><ul><li>Datetime Original - ' +  dateTimeOriginal + '</li><li>Datetime Digitized - ' + dateTimeDigitized + '</li><li>Date GPS - ' + dateGPS + '</li><li>Time GPS - ' + str(timeGPS) + '</li></ul>' 

                        # Add information to list
                        exifData = ImageEXIF(fileName, descLong, gpsTimestamp, gpsLongitude, gpsLatitude, gpsAltitude)
                        self.resultList.append(exifData)
                        return True
                    else:
                        print(theFile, 'Skipped no EXIF data')
                        return False
                else:
                    print(theFile, 'Skipped NOT a File')
                    return False
            else:
                print(theFile, 'Skipped Link NOT a File')
                return False
        else:
            print(theFile, 'Path does NOT exist')        
            return False                
    
    

# Class to create KML file   
class KMLExporter:
    def __init__(self, imageList):
        self.resultList = imageList
    
    # Creates KML File from the Image List        
    def KMLExport(self, fileName):
        try:
            with open(fileName, 'w') as outFile:
                # List to store coordinates for path
                coordPathList = []
                
                # Start XML
                outFile.write('<?xml version="1.0" encoding="UTF-8"?>\n')
                outFile.write('<kml xmlns="http://www.opengis.net/kml/2.2">\n')
                outFile.write('<Document>\n')
                outFile.write('<name>' + fileName + '</name>\n')
                
                # Style red line for path
                outFile.write('<Style id="redLine">')
                outFile.write('<LineStyle>')
                outFile.write('<color>ff0000ff</color>')
                outFile.write('<width>4</width>')
                outFile.write('</LineStyle>')
                outFile.write('</Style>')
                
                # Create individual placemark records from list sorted by gpsTimestamp
                for r in sorted(self.resultList, key=lambda itm: itm.gpsTimestamp): 
                    # Add coordinates to list for path
                    coordPathList.append(str(r.gpsLongitude) + ',' + str(r.gpsLatitude) + ',' + str(r.gpsAltitude))
                    
                    outFile.write('<Placemark>\n')
                    outFile.write('<name>' + r.fileName + '</name>\n')
                    # Format to handle HTML Description <![CDATA[<img style="max-width:500px;" src="files/DSCN0042.jpg">description]]>
                    descCDATA = '<![CDATA[<img style="max-width:500px;" src="images/' + r.fileName + '">' + r.descLong + ']]>' 
                    outFile.write('<description>' + descCDATA + '</description>\n')
                    outFile.write('<TimeStamp>\n')
                    outFile.write('<when>' + r.gpsTimestamp + '</when>\n') 
                    outFile.write('</TimeStamp>\n')
                    outFile.write('<Point>\n')
                    outFile.write('<coordinates>' + str(r.gpsLongitude) + ',' + str(r.gpsLatitude) + ',' + str(r.gpsAltitude) + '</coordinates>\n') #'-122.0822035425683,37.42228990140251,0' 
                    outFile.write('</Point>\n')
                    outFile.write('</Placemark>\n')
       
                # Create red path line showing progression of photos
                outFile.write('<Placemark id="track1">')
                outFile.write('<name>Photo Path</name>')
                outFile.write('<styleUrl>#redLine</styleUrl>')
                outFile.write('<LineString><coordinates>')
                outFile.write(','.join(coordPathList))
                outFile.write('</coordinates></LineString>')
                outFile.write('</Placemark>')
                
                # End XML
                outFile.write('</Document>\n')
                outFile.write('</kml>')
                print("\nKML Created: " + fileName + "\n")
        except Exception as err:
            print("Failed: KML File Save: ",str(err))           

# Class to create the KMZ file which is a zip file containing the KML and Assets such as the images
class KMZExporter:
    def __init__(self, rootPath, kmlPath):
        self.rootPath   = os.path.abspath(rootPath)
        self.kmlPath = os.path.abspath(kmlPath)
    
    def KMZExport(self):
        # https://developers.google.com/kml/documentation/kmzarchives
        # Zip KML together with Images to create a KMZ File
        with ZipFile(os.path.splitext(self.kmlPath)[0] + '.kmz', 'w') as zipKMZ:
            for root, dirs, files in os.walk(self.rootPath):
                for nextFile in files:
                    rootDir = 'images'
                    filePath = os.path.join(root, nextFile)
                    parentPath = os.path.relpath(filePath, self.rootPath)
                    arcName = os.path.join(rootDir, parentPath)
                    zipKMZ.write(filePath, arcName)
            zipKMZ.write(self.kmlPath, os.path.basename(self.kmlPath))
                                      
def CheckRootPathDirectory(rootPath):
    # Validate the path is a directory
    if not os.path.isdir(rootPath):
        raise argparse.ArgumentTypeError('Root Path does not exist')

    # Validate the path is readable
    if os.access(rootPath, os.R_OK):
        return rootPath
    else:
        raise argparse.ArgumentTypeError('Root Path is not readable')         
    

if __name__ == '__main__' and exif:
    # Check Arguments / Display help
    parser = argparse.ArgumentParser(description='Python EXIF to KMZ Parser v1.0 - This program will extract and parse the EXIF data from images in a given folder. This information will be written to a KMZ file that can be opened in Google Earth. The map will display pins of where the images where taken. Each pin has details showing the image and all timestamps associated with the image. A lined path will also be shown between the pins showing the progression of photos. (ogmini August 2022)')
    parser.add_argument('-d', '--rootPath', type= CheckRootPathDirectory,required=True, help="specify the root path for images. Example: C:\ImageFolder")
    parser.add_argument('-o', '--output', type= str, required=True, help="specify output KMZ filename. Example: MyMap.kmz")
    parsedArguments = parser.parse_args()     
    
    # Instantiate ImageReader Object
    print("Reading Images from: " + parsedArguments.rootPath)
    imageObject = ImageReader(parsedArguments.rootPath)
    
    
    # Process and Parse Images for EXIF Data
    # Instantiate KMLExporter Object
    kmlObject = KMLExporter(imageObject.ProcessImages())
    
    print("Images processed: " + str(imageObject.imagesProcessedCount))    
    outputFilename = os.path.splitext(parsedArguments.output)[0] + '.kml'
    
    # Create KML
    kmlObject.KMLExport(outputFilename)
    
    # Instantiate KMZExporter Object
    kmzObject = KMZExporter(parsedArguments.rootPath, outputFilename)
    
    # Create KMZ
    kmzObject.KMZExport()
    
    print("Process finished")


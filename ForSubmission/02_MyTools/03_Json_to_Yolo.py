#--------------------------------------------------------------------------------#
# Import necessary modules.
#--------------------------------------------------------------------------------#
import os
import json
import sys


#--------------------------------------------------------------------------------#
# Define Constants.
#--------------------------------------------------------------------------------#
IMAGE_FILE_EXT = ".jpg"
TEXT_FILE_EXT = ".txt"
IMAGE_WIDTH_PX = 1280
IMAGE_HEIGHT_PX = 720
CLASSES_FILE_NAME = 'classes.txt'
FLAG_RENAME_FILE = 1


#--------------------------------------------------------------------------------#
# Define Global Variables.
#--------------------------------------------------------------------------------#
# This is defined in 'bdd10k' documentation.
# But to reduce execution time, we would like to re-organize as follows:"
    # """
    # pedestrian
    # rider
    # other person'
            # >> 'Person': 0
    # car
    # truck
    # bus
    # train
    # motorcycle
    # bicycle
    # other vehicle
    # trailer
            # >> 'Vehicle': 1
    # traffic light
    # traffic sign
            # >> 'TrafficInfo': 2
    # """
# Objects =   {
                # 'pedestrian': 0, 
                # 'rider': 1,
                # 'car': 2,
                # 'truck': 3,
                # 'bus': 4,
                # 'train': 5,
                # 'motorcycle': 6,
                # 'bicycle': 7,
                # 'traffic light': 8,
                # 'traffic sign': 9,
                # 'other person': 10,
                # 'other vehicle': 11,
                # 'trailer': 12,
            # }


Objects =   {
                'pedestrian': 0, 
                'rider': 1,
                'car': 2,
                'truck': 3,
                'bus': 4,
                'train': 5,
                'motorcycle': 6,
                'bicycle': 7,
                'traffic light': 8,
                'traffic sign': 9,
                'trailer': 10,
                'other vehicle': 11,
                'other person': 12,
            }

MyObjects = {
                'Person': 0,
                'Vehicle': 1,
                'Transport': 2,
                'TrafficObject': 3,
                # 'TrafficLight': 3,
                # 'TrafficSign': 4,
            }

FileCounter = 0
DelCounter = 0


#--------------------------------------------------------------------------------#
# Manage Command Line Arguments.
#--------------------------------------------------------------------------------#
# Get the number of command line arguments.
# Always the file name is the first argument.
TotArgs = len(sys.argv)
print()
# print(TotArgs)
# print(sys.argv[1])
# print(sys.argv[2])
# print(sys.argv[3])

# Check the command line arguments.
if TotArgs != 4:
    print('Command line arguments are not matching. Please check the format.')
    print('Command: python 03_Json_to_Yolo.py <Image Folder Path> <Label File Path> <Folder name Containing Images or Json File Name without Extension>')
    print('Example: python 03_Json_to_Yolo.py "D:\bdd100k\images\seg_track_20\train" "D:\bdd100k\labels\box_track_20\train" "0000f77c-62c2a288"')
    print('Exiting .....')
    exit(0)

# Get the info from the command line arguments.
ImageFolderPath = sys.argv[1]
LabelFilePath = sys.argv[2]
ImageFolderName = sys.argv[3]

# Adjust the path.
ImageFolderPath = ImageFolderPath.replace('\\', '\\\\')
LabelFilePath = LabelFilePath.replace('\\', '\\\\')


#--------------------------------------------------------------------------------#
# Main Code.
#--------------------------------------------------------------------------------#
# Get the actual image file folder and the corresponding Json file name.
ImageFolder = ImageFolderPath + "\\\\" + ImageFolderName
LabelFile = LabelFilePath  + "\\\\" + ImageFolderName + '.json'
# print(ImageFolder)
# print(LabelFile)


# Get the list of image files in the path provided.
ImageFileList = [File for File in os.listdir(ImageFolder) if File.endswith(IMAGE_FILE_EXT)]
ImageFileList.sort(reverse=False)
# print(ImageFileList)
# print(len(ImageFileList))


# Open the Json file to read.
with open(LabelFile, 'r') as ReadFptr:  
  JsonList = json.load(ReadFptr)  

# print(JsonList)
# print(type(JsonList))
# print(len(JsonList))
# print(JsonList[0])
# print(type(JsonList[0]))


# Loop - Extract the data from the Json file.
for JsonListIdx in range(len(JsonList)):
    # # This if statement is to limit for one iteration during the development.
    # if JsonListIdx > 0:
        # # sys.exit(0)
        # break

    Level01Dict = JsonList[JsonListIdx]
    # print(type(Level01Dict))
    # print(Level01Dict.keys())
    # print(Level01Dict.values())
    # print(ImageFileList[JsonListIdx])
    # print(Level01Dict['name'])
    
    # Ensure that the actual image file name and the image file name specified in the Json file are matching.
    if ImageFileList[JsonListIdx] != Level01Dict['name']:
        print(ImageFileList[JsonListIdx])
        print(Level01Dict['name'])
        print('Image file and the corresponding name in the json file are not matching. Please check.')
        print('Exiting .....')
        exit(0)

    # File name for the text file whose primary file name matches with the
    # image file's primary file name and the secondary/extension file name is '.txt'.
    # This file is to write the data in YOLOv3 format i.e. object class, Center X, Center Y, Width and Height.
    TextFileName = ImageFileList[JsonListIdx][0:-4] + TEXT_FILE_EXT
    TextFileFullPath = ImageFolder + '\\\\' + TextFileName
    # print(TextFileFullPath)


    # Get the info regarding object detection.
    LabelsList = Level01Dict['labels']

    # print(LabelsList)
    # print(type(LabelsList))
    # print(len(LabelsList))
    # print("----------")
    # print(LabelsList[0])
    # print(type(LabelsList[0]))
    # print(len(LabelsList[0]))
    
    # In case, the image file do not have object detection info in the corresponding Json file, then:
    if len(LabelsList) == 0:
        """
        # There is a chance that some image files doesn't have objects that we would like to detect.
        # We have TWO options to manage such image files.
        # Option-1: Delete these image files, so that they will not be part of training/validation process.
        # Option-2: Keep these image files.
        # Both these options have pros and cons.
        # If we delete, we only loose these files but no other issues.
        # If we keep, we have to face two issues.
        # Issue-A: We can not leave these image files but need to create the corresponding text files.
        # As there is no object identification information, there will be nothing in these text files,
        # so these text files are '0' byte files. Both '0' byte text file or no text file corresponding
        # to an image file will create errors during 'darknet' compilation process.  To avoid the
        # compilation errors, we need to write a simple space character into these text files so these
        # text files become '1' byte files and avoid compilation errors.
        # Issue-B: When we open the directory containing both the image and the corresponding text files
        # in 'LabelImg' tool, the '0' byte or '1' byte text files will create errors and make the
        # 'LabelImg' application closes itself.
        # Note: Do not write any new line character in the text files.
        """
        # If the flag is set then remove the image files which doesn't have
        # object detection info in the corresponding Json file.
        if FLAG_RENAME_FILE:
            SrcFileFullPath = ImageFolder + "\\\\" + ImageFileList[JsonListIdx]
            DstFileFullPath = ImageFolder + "\\\\" + "Unused_" + ImageFileList[JsonListIdx]
            # print(FileFullPath)
            
            # Remove the file specified.
            # os.remove(FileFullPath)
            # Rename the file which is not having object detection info.
            os.rename(SrcFileFullPath, DstFileFullPath)
            
            # Display Process.
            print("{:s} << {:s}".format(ImageFileList[JsonListIdx], "Renamed the file"))

            # Decrease the counter regarding the 'number of text files created' to display at the end.
            FileCounter -= 1
            
            # Increase the counter regarding the 'number of image files deleated' to display at the end.
            DelCounter += 1
        else:
            # Open the Text file to write.
            WriteFptr = open(TextFileFullPath, 'w')

            # Write a space character into the text file.
            WriteFptr.write(' ')
            
            # Display Process.
            print("{:s} << {:s}".format(TextFileName, "Space character"))

            # Close the Text file after write operation.
            WriteFptr.close()
    else:
        # Open the Text file to write.
        WriteFptr = open(TextFileFullPath, 'w')

        # Sub-Loop.
        for LabelsListIdx in range(len(LabelsList)):
            Level02Dict = LabelsList[LabelsListIdx]
            # print(Level02Dict.keys())
            # print(Level02Dict.values())
            # print("----------")
            
            Id = Level02Dict['id']
            Category = Level02Dict['category']
            Box2D = Level02Dict['box2d']
            # print(Id)
            # print(type(Id))
            # print(Category)
            # print(type(Category))
            # print(Objects[Category])
            # print(Box2D)
            # print(type(Box2D))
            # print(Box2D['x1'])
            # print("----------")

            # X, Y values of the Bounding Box Center.
            Box2D_Center_X = (Box2D['x1'] + Box2D['x2']) / 2
            Box2D_Center_Y = (Box2D['y1'] + Box2D['y2']) / 2
            # Width, Height values of the Bounding Box.
            Box2D_Width = Box2D['x2'] - Box2D['x1']
            Box2D_Height = Box2D['y2'] - Box2D['y1']
            
            # Normalized X, Y values of the Bounding Box Center.
            Box2D_Center_X /= IMAGE_WIDTH_PX
            Box2D_Center_Y /= IMAGE_HEIGHT_PX
            # Normalized Width, Height values of the Bounding Box.
            Box2D_Width /= IMAGE_WIDTH_PX
            Box2D_Height /= IMAGE_HEIGHT_PX
            
            # print(Objects[Category])
            # print(Box2D_Center_X)
            # print(Box2D_Center_Y)
            # print(Box2D_Width)
            # print(Box2D_Height)
        
            # Change the detection object classification from 'bdd10k' documentation format to our own format.
            if 0 <= Objects[Category] <= 1:
                ObjCat = 0
            elif 12 <= Objects[Category] <= 12:
                ObjCat = 0
            elif 2 <= Objects[Category] <= 3:
                ObjCat = 1
            elif 6 <= Objects[Category] <= 7:
                ObjCat = 1
            elif 10 <= Objects[Category] <= 11:
                ObjCat = 1
            elif 4 <= Objects[Category] <= 5:
                ObjCat = 2
            elif 8 <= Objects[Category] <= 8:
                ObjCat = 3
            elif 9 <= Objects[Category] <= 9:
                ObjCat = 3

            # Prepare the data in YOLOv3 format.
            # '.6f' is because the 'LabelImg' tool uses 6 decimal points.
            DataString = str(ObjCat) + ' ' + \
                         str("{:.6f}".format(Box2D_Center_X)) + ' ' + \
                         str("{:.6f}".format(Box2D_Center_Y)) + ' ' + \
                         str("{:.6f}".format(Box2D_Width)) + ' ' + \
                         str("{:.6f}".format(Box2D_Height)) + ' ' + \
                         "\n"

            # Write the data in YOLOv3 format into the text file.
            WriteFptr.write(DataString)

            # Display Process.
            print("{:s} << {:s}".format(TextFileName, DataString), end ="")

        # Close the Text file after write operation.
        WriteFptr.close()


    # Increase the counter regarding the 'number of text files created' to display at the end.
    FileCounter += 1
    print()

# Prepare the 'classes.txt' file.
ClassesFileFullPath = ImageFolder + '\\\\' + CLASSES_FILE_NAME
# print(ClassesFileFullPath)
# print(Objects.keys())

# Open the classes.txt file to write.
with open(ClassesFileFullPath, 'w') as ClsWriFptr:
    # Get all the key values of the dictionary i.e. class names of the objects.
    # for Class in Objects.keys():
    for Class in MyObjects.keys():
        # Write the data in YOLOv3 format into the text file.
        ClsWriFptr.write(Class + "\n")

print()
print("Number of image files deleted because of the non availability of json data: {:03d}".format(DelCounter))
print("Number of text files created corresponding to the remaining image files   : {:03d}".format(FileCounter))
print("Total file should be in the folder at the end of the execution            : {:03d}".format((FileCounter * 2) + 1))

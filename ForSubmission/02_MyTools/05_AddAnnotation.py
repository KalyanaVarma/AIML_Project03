#--------------------------------------------------------------------------------#
# Import necessary modules.
#--------------------------------------------------------------------------------#
import os
import sys


#--------------------------------------------------------------------------------#
# Define Global Variables.
#--------------------------------------------------------------------------------#
AddiFileList = list()


#--------------------------------------------------------------------------------#
# Define Constants.
#--------------------------------------------------------------------------------#
TEXT_FILE_EXT = ".txt"
CLASSES_FILE_NAME = 'classes.txt'
TEXT_NULL = ''


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
# print(sys.argv[4])

# Check the command line arguments.
if TotArgs != 5:
    print('Command line arguments are not matching. Please check the format.')
    print('Command: python 05_AddAnnotation.py <Main Annotation Files Folder Path> <Additional Annotation Files Folder Path> <Object Class Number to Find> <Object Class Number to Replace>')
    print('Example: python 05_AddAnnotation.py "D:\bdd100k\images\seg_track_20\train" "D:\bdd100k\labels\box_track_20\train" "0" "3"')
    print('Exiting .....')
    exit(0)

# Get the info from the command line arguments.
MainFolderPath = sys.argv[1]
AddiFolderPath = sys.argv[2]
ObjClassToFind = sys.argv[3]
ObjClassToRepl = sys.argv[4]

# Adjust the path.
MainFolderPath = MainFolderPath.replace('\\', '\\\\')
AddiFolderPath = AddiFolderPath.replace('\\', '\\\\')


#--------------------------------------------------------------------------------#
# Main Code.
#--------------------------------------------------------------------------------#
# Get the list of Main Annotation files in the path provided.
MainFileList = [File for File in os.listdir(MainFolderPath) if File.endswith(TEXT_FILE_EXT)]
# Sort the list in assending order.
MainFileList.sort(reverse=False)
# Remove the last element i.e. 'classes.txt' file because we need only the annotation files.
if MainFileList[-1] == CLASSES_FILE_NAME:
    MainFileList.pop(-1)
# print(MainFileList)
# print(len(MainFileList))

# Get the list of Additional Annotation files in the path provided.
TempFileList = [File for File in os.listdir(AddiFolderPath) if File.endswith(TEXT_FILE_EXT)]
# Sort the list in assending order.
TempFileList.sort(reverse=False)
# Remove the last element i.e. 'classes.txt' file because we need only the annotation files.
if TempFileList[-1] == CLASSES_FILE_NAME:
    TempFileList.pop(-1)
# print(TempFileList)
# print(len(TempFileList))

# Match the Additional Annotation files list with the Main Annotation files list.
# Main Annotation files list is sequential and fixed, but Additional Annotation files list may contain
#   files with some gap (or) files matching at the beginning (or) files matching at the ending and so on.
#   The reason is that, not all the images have the additional annotation info for example, TrafficLight.
#   In such a case, the text files corresponding to those images will not be created.
for Idx, FileName in enumerate(MainFileList):
    if MainFileList[Idx] in TempFileList:
        AddiFileList.append(MainFileList[Idx])
        # print("Added:", MainFileList[Idx], Idx)
    else:
        AddiFileList.append(TEXT_NULL)
        # print("Added: NULL", Idx)


# Check the Additional Annotation files list.  If it contains filename,
#   then we need to read the content of this file, and write the content
#   at the end of the corresponding Main Annotation file by Object identification
#   value as per the 'classes.txt' file in Main Annotation folder.  Both the source
#   and target object identification values are coming as the command line arguments.
for Idx, FileName in enumerate(AddiFileList):
    if len(AddiFileList[Idx]) == 0:
        print("File {:25s}: Skipped.".format(MainFileList[Idx]))
        # print(AddiFileList[Idx], Idx)
        continue
    else:
        # print(Idx)

        # Get the full paths.
        MainFolderPathFull = MainFolderPath + "\\\\" + MainFileList[Idx]
        AddiFolderPathFull = AddiFolderPath + "\\\\" + AddiFileList[Idx]

        # Open the Main Annotation text file to append.
        # Open the Additional Annotation text file to read.
        with open(MainFolderPathFull, 'a') as ApndFptr, \
             open(AddiFolderPathFull, 'r') as ReadFptr:
            for Line in ReadFptr:
                # Remove the '\n' at the end of the line.
                Line = Line.rstrip()
                
                # Split the line based on the space character.
                TempList = Line.split(' ')
                # print(TempList)
                # print(len(TempList))
                # print(type(TempList[0]))
                
                # Check the first element, which is the object identification value.
                # This value should be checked and changed.
                if TempList[0] != ObjClassToFind:
                    print("Error: Source object class is not matching.  Exiting.")
                    sys.exit(0)
                
                # Change the source object identification value with 
                #   targed object identification value as provided in the command line arguments.
                TempList[0] = ObjClassToRepl
                
                # Prepare the line with replaced object identification value.
                # Also add new line character.
                NewLine = ' '.join(TempList) + '\n'
                # print(NewLine)

                # Append this new line to the Main Annotation text file.
                ApndFptr.write(NewLine)

        print("File {:25s}: Updated.".format(MainFileList[Idx]))

print()
print("Files updated successfully.")

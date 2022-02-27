import cv2
import os
import sys
# import glob

# Frames per second.
FPS_VALUE = 30

# ==============
# import time


# Char0 = '\r|'
# Char1 = '\r/'
# Char2 = '\r-'
# Char3 = '\r\\'

# Flag = 0

# for Count in range(0, 10, 1):
    # if Count % 2 == 0 and not Flag:
        # print(Char0, end="")
        # print("Case1", Flag)
    # elif Count % 2 == 1 and not Flag:
        # print(Char1, end="")
        # Flag ^= 1
        # print("Case2", Flag)
    # elif Count % 2 == 0 and Flag:
        # print(Char2, end="")
        # print("Case3", Flag)
    # elif Count % 2 == 1 and Flag:
        # print(Char3, end="")
        # Flag ^= 1
        # print("Case4", Flag)
        
    # time.sleep(2)

# # for Count in range(0, 10, 1):
    # # print('\r0', end="")

# =============================================

# Get the number of command line arguments.
# Always the file name is the first argument.
TotArgs = len(sys.argv)
# print(TotArgs)
# print(sys.argv[0])
# print(sys.argv[-1])

if TotArgs < 2:
    print('Path not found in the command line arguments. Please provide the path.')
    print('Command: python 02_Frames_to_Video.py <File Path> [Frame File Extention] [Video File Extention]')
    print('Example: python 02_Frames_to_Video.py "C:\\MyDir" ".jpg" ".mov"')
    print('Exiting .....')
    exit(0)
elif TotArgs > 4:
    print("Too many command line arguments.")
    print('Command: python 02_Frames_to_Video.py <File Path> [Frame File Extention] [Video File Extention]')
    print('Example: python 02_Frames_to_Video.py "C:\\MyDir" ".jpg" ".mov"')
    print('Exiting .....')
    exit(0)


# Get the info from the command line parameters.
Path = sys.argv[1]
VideoFileExt = None
FrameFileExt = None

try:
    FrameFileExt = sys.argv[2]
    VideoFileExt = sys.argv[3]
except:
    pass


# Verify the info from the command line parameters.
Path = Path.replace('\\', '\\\\')
# print(Path)

if VideoFileExt == None:
    VideoFileExt = ".mov"

if FrameFileExt == None:
    FrameFileExt = ".jpg"

# print(VideoFileExt)
# print(FrameFileExt)


# Get the list of video files in the path provided.
# FrameFileList = os.listdir(Path, Endswith)
FrameFileList = [File for File in os.listdir(Path) if File.endswith(FrameFileExt)]
FrameFileList.sort(reverse=False)
# print(FrameFileList)


# Max. frame limit.
if len(FrameFileList) > 606:
    print("The maximum limit of the frames to process is 606, but given {} frames. Exiting.".format(len(FrameFileList)))
    sys.exit(0)


ImageList = list()

# Iterate the list for various things.
for FrameFile in FrameFileList:
    TempPath = Path + "\\\\" + FrameFile
    # print(TempPath)
    # Read the image from the Frame file.
    Image = cv2.imread(TempPath)
    # Extract Height, Width and Number of Color channels.
    Height, Width, Layers = Image.shape
    # Prepare a touple with Width first and Height. To be used when creating a video.
    Size = (Width,Height)
    # Note: This statement consumes lot of memory (RAM).
    #       When tried with 1280x720 frame size and 1211 frames,
    #       this 16 Gb RAM crashed.  But worked with 302 frames.
    ImageList.append(Image)


# print(Width)
# print(Height)
# print(Layers)

# Prepare the path and file name for the video file.
# Temp = FrameFile.split("_")
# TempPath = Path + "\\\\" + Temp[0] + "_" + Temp[1] + VideoFileExt
Temp = FrameFile.split("-")
TempPath = Path + "\\\\" + Temp[0] + "-" + Temp[1] + VideoFileExt
# print(TempPath)

# Size = (640,480)
# Define the codec and create VideoWriter object to save the video
# Video = cv2.VideoWriter(TempPath,cv2.VideoWriter_fourcc(*'DIVX'), FPS_VALUE, Size)
# fourcc = cv2.VideoWriter_fourcc(*'XVID')
# fourcc = cv2.VideoWriter_fourcc(*'MPEG')
# fourcc = cv2.VideoWriter_fourcc(*'MP4V')
# Video = cv2.VideoWriter(TempPath, fourcc, FPS_VALUE, Size)

# https://forums.developer.nvidia.com/t/python-what-is-the-four-characters-fourcc-code-for-mp4-encoding-on-tx2/57701/3
Video = cv2.VideoWriter(TempPath, 0x00000021, FPS_VALUE, Size)

# Iterate the list for various things.
for ImageIdx in range(len(ImageList)):
    # print(ImageIdx)
    Video.write(ImageList[ImageIdx])
    print("\rFrame #{:06d} written. Total {:06d} frames.".format(ImageIdx, len(FrameFileList)), end="")


print()    
print("Created the video file.")
Video.release()

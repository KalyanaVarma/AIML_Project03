import cv2
import os
import sys
# import glob

# Note: It is observed that for "BDD100K" data, the Frames Per Second (FPS) is 30.
#       In olden days, FPS was 24 i.e. 24 frames per second.
#       As the "BDD100K" data is huge w.r.t. size of video files as well as the
#       number of video files, it is finally decided that "6" is the best number
#       to manage old videos as well as "BDD100K" data files.  So taking every
#       6th frame of the videos of the "BDD100K" data.  Also observed that, 
#       taking every 6th frame is not showing any video jumping effect.

# Frames per second.
FPS_VALUE = 30
# KEY_NUMBER = 6
KEY_NUMBER = 1


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
    print('Command: python 01_Video_to_Frames.py <File Path> [Video File Extention] [Frame File Extention]')
    print('Example: python 01_Video_to_Frames.py "C:\\MyDir" ".mov" ".jpg"')
    print('Exiting .....')
    exit(0)
elif TotArgs > 4:
    print("Too many command line arguments.")
    print('Command: python 01_Video_to_Frames.py <File Path> [Video File Extention] [Frame File Extention]')
    print('Example: python 01_Video_to_Frames.py "C:\\MyDir" ".mov" ".jpg"')
    print('Exiting .....')
    exit(0)


# Get the info from the command line parameters.
Path = sys.argv[1]
VideoFileExt = None
FrameFileExt = None

try:
    VideoFileExt = sys.argv[2]
    FrameFileExt = sys.argv[3]
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
# VideoFileList = os.listdir(Path, Endswith)
VideoFileList = [File for File in os.listdir(Path) if File.endswith(VideoFileExt)]
VideoFileList.sort(reverse=False)
# print(VideoFileList)


# Iterate the list for various things.
for VideoFile in VideoFileList:
    TempPath = Path + "\\\\" + VideoFile[0:-4]
    # print(TempPath)

    # Create folder(s) with name as the video file name to keep the extracted frames of this particular video.
    if os.path.exists(TempPath):
        print("Path already exists!")
        exit(0)
    else:
        os.makedirs(TempPath)

        # Get the info of the video file.
        TempPath = Path + "\\\\" + VideoFile
        # print(TempPath)
        VideoCap = cv2.VideoCapture(TempPath)
        VideoCap.set(cv2.CAP_PROP_FPS, 5)
        # fps = int(VideoCap.get(5))
        # print("fps:", fps)

        if not VideoCap.isOpened(): 
            print("Unable to open the file:", TempPath)
            exit(0)

        VideoLength = int(VideoCap.get(cv2.CAP_PROP_FRAME_COUNT))
        VideoWidth  = int(VideoCap.get(cv2.CAP_PROP_FRAME_WIDTH))
        VideoHeight = int(VideoCap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        VideoFPS    = VideoCap.get(cv2.CAP_PROP_FPS)

        print()
        print("-------")
        print("Video :", TempPath)
        print("Length:", VideoLength)
        print("Wedth :", VideoWidth)
        print("Height:", VideoHeight)
        print("FPS   :", VideoFPS)
        print("-------")
        print()


        # Extract the frames of the video file into respective directory.
        # Read the video file.
        Success,Frame = VideoCap.read()
        Count = 1
        FileCount = 1

        while Success:
            # TempPath = Path + "\\\\" + VideoFile[0:-4] + "\\\\" + VideoFile[0:-4] + '_' + "Frame_" + "{:06d}".format(Count) + FrameFileExt    
            TempPath = Path + "\\\\" + VideoFile[0:-4] + "\\\\" + VideoFile[0:-4] + '-' + "{:07d}".format(FileCount) + FrameFileExt    

            # Condition-1: Consider the key frames only as destribed at the top of this file.
            if Count == 1 or Count % KEY_NUMBER == 0:
                # Save frame as image file of specified (FrameFileExt) format.
                cv2.imwrite(TempPath, Frame)
                # Status info.
                # print("\rFrame #{:06d} created. Total {:06d} frames.".format(Count, VideoLength), end="")
                print("\rFrame #{:07d} created.".format(FileCount), end="")
                
                # Manage image file name.                
                FileCount += 1


            # Read the video file.
            Success,Frame = VideoCap.read()

            # Manage the counter variable(s).
            Count += 1

        print()
        VideoCap.release()

print()
cv2.destroyAllWindows()

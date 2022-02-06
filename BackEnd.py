#--------------------------------------------------------------------------------#
# Import necessary modules.
#--------------------------------------------------------------------------------#
import io
import os
import sys
import time

import numpy as np

from cv2 import cv2
from fastapi import FastAPI
from fastapi import Request
from fastapi import File
from fastapi import UploadFile

from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles


#--------------------------------------------------------------------------------#
# Define Constants.
#--------------------------------------------------------------------------------#
IMAGE_FILE_EXT_JPG = ".jpg"
IMAGE_FILE_EXT_PNG = ".png"
VIDEO_FILE_EXT_MP4 = ".mp4"
INPUT_FILE_NAME = "InputFile"
OUTPUT_FILE_NAME = "OutputFile"

PATH_LABELS = "./SupportFiles/Static/classes.names"
PATH_CONFIG = "./SupportFiles/Static/yolov3_bdd100k_test.cfg"
PATH_WEIGHT = "./SupportFiles/Static/yolov3_bdd100k_train_last.weights"
CLEANUP_FOLDER = "./SupportFiles/Dynamic/"
CHAR_DASH = '-'

# RESIZE_IMG_TO = (640, 480)
RESIZE_IMG_TO = (1280, 720)

CONFIDENCE_THRESHOLD = 0.5
NMS_THRESHOLD = 0.1

COLOR_BLACK = (0, 0, 0)
COLOR_WHITE = (255, 255, 255)

# Frames per second.
FPS_VALUE = 30
# Verified maximum frame limit on the personal laptop.
MAX_FRAME_LIMIT = 606


#--------------------------------------------------------------------------------#
# Define Global Variables.
#--------------------------------------------------------------------------------#
# Object of FastAPI.
App = FastAPI()

# Templates.
Templates = Jinja2Templates(directory = "HTML")

# static/js/post.index js.Required to call from html.
App.mount("./SupportFiles", StaticFiles(directory="SupportFiles"), name="SupportFiles")


#--------------------------------------------------------------------------------#
# User Defined Functions (UDFs).
#--------------------------------------------------------------------------------#
def ProcessUserFile(UserFile):
  """
  # Function to process the file ONLY with specific extensions which is uploaded by the user.
  """

  # Prepare the binary data from the uploaded file.
  BinaryData = io.BytesIO(UserFile.file.read())
  BinaryDataArray = np.asarray(bytearray(BinaryData.read()), dtype=np.uint8)
  
  # File name and the relative path to save the file.
  FullPath = CLEANUP_FOLDER + INPUT_FILE_NAME + UserFile.filename[-4:]

  # Open the file in binary mode and write the binary data into the file.
  with open(FullPath, "wb") as BinaryFile:
      # Write binary bytes to the file.
      BinaryFile.write(BinaryDataArray)


  return FullPath


def DetectRoadObjects(InputFile):
  """
  # Function to get the road objects detected with bounding boxes.
  """
  
  # Local variable(s).
  LayerNameNeedList = list()
  
  # Initialize the lists of bounding boxes, confidences and class IDs respectively.
  BoundingBoxesList = list()
  ConfidencesList = list()
  ClassIDsList = list()


  # Read the image from the input file using 'cv2'.
  OriginalRgbColorImg = cv2.imread(InputFile)

  # Resize the image to a spefied size.
  ResizedRgbColorImg = cv2.resize(OriginalRgbColorImg, RESIZE_IMG_TO)

  
  # Get the labels as a list from the labels file.
  Labels = open(PATH_LABELS).read().strip().split("\n")
  
  # # To assign colors manually.
  # # Outer Array: Red for the 1st object, Green for the 2nd object and Blue for the 3rd object.
  # # Inner array is BGR because 'cv2' follows BGR system, but not RGB.
  # Colors = [[0, 0, 255], [0, 255, 0], [255, 0, 0]]
  
  # To assign colors randomly.
  # Initialize a list of colors to represent each possible class label.
  np.random.seed(42)
  Colors = np.random.randint(0, 255, size = (len(Labels), 3), dtype = "uint8")
  
  # Load YOLOv3 object detector trained on custom i.e. bdd100k dataset (Currently 3 classes i.e. Person, Vehicle, TrafficInfo).
  Network = cv2.dnn.readNetFromDarknet(PATH_CONFIG, PATH_WEIGHT)
  # Network = cv2.dnn.readNet(PATH_WEIGHT, PATH_CONFIG)


  # Get the image height and image width values from the resized color image.
  (ImgHeight, ImgWidth) = ResizedRgbColorImg.shape[:2]
  
  
  # Get all the *output* layer names that we have in YOLOv3.
  LayerNameFullList = Network.getLayerNames()

  # Find only the *output* layer names that we need from YOLOv3.
  # Detection layer: 82
  # Detection layer: 94
  # Detection layer: 106
  for Idx in Network.getUnconnectedOutLayers():
    LayerNameNeedList.append(LayerNameFullList[Idx - 1])
  

  # Construct a blob from the input image and then perform a forward pass of the
  # YOLO object detector, giving us our bounding boxes and associated probabilities.
  # blob = cv2.dnn.blobFromImage(image, scalefactor=1.0, size, mean, swapRB=True)
  Blob = cv2.dnn.blobFromImage(ResizedRgbColorImg, 1/255.0, (416, 416), swapRB=True, crop=False)
  Network.setInput(Blob)
  
  # Note down the start time.
  StartTime = time.time()
  LayerOutputs = Network.forward(LayerNameNeedList)
  # Note down the end time.
  EndTime = time.time()
  # Info = "YOLO took {:.6f} seconds".format(EndTime - StartTime)


  # Loop over each of the layer outputs.
  for Output in LayerOutputs:
    # Loop over each of the detections.
    for Detection in Output:
      # Extract the class ID and confidence (i.e., probability) of the current object detection.
      Scores = Detection[5:]
      ClassID = np.argmax(Scores)
      Confidence = Scores[ClassID]

      # Filter out weak predictions by ensuring that the detected
      # probability is greater than the thershold/minimum probability.
      if Confidence > CONFIDENCE_THRESHOLD:
        # Scale the bounding box coordinates back relative to the size of the image,
        # keeping in mind that YOLO actually returns the center (x, y) coordinates of the
        # bounding box followed by the boxes' width and height.
        Box = Detection[0:4] * np.array([ImgWidth, ImgHeight, ImgWidth, ImgHeight])
        (CenterX, CenterY, Width, Height) = Box.astype("int")

        # Use the center (x, y) coordinates to derive the top and left corner of the bounding box.
        x = int(CenterX - (Width/2))
        y = int(CenterY - (Height/2))

        # Update the lists of bounding boxes, confidences and class IDs.
        BoundingBoxesList.append([x, y, int(Width), int(Height)])
        ConfidencesList.append(float(Confidence))
        ClassIDsList.append(ClassID)

  # Apply non-maxima suppression to suppress weak, overlapping bounding boxes.
  Idxs = cv2.dnn.NMSBoxes(BoundingBoxesList, ConfidencesList, CONFIDENCE_THRESHOLD, NMS_THRESHOLD)

  # Ensure at least one detection exists.
  if len(Idxs) > 0:
    # Loop over the indexes we are keeping.
    for Idx in Idxs.flatten():
      # extract the bounding box coordinates
      (x, y) = (BoundingBoxesList[Idx][0], BoundingBoxesList[Idx][1])
      (w, h) = (BoundingBoxesList[Idx][2], BoundingBoxesList[Idx][3])

      Color = [int(c) for c in Colors[ClassIDsList[Idx]]]
      # Draw a bounding box rectangle over the object.
      cv2.rectangle(ResizedRgbColorImg, (x, y), (x + w, y + h), Color, 2)
      # Draw a box to display the object name and confidence.
      cv2.rectangle(ResizedRgbColorImg, (x, y-26), (x + 180, y), Color, -1)
      # Prepare the text of object name and confidence.
      # FONT_HERSHEY_SIMPLEX, FONT_HERSHEY_PLAIN, FONT_HERSHEY_DUPLEX, FONT_HERSHEY_COMPLEX
      # FONT_HERSHEY_TRIPLEX, FONT_HERSHEY_COMPLEX_SMALL, FONT_HERSHEY_SCRIPT_SIMPLEX, FONT_HERSHEY_SCRIPT_COMPLEX
      Text = "{}: {:.2f}".format(Labels[ClassIDsList[Idx]], ConfidencesList[Idx])
      cv2.putText(ResizedRgbColorImg, Text, (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.8, COLOR_BLACK, 2)


  # File name and the relative path to save the file.
  FullPath = CLEANUP_FOLDER + OUTPUT_FILE_NAME + InputFile[-4:]

  # Save the image file which is having the objects detected with bounding boxes.
  cv2.imwrite(FullPath, ResizedRgbColorImg)


  return FullPath


def ExtractFrameFromVideo(InputFile):
  """
  # Function to extract the frames from the given video file.
  """

  # Open the video file to extract frames.
  VideoCap = cv2.VideoCapture(InputFile)
  VideoCap.set(cv2.CAP_PROP_FPS, 5)

  if not VideoCap.isOpened(): 
    # print("Unable to open the file:", InputFile)
    FullPath = ".junk"
    return FullPath


  # Extract the frames of the video file into a specific folder.
  # Read the video file.
  Success, Frame = VideoCap.read()
  # Variable to generate file names for the images.
  FileCount = 1

  while Success:
    # Save frame as image file of specified (FrameFileExt) format.
    FullPath = CLEANUP_FOLDER + INPUT_FILE_NAME + CHAR_DASH + "{:07d}".format(FileCount) + IMAGE_FILE_EXT_JPG
    cv2.imwrite(FullPath, Frame)
    # print("\rFrame #{:07d} created.".format(FileCount), end="")
    
    # Manage image file names.
    FileCount += 1

    # Read the video file.
    Success, Frame = VideoCap.read()


  # Close the video file.
  VideoCap.release()


  return FullPath


def CreateVideoFromFrames(FrameFileOutputList):
  """
  # Function to create the video file from the frames.
  """

  # Local variable(s).
  ImageList = list()


  # Max. frame limit.
  if len(FrameFileOutputList) > MAX_FRAME_LIMIT:
    # print("The maximum limit of the frames to process is {}, but given {} frames. Exiting.".format(MAX_FRAME_LIMIT, len(FrameFileOutputList)))
    FullPath = ".junk"
    return FullPath


  # Loop through, to prepare a list of cv2 images.
  for FrameFile in FrameFileOutputList:
    FullPath = CLEANUP_FOLDER + FrameFile
    # Read the image from the Frame file.
    Image = cv2.imread(FullPath)
    # Extract Height, Width and Number of Color channels.
    Height, Width, Layers = Image.shape
    # Prepare a touple with Width first and Height. To be used when creating a video.
    Size = (Width,Height)
    # Note: This statement consumes lot of memory (RAM).
    #       When tried with 1280x720 frame size and 1211 frames,
    #       this 16 Gb RAM crashed.  But worked with 302 frames.
    ImageList.append(Image)


  # For output video file.
  FullPath = CLEANUP_FOLDER + OUTPUT_FILE_NAME + VIDEO_FILE_EXT_MP4
  # https://forums.developer.nvidia.com/t/python-what-is-the-four-characters-fourcc-code-for-mp4-encoding-on-tx2/57701/3
  Video = cv2.VideoWriter(FullPath, 0x00000021, FPS_VALUE, Size)

  # Iterate the list of cv2 images to create the video.
  for ImageIdx in range(len(ImageList)):
    Video.write(ImageList[ImageIdx])


  return FullPath


#--------------------------------------------------------------------------------#
# End Points.
#--------------------------------------------------------------------------------#
# GET option.
@App.get('/')
def root(request:Request):
  return Templates.TemplateResponse("FrontEnd_Input.html", context = {'request':request})


# POST option.
@App.post('/')
async def root(request:Request, UserFile: UploadFile = File(...)):
  # Clean-up the directory where we kept the processed files in previous execution.
  for FileName in os.listdir(CLEANUP_FOLDER):
      os.remove(os.path.join(CLEANUP_FOLDER, FileName))


  # Get the filename and  the file name extension of the uploaded file.
  UserFileName = UserFile.filename
  UserFileExtn = UserFileName[-4:]
  
  # Check the file extension to take appropriate action.
  if UserFileExtn == IMAGE_FILE_EXT_JPG or UserFileExtn == IMAGE_FILE_EXT_PNG:
    #--------------------------------------------------------------------------------#
    # Step-01.
    #--------------------------------------------------------------------------------#
    # If the user uploaded file is of specific type(s) then only process it.
    InputFile = ProcessUserFile(UserFile)
    # Check whether the specific file got created at the specific path or not.
    if not os.path.exists(InputFile):
      return {"Return":"File is NOT available."}


    #--------------------------------------------------------------------------------#
    # Step-02.
    #--------------------------------------------------------------------------------#
    # After confirming about the image file creation, send this file to get the road objects detected with bounding boxes.
    OutputFile = DetectRoadObjects(InputFile)
    # Check whether the specific file got created at the specific path or not.
    if not os.path.exists(OutputFile):
      return {"Return":"File is NOT available."}


    #--------------------------------------------------------------------------------#
    # Step-03.
    #--------------------------------------------------------------------------------#
    # Return the HTML page that can display the input and output images.
    return Templates.TemplateResponse("FrontEnd_OutputImage.html", context = {'request':request, "InputFile":InputFile, "OutputFile":OutputFile})
  elif UserFileExtn == VIDEO_FILE_EXT_MP4:
    #--------------------------------------------------------------------------------#
    # Step-01.
    #--------------------------------------------------------------------------------#
    # If the user uploaded file is of specific type(s) then only process it.
    InputFile = ProcessUserFile(UserFile)
    # Check whether the specific file got created at the specific path or not.
    if not os.path.exists(InputFile):
      return {"Return":"File is NOT available."}


    #--------------------------------------------------------------------------------#
    # Step-02.
    #--------------------------------------------------------------------------------#
    # Extract the frames from the uploaded video file of specific/allowed type.
    CheckFrameFile = ExtractFrameFromVideo(InputFile)
    # Check whether the specific file got created at the specific path or not.
    # Here, in success case, it is the image file i.e. the last frame of the video file.
    # in failure case, it is the name of a junk file.
    if not os.path.exists(CheckFrameFile):
      return {"Return":"File is NOT available."}


    #--------------------------------------------------------------------------------#
    # Step-03.
    #--------------------------------------------------------------------------------#
    # After confirming about the last image file creation, send all the image files one by one to get the road objects detected with bounding boxes.
    # First, get the sorted list of image files which are extracted from the input video file.
    FrameFileInputList = [File for File in os.listdir(CLEANUP_FOLDER) if File.endswith(IMAGE_FILE_EXT_JPG)]
    FrameFileInputList.sort(reverse=False)

    # Iterate the list for sending all the image files one by one to get the road objects detected with bounding boxes.
    for FrameFile in FrameFileInputList:
      InputFileFrame = CLEANUP_FOLDER + FrameFile
      OutputFile = DetectRoadObjects(InputFileFrame)
      # Check whether the specific file got created at the specific path or not.
      if not os.path.exists(OutputFile):
        return {"Return":"File is NOT available."}

      # Make the input image file name and output image file name are simular.
      Temp = InputFileFrame.split(CHAR_DASH)
      TempFileName = CLEANUP_FOLDER + OUTPUT_FILE_NAME + CHAR_DASH + Temp[1]
      os.rename(OutputFile, TempFileName)


    #--------------------------------------------------------------------------------#
    # Step-04.
    #--------------------------------------------------------------------------------#
    # Get ONLY the sorted list of image files having the road objects detected with bounding boxes using Python 'set' operations.
    FrameFileOutputList = [File for File in os.listdir(CLEANUP_FOLDER) if File.endswith(IMAGE_FILE_EXT_JPG)]
    FrameFileOutputList.sort(reverse=False)

    # Python set operations.
    FrameFileOutputList = list(set(FrameFileOutputList) - set(FrameFileInputList))
    FrameFileOutputList.sort(reverse=False)

    # Using the list of image files having the road objects detected with bounding boxes, create the output video file.
    OutputFile = CreateVideoFromFrames(FrameFileOutputList)
    # Check whether the specific file got created at the specific path or not.
    if not os.path.exists(OutputFile):
      return {"Return":"File is NOT available."}


    #--------------------------------------------------------------------------------#
    # Step-05.
    #--------------------------------------------------------------------------------#
    # Return the HTML page that can display the input and output videos.
    return Templates.TemplateResponse("FrontEnd_OutputVideo.html", context = {'request':request, "InputFile":InputFile, "OutputFile":OutputFile})
  else:
    return {"Return":"Unsupported File Selected."}


#--------------------------------------------------------------------------------#
# Main Code.
#--------------------------------------------------------------------------------#
# if __name__ == "__main__":

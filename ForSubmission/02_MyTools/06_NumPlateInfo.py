#--------------------------------------------------------------------------------#
# Import necessary modules.
#--------------------------------------------------------------------------------#
import sys
import cv2
import imutils
import pytesseract
import re
import numpy as np


#--------------------------------------------------------------------------------#
# Define Constants.
#--------------------------------------------------------------------------------#
RESIZE_IMG_TO = (640, 480)
MIN_THRESHOLD_CANNY = 10
MAX_THRESHOLD_CANNY = 200
STP_THRESHOLD_CANNY = 20
COLOR_BGR_BLUE = (255, 0, 0)
COLOR_BGR_GREEN = (0, 255, 0)
COLOR_BGR_RED = (0, 0, 255)
LINE_THICKNESS = 3
VEHICLE_NUMBER_LENGTH = 10


#--------------------------------------------------------------------------------#
# Define Global Variables.
#--------------------------------------------------------------------------------#
pytesseract.pytesseract.tesseract_cmd = ""
VehicleNumberFlag = 0
IndiaStateUtCodesDict = {
                          # "Code":"State or Union Territory"
                          "AN":"Andaman and Nicobar Islands",
                          "AP":"Andhra Pradesh",
                          "AR":"Arunachal Pradesh",
                          "AS":"Assam",
                          # "IND":"Bharat",
                          "IN":"Bharat",
                          "BR":"Bihar",
                          "CH":"Chandigarh",
                          "CG":"Chhattisgarh",
                          "DD":"Dadra and Nagar Haveli and Daman and Diu",
                          "DL":"Delhi",
                          "GA":"Goa",
                          "GJ":"Gujarat",
                          "HR":"Haryana",
                          "HP":"Himachal Pradesh",
                          "JK":"Jammu and Kashmir",
                          "JH":"Jharkhand",
                          "KA":"Karnataka",
                          "KL":"Kerala",
                          "LA":"Ladakh",
                          "LD":"Lakshadweep",
                          "MP":"Madhya Pradesh",
                          "MH":"Maharashtra",
                          "MN":"Manipur",
                          "ML":"Meghalaya",
                          "MZ":"Mizoram",
                          "NL":"Nagaland",
                          "OD":"Odisha",
                          "PY":"Puducherry",
                          "PB":"Punjab",
                          "RJ":"Rajasthan",
                          "SK":"Sikkim",
                          "TN":"Tamil Nadu",
                          "TS":"Telangana",
                          "TR":"Tripura",
                          "UP":"Uttar Pradesh",
                          "UK":"Uttarakhand",
                          "WB":"West Bengal",
                        }


#--------------------------------------------------------------------------------#
# Common Code.
#--------------------------------------------------------------------------------#
IndiaStateUtCodesList = list(IndiaStateUtCodesDict.keys())
IndiaStateUtCodesList.sort(reverse = False)


#--------------------------------------------------------------------------------#
# User Defined Functions (UDFs).
#--------------------------------------------------------------------------------#
def ManageCommandLineArgs():
  """
  # Function to manage command line arguments.
  """

  # Get the number of command line arguments.
  # Always the file name is the first argument.
  TotArgs = len(sys.argv)
  print()
  # print(TotArgs)
  # print(sys.argv[1])
  # print(sys.argv[2])
  # print(sys.argv[3])

  # Check the command line arguments.
  if TotArgs != 5:
    print('Command line arguments are not matching. Please check the format.')
    print('Command: python 06_NumPlateInfo.py <Image Folder Path> <Image File Name> <Path to "tesseract.exe"> <Debug Level (0 to 2; 0 for All)>')
    print('Example: python 06_NumPlateInfo.py "D:\\bdd100k\\images\\seg_track_20\\train" "HR_Pri_IC_001.jpg" <"C:\\Program Files\\Tesseract-OCR\\tesseract.exe"> "0"')
    print('Exiting .....')
    sys.exit(0)

  # Get the info from the command line arguments.
  ImageFolderPath = sys.argv[1]
  ImageFileName = sys.argv[2]
  pytesseract.pytesseract.tesseract_cmd = sys.argv[3]
  DebugLevel = sys.argv[4]

  # Adjust the parameter(s).
  ImageFolderPath = ImageFolderPath.replace('\\', '\\\\')
  pytesseract.pytesseract.tesseract_cmd = pytesseract.pytesseract.tesseract_cmd.replace('\\', '\\\\')
  DebugLevel = int(DebugLevel)

  return ImageFolderPath, ImageFileName, DebugLevel


def CleanVehicleNumber(VehicleNumber):
  """
  # Function to clean-up the vehicle number.
  """

  global VehicleNumberFlag
  VehicleNumberFlag = 0
  VehicleNumberList = list()

  # Create a list of capitl alphabets.
  CapAlphaList = [chr(Val) for Val in range(ord('A'), ord('Z') + 1)]

  # Create a list of digits.
  DigitList = list(map(chr, range(48, 58)))


  # # Convert to upper case because vehicle numbers are in upper case only.
  # VehicleNumber = VehicleNumber.upper()

  # Get the vehicle number string as a list of characters.
  CharList = list(VehicleNumber)
  
  # Loop over the characters of the vehicle number list, validate and create a valid list of characters.
  for Char in CharList:
    if Char in CapAlphaList or Char in DigitList:
      VehicleNumberList.append(Char)


  # Verify the correctness of the vehicle numbers by checking its length.
  if len(VehicleNumberList) != VEHICLE_NUMBER_LENGTH:
    # print("Case-01")
    # Case-01: Vehicle number with incorrect length.
    VehicleNumber = str("".join(VehicleNumberList))
    VehicleNumberFlag = 0
  else:
    # print("Case-02")
    # Case-02: Vehicle number with correct length i.e. the number is as per the
    #          current standard vehicle number system and also of length 10.
    
    # Get the vehicle number list in to vehicle number string.
    TempNumberStr = str("".join(VehicleNumberList))


    #--------------------------------------------------------------------------------#
    # Devide the vehicle number into the parts where each part has a significance.
    #--------------------------------------------------------------------------------#
    # Character '0' and Character '1' represents the State or Union Territory code and are alphabets.
    StateUtCode = TempNumberStr[0:2]
    # Character '2' and Character '3' represents the District or RTO code and are digits.
    DistRtoCode = TempNumberStr[2:4]
    # Character '4' and Character '5' represents the RTO series and are alphabets.
    Series_Code = TempNumberStr[4:6]
    # Character '6' to Character '9' represents a number between '1' and '9999' and are digits.
    Uniq_Number = TempNumberStr[6:]
    
    
    #--------------------------------------------------------------------------------#
    # Validate each significant part of the vehicle number separately.
    #--------------------------------------------------------------------------------#
    # Part-01: Character '0' and Character '1' represents the State or Union Territory code and are alphabets.
    TempList = list(StateUtCode)

    # Check and correct in case of 'O', 'I', '0', '1'.    
    for Idx, Char in enumerate(TempList):
      if TempList[Idx] == '0':
        TempList[Idx] = 'O'

      if TempList[Idx] == '1':
        TempList[Idx] = 'I'
        
    StateUtCode = str("".join(TempList))
    # print(StateUtCode)

    # Validation.
    # Note: Direct assignment first time ONLY. Subsequent assignments should use bitwise AND.
    if StateUtCode in IndiaStateUtCodesList:
      VehicleNumberFlag = 1
    else:
      VehicleNumberFlag = 0
    # print("1 >> {:}".format(VehicleNumberFlag))


    # Part-03: Character '4' and Character '5' represents the RTO series and are alphabets.
    TempList = list(Series_Code)

    # Check and correct in case of 'O', 'I', '0', '1'.    
    for Idx, Char in enumerate(TempList):
      if TempList[Idx] == '0':
        TempList[Idx] = 'O'

      if TempList[Idx] == '1':
        TempList[Idx] = 'I'
        
    Series_Code = str("".join(TempList))
    # print(Series_Code)

    # Validation.
    # Note: Direct assignment first time ONLY. Subsequent assignments should use bitwise AND.
    Pattern = r"[A-Z]{2}"
    Match = re.search(Pattern, Series_Code)

    if Match:
      # print("Match found: ", Match.group())
      VehicleNumberFlag &= 1
    else:
      # print("Match not found")
      VehicleNumberFlag &= 0
    # print("3 >> {:}".format(VehicleNumberFlag))


    # Part-02: Character '2' and Character '3' represents the District or RTO code and are digits.
    TempList = list(DistRtoCode)

    # Check and correct in case of 'O', 'I', '0', '1'.    
    for Idx, Char in enumerate(TempList):
      if TempList[Idx] == 'O':
        TempList[Idx] = '0'

      if TempList[Idx] == 'I':
        TempList[Idx] = '1'

      if TempList[Idx] == 'L':
        TempList[Idx] = '1'

      if TempList[Idx] == 'A':
        TempList[Idx] = '4'
        
    DistRtoCode = str("".join(TempList))
    # print(DistRtoCode)

    # Validation.
    # Note: Direct assignment first time ONLY. Subsequent assignments should use bitwise AND.
    try:
      IntVal = int(DistRtoCode)
      
      if 0 <= IntVal <= 99:
        VehicleNumberFlag &= 1
      else:
        VehicleNumberFlag &= 0
    except:
      VehicleNumberFlag &= 0
    # print("2 >> {:}".format(VehicleNumberFlag))


    # Part-04: Character '6' to Character '9' represents a number between '1' and '9999' and are digits.
    TempList = list(Uniq_Number)

    # Check and correct in case of 'O', 'I', '0', '1'.    
    for Idx, Char in enumerate(TempList):
      if TempList[Idx] == 'O':
        TempList[Idx] = '0'

      if TempList[Idx] == 'I':
        TempList[Idx] = '1'
        
    Uniq_Number = str("".join(TempList))
    # print(Uniq_Number)

    # Validation.
    # Note: Direct assignment first time ONLY. Subsequent assignments should use bitwise AND.
    try:
      IntVal = int(Uniq_Number)
      
      if 0 <= IntVal <= 9999:
        VehicleNumberFlag &= 1
      else:
        VehicleNumberFlag &= 0
    except:
      VehicleNumberFlag &= 0
    # print("4 >> {:}".format(VehicleNumberFlag))

    # Preapare the cleaned-up vehicle number.
    VehicleNumber = StateUtCode + DistRtoCode + Series_Code + Uniq_Number


  return VehicleNumber, VehicleNumberFlag


def DisplayVehicleBasicInfo(VehicleNumber):
  """
  # Function call to display the basic vehicle info i.e State/UT of Registration.
  """

  if VehicleNumber[0:2] in IndiaStateUtCodesList:
      StateUt = list(IndiaStateUtCodesDict.values())[list(IndiaStateUtCodesDict.keys()).index(VehicleNumber[0:2])]
      TempStr = "State/UT of Registration: {:s}".format(StateUt)
      # print('-' * len(TempStr))
      print(TempStr)
      # print('-' * len(TempStr))


  return None


def DisplayVehicleExtraInfo(CroppedColorImg):
  """
  # Function call to display the extra vehicle info i.e Number plate types.
  """
  
  """
  Type          BG          FG          Detail
  --------------------------------------------
  Type_01       White       Black       Private IC
  Type_02       Green       White       Private EV
  Type_03       Yellow      Black       Commercial IC
  Type_04       Black       Yellow      Self-Drive IC
  Type_05       Green       Yellow      Commercial EV
  Type_06       Red         White       Manufacturer IC
  Type_07       Yellow      Red         Temporary IC
  """

  # https://en.wikipedia.org/wiki/Vehicle_registration_plates_of_India
  VehicleInfoList = [
                      # BgLowerLimit,  FgLowerLimit,  BgColor,  FgColor,  Type,        Detail
                      # [            0,             0,  "White",  "Black",  "Type_01",   "Private",],
                      # [            0,             0,  "Green",  "White",  "Type_02",   "Private EV",],
                      # [            0,             0,  "Yellow", "Black",  "Type_03",   "Commercial",],
                      # [            0,             0,  "Black",  "Yellow", "Type_04",   "Self-Driving",],
                      [           65,            25,  "Green",  "Yellow", "Type_05",   "Commercial EV",],
                      # [            0,             0,  "Red",    "White",  "Type_06",   "Manufacturer Owned",],
                      [           25,           170,  "Yellow", "Red",    "Type_07",   "Temporary Registration",],
                    ]


  LowerList = [0, 100, 100]
  UpperList = [0, 255, 255]
  
  ResultsList = list()


  # Convert the given BGR image to HSV.
  hsv = cv2.cvtColor(CroppedColorImg, cv2.COLOR_BGR2HSV)


  # Loop over the vehicle number plate types to find the type of the number plate of the given vehicle.
  for Idx in range(len(VehicleInfoList)):
    #--------------------------------------------------------------------------------#
    # Check for Background color of the number plate.
    #--------------------------------------------------------------------------------#
    LowerList[0] = VehicleInfoList[Idx][0]
    UpperList[0] = VehicleInfoList[Idx][0] + 20
    Lower = np.array(LowerList)
    Upper = np.array(UpperList)

    MaskBg = cv2.inRange(hsv, Lower, Upper)

    if np.sum(MaskBg) > 0:
      # print('Yes, Background is detected!')
      Result = 1
    else:
      # print('No,  Background is not detected!')
      Result = 0

    # cv2.imshow('01:Image', CroppedColorImg)
    # cv2.imshow('02:MaskBg', MaskBg)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()


    #--------------------------------------------------------------------------------#
    # Check for Foreground color of the number plate.
    #--------------------------------------------------------------------------------#
    LowerList[0] = VehicleInfoList[Idx][1]
    UpperList[0] = VehicleInfoList[Idx][1] + 20
    Lower = np.array(LowerList)
    Upper = np.array(UpperList)

    MaskFg = cv2.inRange(hsv, Lower, Upper)

    if np.sum(MaskFg) > 0:
      # print('Yes, Foreground is detected!')
      Result &= 1
    else:
      # print('No,  Foreground is not detected!')
      Result &= 0


    #--------------------------------------------------------------------------------#
    # Update the results.
    #--------------------------------------------------------------------------------#
    ResultsList.append(Result)
    # print(ResultsList)
    
    
    # cv2.imshow('01:Image', CroppedColorImg)
    # cv2.imshow('02:MaskFg', MaskFg)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()


  # There should be ONLY one element with a value '1' and
  # all remaining elements should be '0' in the results list.
  # The reason is, a number plate matches to only one type i.e. Type_01 to Type_07.
  if ResultsList.count(1) != 1:
    print("Something went wrong")
  else:
    # Loop over the Results list and print the results.
    for Idx, Result in enumerate(ResultsList):
      if Result == 1:
        print("Number Plate BG Color   : {:s}".format(VehicleInfoList[Idx][2]))
        print("Number Plate FG Color   : {:s}".format(VehicleInfoList[Idx][3]))
        print("Vehicle Category        : {:s}".format(VehicleInfoList[Idx][5]))
        break


  return None


#--------------------------------------------------------------------------------#
# Main Code.
#--------------------------------------------------------------------------------#
if __name__ == "__main__":
  # Function call to manage command line arguments.
  # Get Image Folder Path, Image File Name, Debug Level info from the command line arguments.
  ImageFolderPath, ImageFileName, DebugLevel = ManageCommandLineArgs()

  
  # Read the image using OpenCV API.
  FullPath = ImageFolderPath + "\\" + ImageFileName
  OriginalColorImg = cv2.imread(FullPath, cv2.IMREAD_COLOR)
  
  # Debug Level 'x' info.
  if 0 <= DebugLevel <= 0:
    cv2.imshow('Original Color Image', OriginalColorImg)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
  
  
  # Resizing help us to avoid any problems with bigger resolution images.
  ResizedColorImg = cv2.resize(OriginalColorImg, RESIZE_IMG_TO)
  
  # Debug Level 'x' info.
  if 0 <= DebugLevel <= 0:
    cv2.imshow('Resized Color Image', ResizedColorImg)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
  
  
  # Convert to grey scale.
  ResizedGrayImg = cv2.cvtColor(ResizedColorImg, cv2.COLOR_BGR2GRAY)
  
  # Debug Level 'x' info.
  if 0 <= DebugLevel <= 0:
    cv2.imshow('Resized Gray Image', ResizedGrayImg)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
  
  
  # Blur to reduce noise.
  # Every image will have useful and useless information.
  # In our case, only the license plate is the useful information
  # and the rest is pretty much useless. This useless information is called noise.
  # Normally, using a bilateral filter (Bluring) will remove the noise from an image.
  # Syntax: destination_image = cv2.bilateralFilter(source_image, diameter of pixel, sigmaColor, sigmaSpace)
  ResizedBlurImg = cv2.bilateralFilter(ResizedGrayImg, 11, 17, 17)
  
  # Debug Level 'x' info.
  if 0 <= DebugLevel <= 0:
    cv2.imshow('Resized Blur Image', ResizedGrayImg)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
  
  
  # Perform edge detection.
  ResizedEdgeImg = cv2.Canny(ResizedBlurImg, MIN_THRESHOLD_CANNY, MAX_THRESHOLD_CANNY)
  
  # Debug Level 'x' info.
  if 0 <= DebugLevel <= 1:
    cv2.imshow('Resized Edge Image', ResizedEdgeImg)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
  
  
  # Find contours in the edged image, keep only the largest ones,
  # and initialize our screen contour.
  Contours = cv2.findContours(ResizedEdgeImg.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
  Contours = imutils.grab_contours(Contours)
  Contours = sorted(Contours, key = cv2.contourArea, reverse = True)[:10]
  
  # If no contours are found in the edged image, then exit the application.
  if len(Contours) <= 0:
    print("Number of contours is Zero.")
    print('Exiting .....')
    sys.exit(0)
    
    
  # Initialize screen count variable.
  NumPlateCoordinates = None

  # Loop over the contours.
  for Contour in Contours:
    # Approximate the contour.
    Peri = cv2.arcLength(Contour, True)
    Approx = cv2.approxPolyDP(Contour, 0.018 * Peri, True)

    # If our approximated contour has four points, then
    # we can assume that we have found our screen.
    if len(Approx) == 4:
      NumPlateCoordinates = Approx
      break
  
  
  if NumPlateCoordinates is None:
    print("Could not get the number plate coordinates.")
    print('Exiting .....')
    sys.exit(0)

  # Get a copy of the Resized Color Image.
  ResizedColorImgCpy = ResizedColorImg.copy()
  
  # To draw all the contours in an image.
  cv2.drawContours(ResizedColorImgCpy, [NumPlateCoordinates], -1, COLOR_BGR_GREEN, LINE_THICKNESS)

  # Masking the part other than the number plate.
  Mask = np.zeros(ResizedBlurImg.shape, np.uint8)
  NumPlateImg = cv2.drawContours(Mask, [NumPlateCoordinates], 0, 255, -1,)
  NumPlateImg = cv2.bitwise_and(ResizedBlurImg, ResizedBlurImg, mask=Mask)
  
  # Debug Level 'x' info.
  if 0 <= DebugLevel <= 1:
    cv2.imshow('Number Plate Image', NumPlateImg)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
  

  # Now crop the number plate.
  (X, Y) = np.where(Mask == 255)
  (TopX, TopY) = (np.min(X), np.min(Y))
  (BottomX, BottomY) = (np.max(X), np.max(Y))
  CroppedBlurImg = ResizedBlurImg[TopX:BottomX + 1, TopY:BottomY + 1]

  # Debug Level 'x' info.
  if 0 <= DebugLevel <= 1:
    cv2.imshow('Cropped Blur Image', CroppedBlurImg)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
  
  
  # Read the number plate.
  # text = pytesseract.image_to_string(Cropped, config='--psm 11')
  VehicleNumber = str(pytesseract.image_to_string(CroppedBlurImg))

  # Debug Level 'x' info.
  if 0 <= DebugLevel <= 1:
    print("Extracted Vehicle Number: {:s}".format(VehicleNumber))
  
  
  if (len(VehicleNumber) <= 0):
    print("Unable to extract the Vehicle Number text from the image.")
  else:
    # Function call to clean-up the vehicle number.
    VehicleNumber, VehicleNumberFlag = CleanVehicleNumber(VehicleNumber)


  # Display the extracted and cleaned-up vehicle number.
  print("Vehicle Info:")
  print("-------------")
  # Display the extracted and cleaned-up vehicle number.
  print("Registration Number     : {:s}".format(VehicleNumber))

  
  if VehicleNumberFlag == 0:
    # print("Note: This vehicle number neither confirming the format nor confirming the size (10 Characters).  May not the correct one.")
    # print("Non-Standard Vehicle Number.")
    print("State/UT of Registration: Unknown")
  else:
    # print("Note: This vehicle number confirming the format and size (10 Characters).  Mostly, the correct one.")
    # print("Standard Vehicle Number.")

    # Function call to display the basic vehicle info i.e State/UT of Registration.
    DisplayVehicleBasicInfo(VehicleNumber)

    # Now crop the number plate.
    CroppedColorImg = ResizedColorImg[TopX:BottomX + 1, TopY:BottomY + 1]
    
    # Debug Level 'x' info.
    if 0 <= DebugLevel <= 1:
      cv2.imshow('Resized Color Image', CroppedColorImg)
      cv2.waitKey(0)
      cv2.destroyAllWindows()
    
    # Function call to display the extra vehicle info i.e Number plate types.
    DisplayVehicleExtraInfo(CroppedColorImg)

  
  # Debug Level 'x' info.
  if 0 <= DebugLevel <= 2:
    cv2.imshow('Resized Color Image with Identified Number Plate', ResizedColorImgCpy)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

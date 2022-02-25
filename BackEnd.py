#--------------------------------------------------------------------------------#
# Import necessary modules.
#--------------------------------------------------------------------------------#
import io
from cv2 import cv2

import numpy as np

from fastapi import FastAPI
from fastapi import Request
from fastapi import File
from fastapi import UploadFile

from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles



#--------------------------------------------------------------------------------#
# Define Constants.
#--------------------------------------------------------------------------------#
RESIZE_IMG_TO = (640, 480)


#--------------------------------------------------------------------------------#
# Define Global Variables.
#--------------------------------------------------------------------------------#
# Object of FastAPI.
App = FastAPI()

# Templates.
Templates = Jinja2Templates(directory = "HTML")

# static/js/post.index js.Required to call from html
App.mount("/SupportFiles", StaticFiles(directory="SupportFiles"), name="SupportFiles")


# GET option.
@App.get('/')
def root(request:Request):
  return Templates.TemplateResponse("FrontEnd.html", context = {'request':request})


# POST option.
@App.post('/')
async def root(request:Request, UserFile: UploadFile = File(...)):
  BinaryData = io.BytesIO(UserFile.file.read())
  
  BinaryDataArray = np.asarray(bytearray(BinaryData.read()), dtype=np.uint8)

  OriginalRgbColorImg = cv2.imdecode(BinaryDataArray, cv2.IMREAD_COLOR)
  OriginalGrayScaleImg = cv2.cvtColor(OriginalRgbColorImg, cv2.COLOR_RGB2GRAY)

  ResizedRgbColorImg = cv2.resize(OriginalRgbColorImg, RESIZE_IMG_TO)
  ResizedGrayScaleImg = cv2.resize(OriginalGrayScaleImg, RESIZE_IMG_TO)

  cv2.imwrite("./SupportFiles/Dynamic/Input.jpg", ResizedRgbColorImg)
  cv2.imwrite("./SupportFiles/Dynamic/Output.jpg", ResizedGrayScaleImg)

  InputImg = "Input.jpg"
  OutputImg = "Output.jpg"
  InputImg = ("./SupportFiles/Dynamic/Input.jpg")
  OutputImg = ("./SupportFiles/Dynamic/Output.jpg")


  return Templates.TemplateResponse("Results.html", context = {'request':request, "InputImg":InputImg, "OutputImg":OutputImg})


#--------------------------------------------------------------------------------#
# Main Code.
#--------------------------------------------------------------------------------#
# if __name__ == "__main__":

# AIML_Project03


The folder "ForSubmission": This folder is for the files and info regarding the project submission.
---------------------------------------------------------------------------------------------------
* This folder consists of 3 sub-folders:
  + 01_Training_Output:
  - This sub-folder contains all the input images and videos given to the model for testing and the corresponding output images and videos having the object detection bounding boxes and confidence values.
  - This sub-folder contains the Google Colab Pro notebook file 'ObjectDection_DarknetYOLOv3_ColabPro.ipynb' which is the Python code file used for the development and training of the model.
  - This sub-folder contains a total of 27 files.
  + 02_MyTools:
  - This sub-folder contains all the Python code files which we have implemented and are used as tools for making various things easy during development and training. We have a total of 6 Python code files here.
  - This sub-folder contains the file 'Commands.txt' which contains the commands regarding how to use the Python code files i.e. tools.
  - This sub-folder contains the 'PythonPackages.txt' which contains the info regarding all the Python packages and modules with versions that we have used during our development time.  This file can be used as 'requirements.txt' to install Python packages and module in case to execute the 6 Python code files.
  - This sub-folder contains the '[Cat01] MH_Pri_EV_002.jpg' file, which is minimum required to test the '06_NumPlateInfo.py' Python code file i.e. tool.
  - This sub-folder contains a total of 9 files.
  + 03_Presentation:
  - This sub-folder contains the file 'PCGP Final Presentation.pdf', which is the PDF version of the 'PCGP Final Presentation.pptx' that we are going to present on Sun, 27/Feb/2002.
  - This sub-folder contains a total of 1 file.


The folders "HTML", "SupportFiles" and the files "BackEnd.py", "Procfile", "requirements.txt", "runtime.txt":
-------------------------------------------------------------------------------------------------------------
* These folders and the files are the part of the stuff that is required for Cloud (Heroku) deployment.

The folder "HTML":
  * This folder contains all the necessary HTML files which are the part of User Interface w.r.t. the Cloud (Heroku) deployment.

The folder "SupportFiles":
  * This folder consists of 2 sub-folders:
    + Dynamic:
    - This sub-folder is to store the files (Image, Video)  which are sent through the User Interface i.e. input file (and/or) for the files processed by the backend program (and/or) the output file. Actually this folder is used for the files that are dynamically created and then removed.
    - This sub-folder contains 'Test.txt' file which is a dummy file because of the reason that GitHub won't allow empty folders. This is only the static file so that GitHub will keep this folder.
    + Static:
    - This sub-folder is to store the files which are the result of the model training process.
    - This sub-folder containg the following files:
      classes.names
      yolov3_bdd100k_test.cfg
      yolov3_bdd100k_train_last.weights
    - This sub-folder contains a total of 3 files.

The file "BackEnd.py":
  * This file is the Python code file that uses the FastAPI and is the backend code file for the deployment of the model or application.

The file "Procfile":
  * This file contains the web server command for the 'uvicorn' web server.

The file "requirements.txt":
  * This file contains the info regarding all the Python packages and modules with versions that are required to bring-up the model or application on the Cloud (Heroku). This file is the file for the command 'pip install -r requirements.txt' to install Python packages.

The file "runtime.txt":
  * This file contains the info regarding the version of the Python to be used. This file is used to know the system which version of the Python is required to bring-up the model or application on the Cloud (Heroku).

# Import necessary modules.
import os
import sys
import cv2
import imutils
import numpy as np
from skimage.metrics import structural_similarity as compare_ssim


# Define Global Variables.


# Define Constants.

# Observed value of SSIM for best matching images.
IMAGE_FILE_EXT = ".jpg"
SSIM_MAX = 0.98
SHOW_IMAGE = 0


# Manage Command Line Arguments.
# Get the number of command line arguments.
# Always the file name is the first argument.
TotArgs = len(sys.argv)
print()
# print(TotArgs)
# print(sys.argv[1])
# print(sys.argv[2])
# print(sys.argv[3])

# Check the command line arguments.
if TotArgs != 3:
    print('Command line arguments are not matching. Please check the format.')
    print('Command: python 04_ImgCompare.py <First Image Folder Path> <Second Image Folder Path>')
    print('Example: python 04_ImgCompare.py "D:\bdd100k\images\seg_track_20\train1" "D:\bdd100k\images\seg_track_20\train2"')
    print('Exiting .....')
    exit(0)

# Get the info from the command line arguments.
PathA = sys.argv[1]
PathB = sys.argv[2]

# Adjust the path.
PathA = PathA.replace('\\', '\\\\')
PathB = PathB.replace('\\', '\\\\')


#--------------------------------------------------------------------------------#
# Main Code.
#--------------------------------------------------------------------------------#
# Get the list of first set of images.
ImageFileListA = [File for File in os.listdir(PathA) if File.endswith(IMAGE_FILE_EXT)]
ImageFileListA.sort(reverse=False)

# Get the list of second set of images.
ImageFileListB = [File for File in os.listdir(PathB) if File.endswith(IMAGE_FILE_EXT)]
ImageFileListB.sort(reverse=False)


# Loop through both the lists for image comparison.
for ImageA in ImageFileListA:
    for ImageB in ImageFileListB:
        # Prepare the full path i.e. Path + File Name.
        FullPathA = PathA + "\\" + ImageA
        FullPathB = PathB + "\\" + ImageB
        # print(FullPathA)
        # print(FullPathB)
        
        # Load the two input images.
        ImgA = cv2.imread(FullPathA)
        ImgB = cv2.imread(FullPathB)

        # Convert the two imput images to grayscale.
        GrayImgA = cv2.cvtColor(ImgA, cv2.COLOR_BGR2GRAY)
        GrayImgB = cv2.cvtColor(ImgB, cv2.COLOR_BGR2GRAY)

        """
        https://www.pyimagesearch.com/2017/06/19/image-difference-with-opencv-and-python/
        
        The 'Score' represents the structural similarity index between the two input images.
        This value can fall into the range [-1, 1] with a value of one being a “perfect match”.

        The 'Diff' image contains the actual image differences between the two input images
        that we wish to visualize. The difference image is currently represented as a
        floating point data type in the range [0, 1] so we first convert the array to
        8-bit unsigned integers in the range [0, 255] before we can further process it using OpenCV.
        """

        # Compute the Structural Similarity Index (SSIM) between the two images,
        # ensuring that the difference image is returned.
        (Score, Diff) = compare_ssim(GrayImgA, GrayImgB, full=True)
        Diff = (Diff * 255).astype("uint8")
        Text = "Image-1: {:s}, Image-2: {:s}, SSIM: {:0.2f}".format(ImageA, ImageB, Score)
        print("\r{:s}".format(Text), end="")

        # In case the two images are almost identical,
        if Score >= SSIM_MAX:
            print(" << Matching.")
            
            # if the show window flag is on then show the difference between the two images.
            if SHOW_IMAGE:
                cv2.imshow(Text, Diff)
                cv2.waitKey(0)
                cv2.destroyAllWindows()


    print("")




# PathA = "D:\\StudyKit\\2021-11-13 AI, ML PG Course at IIIT, Hyd\\Project#03\\03 Berkeley DeepDrive Data\\bdd100k\\images\\seg_track_20\\train\\0000f77c-62c2a288"
# PathB = "D:\\StudyKit\\2021-11-13 AI, ML PG Course at IIIT, Hyd\\Project#03\\bdd100k\\videos\\train\\0000f77c-62c2a288"





# # Working fine.
# import cv2
# import numpy as np

# a = cv2.imread("D:\\StudyKit\\2021-11-13 AI, ML PG Course at IIIT, Hyd\\Project#03\\03 Berkeley DeepDrive Data\\bdd100k\\images\\seg_track_20\\train\\000d35d3-41990aa4\\000d35d3-41990aa4-0000001.jpg")
# b = cv2.imread("D:\\StudyKit\\2021-11-13 AI, ML PG Course at IIIT, Hyd\\Project#03\\bdd100k\\videos\\train\\New folder\\000d35d3-41990aa4\\000d35d3-41990aa4-0000001.jpg")
                
# difference = cv2.subtract(a, b)
# result = not np.any(difference)

# if result is True:
    # print("Pictures are the same")
# else:
    # cv2.imwrite("ed.jpg", difference )
    # print("Pictures are different, the difference is stored as ed.jpg")

# image = cv2.imread("ed.jpg")

# cv2.imshow("Hello", image)
# cv2.waitKey(0)
# cv2.destroyAllWindows()





##### Not usesful.

# import cv2
# import numpy as np

# original = cv2.imread("D:\\StudyKit\\2021-11-13 AI, ML PG Course at IIIT, Hyd\\Project#03\\03 Berkeley DeepDrive Data\\bdd100k\\images\\seg_track_20\\train\\0000f77c-62c2a288\\0000f77c-62c2a288-0000001.jpg")
# duplicate = cv2.imread("D:\\StudyKit\\2021-11-13 AI, ML PG Course at IIIT, Hyd\\Project#03\\bdd100k\\videos\\train\\0000f77c-62c2a288\\0000f77c-62c2a288_000003.jpg")

# # 1) Check if 2 images are equals
# if original.shape == duplicate.shape:
    # print("The images have same size and channels")
    # difference = cv2.subtract(original, duplicate)
    # b, g, r = cv2.split(difference)
    
# if cv2.countNonZero(b) == 0 and cv2.countNonZero(g) == 0 and cv2.countNonZero(r) == 0:
    # print("The images are completely Equal")

# cv2.imshow("Original", original)
# cv2.imshow("Duplicate", duplicate)
# cv2.waitKey(0)
# cv2.destroyAllWindows()
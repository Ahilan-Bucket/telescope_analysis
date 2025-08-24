import numpy as np
from astropy.io import fits
import matplotlib.pyplot as plt
import os
home = os.getenv('HOME')

# This is the only thing that needs to switch depending on if you're working at the lab
# or on your own computer
onedrive = r"C:\Users\ahila\OneDrive - Simon Fraser University (1sfu)"

# This is in our shared directory.  When you get your own data, replace 
# "JoannaData" with the folder you created with your group
data_dir = onedrive + r"\PHYS391-Spring-2025-shared\Assignment2\Group 3"

# This is your private directory.  You should save this python script there too.
working_dir = onedrive + r'\PHYS391-Spring-2025-private\Assignment2'


#---------------------------------------------------------------------------------------
bias_directory = data_dir + r'\Bias\\'
light_directory = data_dir + r'\Light\\'
                                                                                                                                                              

# choose 2 bias files in the bias directory
biasfiles = [r'BIAS-0001.fit',r'BIAS-0002.fit']

# The two dome exposures.
domefiles = [r'DOME-0001.fit',r'DOME-0002.fit']

# Open one of the dome exposures using ds9 and examine where the overscan and dark 
# strips are. Determine the crop ranges remembering that ds9 starts counting at 1 while
# Python starts counting at 0. 

# (Y1,Y2) , (x1,x2)
crop = slice(114-1,8839-1) , slice(48-1,11712-1) # slice(8839,115), slice (7082,5978) on ds9
# (small, )



# Extract the image data from the bias files, crop them to the useable area.  
# For B1, B2, L1 and L2, you can use the mean of the arrays (after cropping).
# Note that the raw image values are saved as integers.  Turn them into floats before
# you do any calculations on them.  Otherwise, your values will be weird.

hduB1 = fits.open(bias_directory + biasfiles[0]) 

imageB1 = hduB1[0].data.astype(float)
#print("Image B1",imageB1)

crop_imageB1 = imageB1[crop]

#print("crop",crop_imageB1)
    
hduB2 = fits.open(bias_directory + biasfiles[1]) 

imageB2 = hduB2[0].data.astype(float)
crop_imageB2 = imageB2[crop]

meanB1 = np.mean(crop_imageB1)

meanB2 = np.mean(crop_imageB2)


# Dome 
# Extract the data from the dome images into the arrays dome1 and dome2:

hduL1 = fits.open(light_directory + domefiles[0]) 

imageL1 = hduL1[0].data.astype(float)
crop_imageL1 = imageL1[crop]
    
hduL2 = fits.open(light_directory + domefiles[1]) 

imageL2 = hduL2[0].data.astype(float)
crop_imageL2 = imageL2[crop]
    

meanL1 = np.mean(crop_imageL1)
meanL2 = np.mean(crop_imageL2)


print(f"Mean B1 {meanB1} \nMean B2 {meanB2} \nMean L1 {meanL1} \nMean L2 {meanL2} ")


#print("crop_imageL1", crop_imageL1) 

# Should i use Cropeed images here? # ???
# Create the difference images and compute the variance of the difference images.
# (This is where things go wrong if you didn't convert the images to floats.)
L12 = crop_imageL1 - crop_imageL2
B12 = crop_imageB1 - crop_imageB2

varL12 = np.var(L12)
varB12 = np.var(B12)

print(f"\nVar L12 {varL12}")
print(f"Var B12 {varB12}")



# Variance alreadu squared
# Use the Eq 1 in the Assignment to derive the gain of the CCD:
# gain = ( (crop_imageL1 + crop_imageL2) - ( crop_imageB1 + crop_imageB2) ) / (varL12 - varB12) 


gain = ( (meanL1 + meanL2) - ( meanB1 + meanB2) ) / (varL12 - varB12) 


print('The CCD gain is: ', gain)


# Now compute the read noise in electrons using Eq 2
variance_readnoise = 0.5 * gain **2 * varB12
readnoise = np.sqrt(variance_readnoise)

print('The CCD read noise is ', readnoise,' electrons')

# Make a histogram of the values in the bias difference image.  Since the difference 
# image is a 2D array, you'll need to flatten it into a 1D array before you use it as
# input into plt.hist().  Use 100 bins, and be sure to label the plot with the correct
# units. 
plt.hist( B12.flatten() , bins = 100)
plt.xlim(-40,40)
plt.xlabel("Bias Difference Image (ADU)")
plt.ylabel("Frequency")
plt.title("Histogram of Bias Difference Image")
plt.tight_layout()

# Save the image into your working directory
plt.savefig(working_dir+'/BiasDifferenceHistogram.png')
plt.show()

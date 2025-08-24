import numpy as np
from astropy.io import fits
import os, glob
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
# Write a function to read in a list of files and output the mean of all the frames.
def combine(filelist):
    # Strategy: read the files one by one.  For the first file save the image data to 
    # an array.  For the rest of the files add their data to the first array.  At the 
    # end, divide the image array by the number of files in filelist to get the mean.  
    # This method ensures that we don't load all the files into memory.
    count = 0
    for f in filelist:
        hdu = fits.open(f)
        image = hdu[0].data.astype(float)
        if count == 0:
            array_memory = image
        else:
            array_memory += image
        count += 1
            
    meanimg = array_memory / count
               
    return meanimg

#---------------------------------------------------------------------------------------
bias_directory = data_dir + r'\Bias\\'
dark_directory = onedrive+ r'\PHYS391-Spring-2025-shared\Assignment2\DARK'


# Put in your values that you found in Part 3.

gain = 0.3360284075579739

readnoise = 1.6506094506539937 # in electrons

# And the "crop" tuple that you found in Part 3:

crop = slice(114-1,8839-1) , slice(48-1,11712-1) # slice(8839,115), slice (7082,5978) on ds9

filelist = glob.glob(bias_directory+'/*')
masterbias = combine(filelist) # use the "combine" function you wrote above

medianbias = np.median(masterbias[crop]) # compute the median of the *cropped* masterbias

# Note: the following line prints an f-string which is a useful way to construct strings
# using predefined variables.  The :.4f means print only 4 decimal places.
print(f'Median value of the master bias: {medianbias:.4f}') 

# Save the master bias as a new file in your working_dir.  Open the first fits file to
# get the "hdu" object which we'll use to make a new file.  Overwrite the data
# with the masterbias add some information to the header.  Then use the "writeto" 
# method to save to file.
hdu = fits.open(filelist[0]) # open the first file to get the header information
hdu[0].data = masterbias # Save the master bias data here
hdu[0].header['COMMENT'] = ('Master Bias (ADU) created by Ahilan Kumaresan') # Put your name
hdu[0].header['BZERO'] = 0 
hdu.writeto(working_dir+'/MasterBias_BIN1.fit',overwrite=True)


# Do the same thing to create the master dark.  
filelist = glob.glob(dark_directory+'/*')
masterdark = combine(filelist)

# This time we need to remove the bias, and ensure that the resulting dark values are 
# in units of ADU/s, so they represent the dark *current*.  Each file is exposed with 
# the same exposure time.  Get the time from the first file in the list.
hdu = fits.open(filelist[0]) # open the first file
t_exp = hdu[0].header['EXPTIME'] # get the exposure time of the first file. 
            # Assume all files have the same exposure time (they do)
            
# Use the masterbias and t_exp to turn the masterbias data into ADU/s
# Master Dark = (master dark - master bias) / t_exp

masterdark = (masterdark - masterbias) / t_exp # ??? ASK

# The dark current for this long exposure was sometimes smaller than the read noise, 
# so some of the pixels will be negative after subtracting the masterbias.  For these 
# pixels, assign the value to be 0 since the dark current was negligibleible.
mask = masterdark < 0 # mask is an array with True / False for each element in masterdark

badfrac = np.sum(mask) / masterdark.size # Number of negative pixels/total number of pixels
# np.sum(mask) when mask is an array of True and False, 
# len(array) gives the dimesnion of the first column. So no. of rows
# mask.size = total number of elemnts in x and y
# mask.shape = dimensions on x and y

print(f'Fraction of pixels with unmeasurable dark current: {badfrac:.4f}') 

# For these pixels set the masterdark to be 0.
masterdark[mask] = 0 # Replaces the below...
'''
for i in range(len(masterdark)):
    if masterdark[i] < 0:
        masterdark[i] == 0
'''    

mediandark = np.median(masterdark[crop]) # The median of the cropped masterdark 
mediandark_electrons = mediandark * gain # The median of the cropped masterdark in electrons.
# From formula to convert ADU to electrons

print(f'Median ADU of the master dark: {mediandark:.6f} per second')
print(f'Median dark current in e-/s: {mediandark_electrons:.6f}')

# Save the master dark as a new file in your working_dir.  Overwrite the data in the 
# hdu object you opened, and add some information to the header.  Then use the "writeto" 
# method to save to file.
hdu[0].data = masterdark # Save the masterdark here
hdu[0].header['COMMENT'] = ('Master Dark (ADU/s) created by Ahilan Kumaresan') # Put your name
hdu[0].header['BZERO'] = 0

hdu.writeto(working_dir+'/MasterDark_BIN1.fit',overwrite=True)
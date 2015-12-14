'''
(c) December 2015 by Daniel Seita

OK, so we'll do this in vim rather than ipython notebook (but I'll learn how to use notebook later).
What we do here is we assume we have 'images' as the name of the directory that contains a crapload
of PNG files. Then we'll go ahead and downsample as many images as we reasonably can to 84x84. Then,
I'll copy this to my machine that has caffe in it, and we can get the ball going on that. Oh, I
forgot, we do need the file with all the numbers in it, as well. Ugh ...
'''

import cv2
import os
import numpy as np
import scipy
import scipy.misc
import sys

def process_images(user_id, image_files, file_prefix, output_directory):
    """
    The 'image_files' is a list of the names of space invaders images, in numeric order (i.e.,
    1.png, 2.png, ..., 20000.png or whatever is the max) we process these images into a single
    output directory. Processing includes (1) downsampling to 84x84, (2) averaging two consecutive
    images to avoid the dashed lines (the 'bullets/lasers') from disappearing, and (3) putting all
    images from all users in the same directory, to simplify the process of randomly drawing them.

    Our images are 1.png, 2.png, etc. So this will save images as uid_00001.png, uid_00002.png,
    etc., with the following max: uid_1.png = np.max(1.png, 2.png), and similarly for higher
    indices.

    Some file names are missing, e.g., we may have 140.png followed by 142.png. That's fine, our
    code should combine those two and save the file as uid_00140.png.
    """

    # Note weird convention, cv2.shape is like (width,height) but numpy is (height,width)
    total_images = len(image_files)
    prev_img = cv2.imread(file_prefix + '1.png',0)
    assert image_files[1] == '00002.png', "image_files[1] = " + image_files[1]

    # Iterate through images. First current_img is named '0002.png', in NUMERICAL order.
    for index in range(1,len(image_files)):

        # Debug prints, take max of frames, and convert from, e.g., '0004.png' to '4.png'
        if (index % 5000 == 0):
            print "Done with image {} out of {}.".format(index, total_images)
        index_current = int(image_files[index].split('.')[0])
        current_img = cv2.imread(file_prefix + str(index_current) + '.png',0)
        img_max = np.maximum(prev_img, current_img)
        assert img_max.shape == (213,160), "The shape is " + str(img_max.shape)

        # Resize according to deep_q_rl conventions
        resized = cv2.resize(img_max, (84,110), interpolation=cv2.INTER_LINEAR)
        crop_y_cutoff = 18
        cropped = resized[crop_y_cutoff:crop_y_cutoff+84,:]
        assert cropped.shape == (84,84), "The shape is " + str(cropped.shape)

        # Save file based on the index of the *previous* image, at index-1
        index_prev = str(index_current - 1).zfill(5)
        new_file_name = output_directory + '/' + user_id + '_' + index_prev + '.png'
        scipy.misc.imsave(new_file_name, cropped)
        prev_img = current_img

    print "All done with this set of images."


########
# MAIN #
########

immediate_directory = '/Users/danielseita/atari_learning/processing/out' # Original, raw images from all users
output_directory = 'images_processed_fivedigits' # Downsampled *and* combined so it's across users

# For each directory in 'images', which has a 'user', we go to 'game2' and downsample each image.
user_files = os.listdir(immediate_directory)
user_files.remove('.DS_Store')
assert len(user_files) == 33, "User files has length " + str(len(user_files))
user_index = 0

for user in user_files:
    if user_index != 24 and user_index != 18: # and user_index >= 19: # Be careful about this!
        sp_inv_images = immediate_directory + '/' + user + '/game2/'
        images_raw = [x for x in os.listdir(sp_inv_images) if 'png' in x]
        images_sorted = sorted([x.split('.')[0].zfill(5) + '.png' for x in images_raw])
        print 'Total of {} images in {} for user index {}'.format(len(images_sorted), sp_inv_images, user_index)
        uid = sp_inv_images.split('/')[-3]
        process_images(uid, images_sorted, sp_inv_images, output_directory)
        user_index += 1
    else:
        user_index += 1

'''
(c) December 2015 by Daniel Seita

Here, we assume we have a bunch of 84x84 images already created for ALL users, and they are all
named appropriately, in order, and with the prefix the user ID. From this, ALONG with the game log,
(export_2015-12-13/gamelogs.json) we must determine the correct action to use. This will be tricky,
by the way. Also, we're going to have to subsample.

The easiest way, I think, is to go through the game log, with the action known at each frame, and
each time we see a log item, we "update" the action accordingly.

Note: I explicltly went through that gamelogs.json file to get rid of the three bogus user IDs.

Note: if I see anything with 'mPicPJMS6vYfQoEsB' in it, be aware that that user ID gave some
problems. So avoid using it. Also 'szBfRJZ6deGMttB3a'. Not sure why ... OK I deleted images from
those users, so that shouldn't be aproblem. There will now be THIRTY ONE users that provide us the
data we need to do for this project.
'''

import glob
import json
import os
import sys

def determine_actions(uid, log, outfile):
    """
    For user 'uid' with game log 'log' (i.e., that list of 4-tuples...), we must determine the
    appropriate actions for the screenshots we use, and write it to the outfile. Note: I do think
    this is all correctly set up ... I checked the lengths and they all match up appropriately.
    Also, let's just TRY to use all images for now?

    Actions:
      0 = nothing
      1 = fire
      2 = right
      3 = left
      4 = right fire
      5 = left fire

    In Javatari, 13 = left, 14 = right, 15 = fire, and 'true/false' to indicate if pressed.
    """

    image_root = '/Users/danielseita/UC_Berkeley_Material/CS_287-Advanced_Robotics/FinalProject/images_processed_fivedigits'
    relevant_images = glob.glob(image_root + '/' + uid + '*')
    current_frame = 0
    current_action = 0
    log_index = 0
    pressed_space = False
    acceptable_numbers = [13,14,15]

    # If I ever want to know what frame I'm in for the logs, use int(current_log[1]).
    current_log = log[log_index]
    while int(current_log[2]) not in acceptable_numbers:
        log_index += 1
        current_log = log[log_index]

    # Iterate through images, but the idea is that we should know action up to a point after this image
    for name in relevant_images:
        
        # Get last FIVE digits and convert to actual frame number
        image_name = name.split('/')[-1].split('.')[0]
        image_frame = int(image_name[-5:]) # E.g., if 13 for first user, we change actions

        # If the current action we know is *ahead* of this frame, then we know what to do.
        if image_frame < int(current_log[1]):
            outfile.write(name + ' ' + str(current_action) + '\n')

        else:
            # Now have to go through a bunch of cases. Yes, we use integers here, not strings.
            if (current_log[2] == 13 and current_log[3] == True):
                if pressed_space:
                    current_action = 5
                else:
                    current_action = 3
            elif (current_log[2] == 13 and current_log[3] == False):
                if pressed_space:
                    current_action = 1
                else:
                    current_action = 0
            elif (current_log[2] == 14 and current_log[3] == True):
                if pressed_space:
                    current_action = 4
                else:
                    current_action = 2
            elif (current_log[2] == 14 and current_log[3] == False):
                if pressed_space:
                    current_action = 1
                else:
                    current_action = 0
            elif (current_log[2] == 15 and current_log[3] == True):
                pressed_space = True
                if current_action == 2: # Right
                    current_action = 4
                elif current_action == 3: # Left
                    current_action = 5
                else:
                    current_action = 1
            elif (current_log[2] == 15 and current_log[3] == False):
                pressed_space = False
                if current_action == 4: # Right fire
                    current_action = 2
                if current_action == 5: # Left fire
                    current_action = 3
                else:
                    current_action = 0

            # After every time we're here, we update, and better be writing *something* to the output file!
            log_index += 1
            current_log = log[log_index]
            while int(current_log[2]) not in acceptable_numbers:
                log_index += 1
                if (log_index < len(log)):
                    current_log = log[log_index]
                else:
                    break
            outfile.write(name + ' ' + str(current_action) + '\n')

########
# MAIN #
########

immediate_directory = '/Users/danielseita/atari_learning/processing/out'
user_files = os.listdir(immediate_directory)
user_files.remove('.DS_Store')
user_files.remove('mPicPJMS6vYfQoEsB')
user_files.remove('szBfRJZ6deGMttB3a')
assert len(user_files) == 31, "User files has length " + str(len(user_files))

# Use json.loads( string ) to convert a string into a dict, if possible.
gamelogs_file = 'export_2015-12-13/gamelogs.json'

with open(gamelogs_file, 'r') as f:

    outfile = open('output.txt', 'w')
    logs = f.readlines()
    game_dicts = [json.loads(logs[i]) for i in range(len(logs))]
    indices = {}

    # Just to make indexing a little easier; 'game2' indicates it has space invaders info.
    for (i,d) in enumerate(game_dicts):
        if d['name'] == 'game2' and str(d['uid']) in user_files:
            indices[str(d['uid'])] = i

    # OK, now the real thing starts.
    for (i,uid) in enumerate(user_files):
        print "Currently analyzing S.I. for user {} at index {}.".format(uid,i)
        d = game_dicts[indices[uid]] 
        log = d['data']['logs']
        determine_actions(uid, log, outfile)
    outfile.close()

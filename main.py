# Run PrintDQ toolchain on the grid
# Author: Steven Doran

import os
import time
from lib import helper as h

#
#
#

'''@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@'''

''' Please modify the following to reflect your working directory '''

user = '<username>'

TA_folder = 'ToolAnalysis/'                       # Folder that was tar-balled (Needs to be the same name as the ToolAnalysis directory in /exp/annie/app that will run TrigOverlap + BeamFetcherV2 toolchains)
TA_tar_name = 'MyToolAnalysis_grid.tar.gz'        # name of tar-ball

grid_sub_dir = 'PrintDQ_grid/'                    # input grid
grid_output = 'output/PrintDQ/'                   # output grid

'''@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@'''

#
#
#
#
#

# constructed paths based on user customization and current areas of data

scratch_path = '/pnfs/annie/scratch/users/' + user + '/' + grid_sub_dir                            # clone repository/set of grid scripts
output_path = '/pnfs/annie/scratch/users/' + user + '/' + grid_output                              # general output directory (jobs will be deposited directly here)
data_path = '/pnfs/annie/persistent/processed/processed_EBV2/'                                     # Processed Data location


# # # # # # # # # # # # # # # # # # # # # # # # # # 
print('\n\n**********************************************************\n')
user_confirm = input('The current user is set to ' + user + ', is this correct? (y/n):      ')
if user_confirm == 'n':
    user = input('\nPlease enter the correct user name:      ')
    print('\nUser has been set to ' + user + ', locking in changes...')
    time.sleep(3)
elif user_confirm != 'y' and user_confirm != 'n':
    print('\nInvalid response - please restart script\n')
    exit()
print('\n')

usage_verbose = """
#########################################################################################
# ******* PrintDQ grid submission ********
# args: --runs_to_run
#
# runs_to_run = runs you would like to submit.
#       --> Two options:
#               1. Read from user provided list (please populate 'runs.list')
#               2. Submit runs manually
#########################################################################################
"""

print(usage_verbose, '\n')

runs_to_run_user = h.get_runs_from_user()

print('\nVetting the runs you submitted...\n')

# Make sure the ProcessedData is available for the runs the user selected
available_runs = h.is_there_data(runs_to_run_user, data_path)
    
# -------------------------------------------------------------
print('\n*************************************************\n')
print('The following runs will be sent:\n')
print('  - ', available_runs)
print('\n')
time.sleep(3)
print('Locking arguments in...')
for i in range(5):
    print(str(5-i) + '...')
    time.sleep(1)
print('\n\nProceeding with grid submission...\n')
time.sleep(1)


# Clear any previous scripts and create the new grid scripts
os.system('rm submit_grid_job.sh')
os.system('rm grid_job.sh')
os.system('rm run_container_job.sh')
time.sleep(1)
h.submit_PrintDQ(scratch_path, output_path, data_path, TA_tar_name)
h.grid_PrintDQ(user, TA_tar_name, TA_folder, scratch_path)
h.container_PrintDQ(TA_folder, scratch_path)
time.sleep(1)

# submit grid jobs
for i in range(len(available_runs)):
    os.system('sh submit_grid_job.sh ' + available_runs[i])
    print('\n# # # # # # # # # # # # # # # # # # # # #')
    print('Run ' + available_runs[i] + ' sent')
    print('# # # # # # # # # # # # # # # # # # # # #\n')
    time.sleep(1)


# finish up
print('\nAll runs', available_runs, 'sent!\n')
time.sleep(1)
print('Exiting...\n')
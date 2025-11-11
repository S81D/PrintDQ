# Creation script to produce PrintDQ grid scripts + some helper functions
# Author: Steven Doran

import os

# submission script
def submit_PrintDQ(scratch_path, output_path, data_path, TA_tar_name):

    # job resources
    lifetime = str(6)        # hr
    mem = str(4000)          # MB
    # disk space calculated dynamically (below)

    print('\nResource allocation per job:')             
    print('   - lifetime   = ' + lifetime + 'hr')
    print('   - memory     = ' + mem + 'MB')

    file = open(scratch_path + '/submit_grid_job.sh', "w")

    file.write('#!/bin/bash\n')
    file.write('# Job submission script for PrintDQ toolchain\n')
    file.write('# Author: Steven Doran\n')
    file.write('\n')

    file.write('RUN=$1\n')
    file.write('\n')
    file.write('export INPUT_PATH=' + scratch_path + '/\n')
    file.write('export OUTPUT_FOLDER=' + output_path + '/$RUN\n')
    file.write('export PROCESSED_FILES_PATH=' + data_path + '/R${RUN}/\n')
    file.write('\n')

    file.write('QUEUE=medium\n')
    file.write('\n')

    file.write('mkdir -p $OUTPUT_FOLDER\n')
    file.write('\n')

    file.write('# Create a list of part files to attach\n')
    file.write('PART_FILES=""\n')
    file.write('for FILE in ${PROCESSED_FILES_PATH}ProcessedData*; do\n')
    file.write('    PART_FILES="$PART_FILES -f $FILE"\n')
    file.write('done\n')
    file.write('\n')

    file.write('# Calculate required disk space based on input files\n')
    # dynamic disk allocation: get total size in KB, convert to GB, add buffer (5 GB)
    file.write('TOTAL_SIZE=$(du -sk ${PROCESSED_FILES_PATH}ProcessedData* 2>/dev/null | awk \'{sum+=$1} END {print sum}\')\n')
    file.write('DISK_GB=$(echo "scale=0; ($TOTAL_SIZE / 1024 / 1024) + 5" | bc)\n')
    file.write('# Set minimum disk space\n')
    file.write('if [ $DISK_GB -lt 10 ]; then\n')    # min will be 10 GB
    file.write('    DISK_GB=10\n')
    file.write('fi\n')
    file.write('echo "   - disk space = ${DISK_GB}GB"\n')
    file.write('\n')

    file.write('echo ""\n')
    file.write('echo "submitting job..."\n')
    file.write('echo ""\n')
    file.write('\n')

    file.write('jobsub_submit --memory=' + mem + 'MB --expected-lifetime=' + lifetime + 'h -G annie --disk=${DISK_GB}GB ')

    # use OFFSITE resources
    file.write('--resource-provides=usage_model=OFFSITE --blacklist=Omaha,Swan,Wisconsin,RAL ')

    file.write('$PART_FILES -f ${INPUT_PATH}/run_container_job.sh -f ${INPUT_PATH}/' + TA_tar_name + ' -d OUTPUT $OUTPUT_FOLDER ')
    file.write('file://${INPUT_PATH}/grid_job.sh PrintDQ_${RUN} \n')
    file.write('\n')

    file.write('echo "job name is: PrintDQ_${RUN}"\n')
    file.write('echo "" \n')

    file.close()

    return



# job script that will run on the cluster node
def grid_PrintDQ(user, TA_tar_name, TA_folder, scratch_path):

    file = open(scratch_path + '/grid_job.sh', "w")

    file.write('#!/bin/bash\n')
    file.write('# Author: Steven Doran\n')
    file.write('\n')
    file.write('cat <<EOF\n')
    file.write('condor   dir: $CONDOR_DIR_INPUT\n')
    file.write('process   id: $PROCESS\n')
    file.write('output   dir: $CONDOR_DIR_OUTPUT\n')
    file.write('EOF\n')
    file.write('\n')

    file.write('HOSTNAME=$(hostname -f)\n')
    file.write('GRIDUSER="' + user + '"\n')
    file.write('\n')
    file.write('# Argument passed through job submission\n')
    file.write('FIRST_ARG=$1\n')
    file.write('RUN=$(echo "$FIRST_ARG" | grep -oE \'[0-9]+\')\n')
    file.write('\n')

    file.write('# Create a dummy log file in the output directory\n')
    file.write('DUMMY_OUTPUT_FILE=${CONDOR_DIR_OUTPUT}/${FIRST_ARG}_${JOBSUBJOBID}_dummy_output\n')
    file.write('touch ${DUMMY_OUTPUT_FILE}\n')
    file.write('echo "This dummy file belongs to job ${FIRST_ARG}" >> ${DUMMY_OUTPUT_FILE} \n')
    file.write('start_time=$(date +%s)   # start time in seconds \n')
    file.write('echo "The job started at: $(date)" >> ${DUMMY_OUTPUT_FILE} \n')
    file.write('echo "" >> ${DUMMY_OUTPUT_FILE} \n')
    file.write('\n')

    file.write('echo "Files present in CONDOR_INPUT:" >> ${DUMMY_OUTPUT_FILE} \n')
    file.write('ls -lrth $CONDOR_DIR_INPUT >> ${DUMMY_OUTPUT_FILE} \n')
    file.write('echo "" >> ${DUMMY_OUTPUT_FILE} \n')
    file.write('\n')
    
    file.write('# Copy datafiles from $CONDOR_INPUT onto worker node (/srv)\n')
    file.write('${JSB_TMP}/ifdh.sh cp -D $CONDOR_DIR_INPUT/ProcessedData* .\n')
    file.write('${JSB_TMP}/ifdh.sh cp -D $CONDOR_DIR_INPUT/' + TA_tar_name + ' .\n')
    file.write('\n')

    file.write('# un-tar TA\n')
    file.write('tar -xzf ' + TA_tar_name + '\n')
    file.write('rm ' + TA_tar_name + '\n')
    file.write('\n')

    file.write('FILES_PRESENT=$(ls /srv/Processed* 2>/dev/null | wc -l)\n')
    file.write('echo "*** There are $FILES_PRESENT files here ***" >> ${DUMMY_OUTPUT_FILE}\n')
    file.write('\n')

    file.write('# Create my_inputs.txt for toolchain\n')
    file.write('ls -v /srv/Processed* >> my_inputs.txt\n')
    file.write('\n')
    
    file.write('echo "" >> ${DUMMY_OUTPUT_FILE}\n')
    file.write('echo "Processed files present:" >> ${DUMMY_OUTPUT_FILE}\n')
    file.write('ls -v /srv/Processed* >> ${DUMMY_OUTPUT_FILE}\n')
    file.write('echo "" >> ${DUMMY_OUTPUT_FILE}\n')
    file.write('\n')

    file.write('echo "Make sure singularity is bind mounting correctly (ls /cvmfs/singularity)" >> ${DUMMY_OUTPUT_FILE}\n')
    file.write('ls /cvmfs/singularity.opensciencegrid.org >> ${DUMMY_OUTPUT_FILE}\n')
    file.write('\n')
    file.write('# Setup singularity container\n')
    file.write('singularity exec -B/srv:/srv /cvmfs/singularity.opensciencegrid.org/anniesoft/toolanalysis:latest/ $CONDOR_DIR_INPUT/run_container_job.sh $RUN\n')
    file.write('\n')
    file.write('# ------ The script run_container_job.sh will now run within singularity ------ #\n')
    file.write('\n')

    file.write('# cleanup and move files to $CONDOR_OUTPUT after leaving singularity environment\n')
    file.write('echo "Moving the output files to CONDOR OUTPUT..." >> ${DUMMY_OUTPUT_FILE}\n')
    file.write('${JSB_TMP}/ifdh.sh cp -D /srv/logfile*.txt $CONDOR_DIR_OUTPUT     # log files\n')
    file.write('${JSB_TMP}/ifdh.sh cp -D /srv/*.csv $CONDOR_DIR_OUTPUT            # Modify: any .root files etc.. that are produced from your toolchain\n')
    file.write('\n')
    file.write('echo "" >> ${DUMMY_OUTPUT_FILE}\n')
    file.write('echo "Input:" >> ${DUMMY_OUTPUT_FILE}\n')
    file.write('ls $CONDOR_DIR_INPUT >> ${DUMMY_OUTPUT_FILE}\n')
    file.write('echo "" >> ${DUMMY_OUTPUT_FILE}\n')
    file.write('echo "Output:" >> ${DUMMY_OUTPUT_FILE}\n')
    file.write('ls $CONDOR_DIR_OUTPUT >> ${DUMMY_OUTPUT_FILE}\n')
    file.write('\n')
    file.write('echo "" >> ${DUMMY_OUTPUT_FILE}\n')
    file.write('echo "Cleaning up..." >> ${DUMMY_OUTPUT_FILE}\n')
    file.write('echo "srv directory:" >> ${DUMMY_OUTPUT_FILE}\n')
    file.write('ls -v /srv >> ${DUMMY_OUTPUT_FILE}\n')
    file.write('\n')
    file.write('# make sure to clean up the files left on the worker node\n')
    file.write('rm /srv/Processed*\n')
    file.write('rm /srv/*.txt\n')
    file.write('rm /srv/*.csv\n')
    file.write('rm /srv/*.sh\n')
    file.write('rm -rf /srv/' + TA_folder + '\n')
    file.write('\n')

    file.write('end_time=$(date +%s) \n')
    file.write('echo "Job ended at: $(date)" >> ${DUMMY_OUTPUT_FILE} \n')
    file.write('echo "" >> ${DUMMY_OUTPUT_FILE} \n')
    file.write('duration=$((end_time - start_time)) \n')
    file.write('echo "Script duration (s): ${duration}" >> ${DUMMY_OUTPUT_FILE} \n')
    file.write('\n')
    file.write('### END ###\n')

    file.close()

    return


# job that executes within our container
def container_PrintDQ(TA_folder, scratch_path):

    file = open(scratch_path + '/run_container_job.sh', "w")

    file.write('#!/bin/bash\n')
    file.write('# Steven Doran\n')
    file.write('\n')

    file.write('RUN=$1\n')
    file.write('\n')
    
    file.write('# logfile\n')
    file.write('touch /srv/logfile_${RUN}.txt\n')
    file.write('pwd >> /srv/logfile_${RUN}.txt\n')
    file.write('ls -v >> /srv/logfile_${RUN}.txt\n')
    file.write('echo "" >> /srv/logfile_${RUN}.txt\n')
    file.write('\n')

    file.write('# place the input file containing the necessary data files in the toolchain\n')
    file.write('rm /srv/' + TA_folder + '/configfiles/PrintDQ/my_inputs.txt\n')
    file.write('\cp /srv/my_inputs.txt /srv/' + TA_folder + '/configfiles/PrintDQ/\n')
    file.write('\n')

    file.write('# enter ToolAnalysis directory\n')
    file.write('cd ' + TA_folder + '/\n')
    file.write('\n')

    file.write('# set up paths and libraries\n')
    file.write('source Setup.sh\n')
    file.write('\n')

    file.write('# Run the toolchain, and output verbose to log file\n')
    file.write('./Analyse configfiles/PrintDQ/ToolChainConfig >> /srv/logfile_${RUN}.txt 2>&1 \n')
    file.write('\n')

    file.write('# log files\n')
    file.write('echo "" >> /srv/logfile_${RUN}.txt\n')
    file.write('echo "**************************************************" >> /srv/logfile_${RUN}.txt\n')
    file.write('echo "" >> /srv/logfile_${RUN}.txt\n')
    file.write('echo "ToolAnalysis directory contents:" >> /srv/logfile_${RUN}.txt\n')
    file.write('ls -lrth >> /srv/logfile_${RUN}.txt\n')
    file.write('\n')

    file.write('# copy any produced files to /srv for extraction\n')
    file.write('cp *.csv /srv/\n')
    file.write('\n')
    file.write('# make sure any output files you want to keep are put in /srv or any subdirectory of /srv\n')
    file.write('\n')
    file.write('### END ###\n')

    file.close()



# Ask user for runs you would like to include
def get_runs_from_user():
    runs = []
    which_option = input("Read from a list (runs.list) or enter the runs manually?\nType '1' for the list, type '2' for manual submission:   ")
    if which_option == '1':
        try:
            with open('runs.list', 'r') as file:
                for line in file:
                    run = line.strip()
                    if run:  # Ensure the line is not empty
                        runs.append(run)
            print("Runs added from runs.list")
        except FileNotFoundError:
            print("\nError: 'runs.list' file not found. Please create the list file and re-run the script.\n")
            exit()
    elif which_option == '2':
        print("Enter the runs you want to include. Type 'done' when you are finished.")
        while True:
            user_input = input("Enter run number: ")
            if user_input.lower() == 'done':
                break
            runs.append(user_input)
    else:
        print("\nError: please type '1' or '2'! Exiting...\n")
        exit()
    return runs



# Check if there isn't ProcessedData for any of the runs and omit that run from the list
def is_there_data(runs_to_run_user, data_path):
    temp_runs = []
    for i in range(len(runs_to_run_user)):
        if os.path.isdir(data_path + 'R' + runs_to_run_user[i] + '/'):
            temp_runs.append(runs_to_run_user[i])
        else:
            print('Run ' + runs_to_run_user[i] + ' was not processed!!! Removing from the list')
    return temp_runs





    















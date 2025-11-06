import os
from glob import glob

# Check PrintDQ processing status against ProcessedData
# Author: Steven Doran

# Output will be:
#         [run number] [(run type)] [total processed part files] [PrintDQ status]
#  

##########################################################################################

run_to = 'current'                  # the script will show runs up to this one (set to 'current' to display latest runs)

run_back = 5300                # the script will only check runs this far back

                               # for now, the PrintDQ is only designed for beam runs, but keep this functionality in case the tool is ever expanded
run_type = 'beam'              # specify run type you would like to check ('beam', 'LED', 'cosmic', 'laser', 'AmBe')

min_part_size = 3              # only check for runs with atleast this many part files


# modify accordingly
rawdata_path = '/pnfs/annie/persistent/raw/raw/'
prodata_path = '/pnfs/annie/persistent/processed/processed_EBV2/'
printdq_path = '/pnfs/annie/persistent/processed/PrintDQ_metrics/'

# you need to create this file (see README) before executing
SQL_path = 'ANNIE_SQL_RUNS.txt'

##########################################################################################

# define color codes for text output
RESET = "\033[0m"                      # white = PrintDQ file exists
RED = "\033[91m"                       # red = PrintDQ file not present
GREEN = "\033[92m"                     # green = PrintDQ complete (for emphasis if needed)
DARK_GRAY = "\033[90m"                 # gray = ProcessedData not available


# from run type name, get number
def get_run_type(run_type):
    if run_type == 'beam':
        return ['3', '34', '39']
    elif run_type == 'cosmic':
        return ['7', '37']
    elif run_type == 'LED':
        return ['1', '35']
    elif run_type == 'AmBe':
        return ['4', '43', '42', '41', '36']
    elif run_type == 'laser':
        return ['8', '44', '40']


# grab the run types from the SQL file
def read_SQL(SQL_file, run_back, run_type):
    
    run_data = {}

    # check if the SQL file exists
    if not os.path.isfile(SQL_file):
        print(f"\nERROR: The SQL file '{SQL_file}' does not exist. Please follow the README and generate an SQL txt file.\nExiting...\n")
        exit()

    # read the SQL file, get the run numbers and the run type
    with open(SQL_file, 'r') as file:
        lines = file.readlines()[2:] 
        for line in lines:
            columns = [col.strip() for col in line.split('|')]
            if len(columns) > 1:
                runnum = columns[1]
                runconfig = columns[5]   # run type

            # 'current' means we don't want a "ceiling" on the runs we display
            if run_to == 'current':
                if int(runnum) >= int(run_back) and runconfig in run_type:
                    run_data[runnum] = int(runconfig) if runconfig.isdigit() else None
            else:
                if int(run_to) >= int(runnum) >= int(run_back) and runconfig in run_type:    
                    run_data[runnum] = int(runconfig) if runconfig.isdigit() else None

    return run_data


def check_printdq_status(sql, rawdata_path, prodata_path, printdq_path):

    # column header
    print(f"{'RUN':<3} {'TYPE':<2} {'PRO':<3} STATUS")
    print('-' * 25)

    for run_number, run_type in sql.items():

        raw_run_folder = os.path.join(rawdata_path, run_number)
        processed_run_folder = os.path.join(prodata_path, f"R{run_number}")
        printdq_file = os.path.join(printdq_path, f"R{run_number}_PrintDQ.csv")

        # check if RAWDATA folder exists
        if not os.path.isdir(raw_run_folder):
            continue

        # count part files in RAWDATA
        raw_files = glob(os.path.join(raw_run_folder, f"RAWDataR{run_number}S0p*"))
        num_raw_files = len(raw_files)

        # skip the very small runs
        if num_raw_files < min_part_size:
            continue

        # check if PROCESSED folder exists
        if not os.path.isdir(processed_run_folder):
            print(f"{DARK_GRAY}{run_number:>4} {run_type:>2} {'':>4} NO PROCESSED DATA{RESET}")
            continue

        # count part files in PROCESSED data
        processed_files = glob(os.path.join(processed_run_folder, f"ProcessedData*R{run_number}S0p*"))
        num_processed_files = len(processed_files)

        # check if no processed files exist
        if num_processed_files == 0:
            print(f"{DARK_GRAY}{run_number:>4} {run_type:>2} {0:>4} NO PROCESSED DATA{RESET}")
            continue

        # check if PrintDQ file exists
        if not os.path.exists(printdq_file):
            print(f"{RED}{run_number:>4} {run_type:>2} {num_processed_files:>4} PRINTDQ NOT PRESENT{RESET}")
            continue

        # PrintDQ file exists
        print(f"{run_number:>4} {run_type:>2} {num_processed_files:>4} PRINTDQ COMPLETE")

          
print('\n')
run_type_list = get_run_type(run_type)
sql = read_SQL(SQL_path, run_back, run_type_list)
check_printdq_status(sql, rawdata_path, prodata_path, printdq_path)
print('\n')

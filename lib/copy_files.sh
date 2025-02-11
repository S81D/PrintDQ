#!/bin/bash
# script to transfer .csv files created from the PrintDQ toolchain to the persistent/ area
# Steven Doran

username=<user>    # edit accordingly

data_path=/pnfs/annie/persistent/processed/PrintDQ_metrics/
output_path=/pnfs/annie/scratch/users/${username}/output/PrintDQ/    # you may need to create an output/PrintDQ/ scratch folder if not already present, or edit accordingly

# Overwrite not enabled for ifdh cp - skip the file if it exists in /persistent
file_exists() {
    if [ -e "$1" ]; then
        return 0  # File exists
    else
        return 1  # File does not exist
    fi
}

# setup transfer
source /cvmfs/fermilab.opensciencegrid.org/products/common/etc/setup
setup ifdhc v2_5_4

echo ""
echo "Transferring PrintDQ .csv files..."
echo ""

# Search the output_path for all .csv files and transfer them to data_path if they do not exist there (weren't previously transferred)
for run_folder in "$output_path"*/; do
    
    run_number=$(basename "$run_folder")           # grab the run number
    
    csv_file="R${run_number}_PrintDQ.csv"          # build the expected .csv file name
    source_file="${run_folder}${csv_file}"
    destination_file="${data_path}${csv_file}"

    if [ -e "$source_file" ]; then                 # check if the .csv file exists in output_path

        if file_exists "$destination_file"; then   # check if it is already present in data_path; if so, skip. If not, initiate transfer
            echo "$csv_file already exists in $data_path. Skipping..."
        else
            echo "Transferring $csv_file to $data_path..."
            ifdh cp "$source_file" "$data_path/"
        fi
    else
        echo "No .csv file found for run $run_number. Skipping..."
    fi
done

echo ""
echo "Transfer complete."
echo ""

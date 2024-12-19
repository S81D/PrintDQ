# PrintDQ

Scripts to run the `PrintDQ` toolchain on the grid and create run metric plots.

-----------------------

### Contents:
- `main.py` sends jobs to the grid.
- `lib/` folder contains helper scripts.
- `helper.py` contains functions that are called by `main.py`.
- `tarball_create_script.py` will tar-ball your local copy of ToolAnalysis in preparation for grid submission.
- `copy_files.sh` will copy .csv files deposited by the grid jobs to `persistent/`.

### Usage:

For grid submission:

1. Compile ToolAnalysis from the main repository (https://github.com/ANNIEsoft/ToolAnalysis/tree/Application) within your `/exp/annie/app/<user>/` area. The grid scripts will be run the `PrintDQ` toolchain.
2. Clone a copy of this repo to your user directory in ```/pnfs/annie/scratch/users/<username>/```.
3. Once your ToolAnalysis directory is fully built and works, run ```python3 lib/tarball_create_script.py``` to create a tarball of ToolAnalysis to be run on the grid. Make sure to modify path and folder names within the script accordingly.
4. Edit ```main.py``` to reflect your username, the name of your ToolAnalysis folder, the name of the ToolAnalysis tarball, and the output location for the grid jobs. Ensure the output area for your grid jobs has been created.
5. One of the arguments ```main.py``` will take from the user is a list of the beam runs they wish to submit. These run numbers can either be provided one at a time to the script while running it, or the user can populate a `runs.list` file beforehand with the approprate runs. IF you plan on using the list file, please populate that file prior to running `main.py`. 
6. Run the the main script: ```python3 main.py``` to submit the grid jobs. The script will confirm your username, then ask if you are submitting the runs via list file or manually (one at a time). If providing a list the script will continue and automatically submit your jobs. If submitting the runs manually, you will need to provide the run numbers one at a time. The script will terminate once all jobs are sent.
7. After job outputs are returned, you can run `sh lib/copy_files.sh` to transfer the created .csv files to `persistent/` for storage and future analysis. The script will automatically sort and transfer the files depending on if they are present in the `persistent/` area.

-----------------------

### Additional information

- The `PrintDQ` toolchain often takes a very long time on certain part files. This will sometimes lead to jobs hanging, depending on the grid resources. Ordinarily, the toolchain can be run quickly (< 10 min) over ~hundreds of part files. In other cases, a single part file may take > 10 min. To be safe, a large resource allocation is requested for each job. The `ClusterFinder` tool is the primary culprit for any long run times, and occasionally will reach an event in a particular part file that takes extremely long to process (for whatever reason). The larger resource allocation also accounts for copying hundreds of part files for a given run, which takes time + disk space.

-----------------------

To check on your jobs, use: ```jobsub_q -G annie --user <<username>>```

To cancel job submissions, use: ```jobsub_rm -G annie <<username>>```

To check why jobs are held, use: ```jobsub_q --hold -G annie <<username>>```

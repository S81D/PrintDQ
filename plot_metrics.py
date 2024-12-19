print('\nLoading...\n')
import os
import re
import csv
from PIL import Image
import matplotlib.pyplot as plt
import matplotlib as mpl
font = {'family' : 'serif', 'size' : 12 }
mpl.rc('font', **font)
mpl.rcParams['mathtext.fontset'] = 'cm' # Set the math font to Computer Modern
mpl.rcParams['legend.fontsize'] = 1

# ------------------------------------------------------- #

# Produce run metric plots using the PrintDQ .csv files
# Author: Steven Doran

csv_dir = '/pnfs/annie/persistent/processed/PrintDQ_metrics'
plot_dir = 'DQ_plots/'
PDF_name = 'Run_Metrics.pdf'

# ------------------------------------------------------- #

os.system('mkdir -p ' + plot_dir)

def extract_metrics(directory):

    all_metrics = []
    
    for filename in os.listdir(directory):
        if filename.endswith(".csv"):

            # extract run number
            match = re.match(r"R(\d+)_PrintDQ\.csv", filename)
            run_number = int(match.group(1))

            filepath = os.path.join(directory, filename)
            print(f"Processing file: {filename}")
            
            # construct dict to hold run number, metric name, number of counts, rate, and rate error
            with open(filepath, 'r') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    metric = row.get("Metric", "").strip()
                    count = row.get("Counts", "").strip()
                    rate = row.get("Rate (%)", "").strip()
                    rate_error = row.get("Rate Error (+/- %)", "").strip()
                    if metric: 
                        all_metrics.append({
                            "Run Number": run_number,
                            "Metric": metric,
                            "Counts": int(count),
                            "Rate": float(rate),
                            "Rate Error": float(rate_error)
                        })

    return all_metrics



def plot_figure(run_numbers, metric, rate, error, color, ylim, nominal, nominal_val, plots_dir):

    plt.figure(figsize=(12, 6))
    plt.errorbar(run_numbers, rate, yerr = error, color = color, 
            fmt='o', markersize=3, linestyle='None', label=metric, zorder = 10)
    
    # some figures could benefit with a dashed line at 100% or some other value
    if nominal:
        plt.axhline(nominal_val, linestyle = 'dashed', color = 'k', zorder = 1)
    
    plt.ylim(ylim)
    plt.title(metric)
    plt.xlabel('Run Number')
    
    if metric == 'Cluster per Event':
        plt.ylabel(metric)
    else:
        plt.ylabel(metric + ' rate (%)')
    
    plt.savefig(plots_dir + metric + '_plot.png', 
            dpi=300,bbox_inches='tight',pad_inches=.3,facecolor = 'w')
    plt.close()



def png_to_pdf(plot_dir, output_pdf):
    
    png_files = [f for f in os.listdir(plot_dir) if f.endswith('.png')]
    images = []
    
    for file in png_files:
        file_path = os.path.join(plot_dir, file)
        with Image.open(file_path) as img:
            images.append(img.convert('RGB'))

    if images:
        images[0].save(plot_dir + output_pdf, save_all=True, append_images=images[1:])


# ------------------------------------------------------- #

metrics_data = extract_metrics(csv_dir)

# ------------------------------------------------------- #

# for each quantity, plot

# grab all metric names
metrics = set(metric['Metric'] for metric in metrics_data)
colors = ['grey', 'navy', 'blue', 'indianred', 'darkorange', 'purple', '#B8860B',
           'dodgerblue', 'red', 'tomato', 'darkgreen', 'steelblue', 'green', 'darkred']

print('\n')
count = 0
for metric_name in metrics:

    if metric_name != 'Total Events':

        print(metric_name, colors[count])

        run_numbers = []
        rate = []
        error = []
        
        for metric in metrics_data:
            if metric['Metric'] == metric_name:
                run_numbers.append(metric['Run Number'])
                rate.append(metric['Rate'])
                error.append(metric['Rate Error'])

        nominal=False; nominal_val = 0

        if metric_name == 'Beam OK' or metric_name == 'Has BRF Fit':
            ylim=(-5, 105)
            nominal=True; nominal_val = 100
        elif metric_name == 'EventTimeTank = 0':
            ylim=(3.5,-0.05)
            nominal=True; nominal_val = 0
        elif metric_name == 'Has LAPPD Data':
            ylim=(-0.5,15)
        elif metric_name == 'Extended (CC)':
            ylim=(-0.1,2.5)
        elif metric_name == 'Extended (NC)':
            ylim=(-0.02,0.7)
        elif metric_name == 'Ext Clusters' or metric_name == 'Prompt Clusters' or metric_name == 'Spill Clusters':
            ylim=(-5,105)
        elif metric_name == '1 MRD Track':
            ylim=(-0.05,0.45)
        elif metric_name == 'Tank+MRD Coinc':
            ylim=(-0.05,0.8)
        elif metric_name == 'Tank+Veto Coinc':
            ylim=(-0.05,1.25)
        elif metric_name == 'Tank+MRD+Veto Coinc':
            ylim=(-0.02,0.35)
        elif metric_name == 'Total Clusters (rate given as clusters / event)':
            plot_figure(
                run_numbers=run_numbers,
                metric='Cluster per Event',
                rate=rate,
                error=error,
                color=colors[count],
                ylim=(-0.05, 1),
                nominal=False,
                nominal_val=0,
                plots_dir=plot_dir
            )
            count += 1
            continue

        plot_figure(
                run_numbers=run_numbers,
                metric=metric_name,
                rate=rate,
                error=error,
                color=colors[count],
                ylim=ylim,
                nominal=nominal,
                nominal_val=nominal_val,
                plots_dir=plot_dir
            )

        count += 1


# lastly, combine .pngs into a PDF
png_to_pdf(plot_dir, PDF_name)

print('\n\n*** Plots saved to ' + plot_dir + ' ***')
print('\ndone\n')
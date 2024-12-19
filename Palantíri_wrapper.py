"""
Created on Wed Nov  6 23:15:17 2024

@author: Siva Kumar Valluri
"""
from PalantíriGUI import PalantíriGUI
from Palantíri import Palantíri
import tkinter as tk
import itertools
import pandas as pd
import numpy as np


# Main function to run the GUI that allows user to input details
def Stone_of_Avallónë(): #The master stone that 'communicates' with Elendil's 7 palantiri 
    root = tk.Tk()
    gui = PalantíriGUI(root)
    root.mainloop()
    # Return the gathered values for use by other scripts (from PalantíriGUI  to Palantíri)
    return gui.address_set, gui.name_set, gui.sample_name, gui.delays, gui.exposures, gui.SIMX_frames

address_set, name_set, sample_name, delays, exposures, SIMX_frames = Stone_of_Avallónë()
#pages_intensity = []
pages_coverage = []
pages_mean_intensity = []
for addresses, name  in itertools.zip_longest(address_set, name_set):
    Ithil_stone = Palantíri(addresses, name, delays, exposures, SIMX_frames) # "Sauruman's corrupted stone"
    Ithil_stone.ósanwë()                              # showcase all 8 static and emission images 
    #df_pixel_intensities, df_mean_intensities = Ithil_stone.silivros()
    _, df_mean_intensities = Ithil_stone.silivros()   # pixel intensities within particles as a function of time
    df_areas_by_threshold  = Ithil_stone.wathar()     # area covered by emission as a function of time
    plotting_time, error = Ithil_stone.lúmëa()        # plotting detail referencing time in nanoseconds
    #pages_intensity.append(df_pixel_intensities)
    pages_coverage.append(df_areas_by_threshold)
    pages_mean_intensity.append(df_mean_intensities)


"""
Saving raw emission coverage and pixel average intensities for each run as a function of time
"""
# Combine pages_mean_intensity data
mean_intensity_data = pd.DataFrame()
for df, name in zip(pages_mean_intensity, name_set):
    # Transpose each DataFrame, reset the index, and rename columns
    df_transposed = df.T
    df_transposed.insert(0, "time", df_transposed.index)  # Insert "time" as the first column
    # Convert the "time" column to string and remove "ns" suffix if present
    df_transposed["time"] = df_transposed["time"].astype(str).str.replace("ns", "").str.strip()    
    # Rename the columns: keep the first as "time", and rename the rest with the sheet name
    df_transposed.columns = ["time"] + [f"{name}"]
    
    # Merge with the main DataFrame on "time"
    if mean_intensity_data.empty:
        mean_intensity_data = df_transposed
    else:
        mean_intensity_data = pd.merge(mean_intensity_data, df_transposed, on="time", how="outer")

# Save the data to a text file for origin 
mean_intensity_data.to_csv(f"{sample_name}_mean_intensity_summary.txt", sep="\t", index=False)
print("Emission intensity processed and saved successfully.")

coverage_100_data = pd.DataFrame()
for df, name in zip(pages_coverage, name_set):
    # Merge with the main DataFrame on "time"
    th_100 = df.loc[:,100].values
    df_dummy = pd.DataFrame()
    df_dummy.insert(0, "time", df.index)
    df_dummy.insert(1, f"{name}", th_100)
    if coverage_100_data.empty:
        coverage_100_data = df_dummy
    else:
        coverage_100_data = pd.merge(coverage_100_data, df_dummy, on="time", how="outer")

# Save the data to a text file for origin 
coverage_100_data.to_csv(f"{sample_name}_coverage_threshold_summary.txt", sep="\t", index=False)
print("Coverage processed and saved successfully.")


"""
Binning by 'particle' size
"""

# Loop to ensure the user provides a valid response for binning
while True:
    user_response = input("Do you want to bin? (yes/no): ").strip().lower()
    if user_response in ["y", "yes", "yippi ka yay", "ok", "sure", "yeah", "yup", "ná", "na"]:
        binning = True
        print("Get your particle diameters (in microns) ready for all runs.")
        bins = [ 1.15**x for x in range(25, 48,1)]
        rep_diameter = [(bins[i]+bins[i+1])/2 for i in range(0, len(bins)-1, 1)]

        break
    elif user_response in ["n", "no","nope","nada"]:
        binning = False
        print("~Metta~")
        break
    else:
        print("Invalid input. Please enter one of the following: yes, no.")
    

if binning:
    particle_sizes = {}
    #taking particle sizes
    for run in name_set:
        while True:
            try:
                # Prompt user for particle size for each sheet
                particle_size = input(f"Enter diameter for run-{run} (in microns): ")
                
                # Try to convert the input to a float
                particle_size = float(particle_size)
                
                # If successful, store the value and break the loop
                particle_sizes[run] = particle_size
                break
            except ValueError:
                print("Invalid input. Please enter a numeric value.")
                
    # Binning data according to the particle sizes
    binned_data = {rep: [] for rep in rep_diameter}
    binned_data2 = {rep: [] for rep in rep_diameter}
    # Loop through each run and assign data to the correct bin based on particle size
    for run, size in particle_sizes.items():
        # Find the appropriate bin for the current particle size
        for i in range(len(bins) - 1):
            if bins[i] <= size < bins[i + 1]:
                # Append the data from the current run to the corresponding bin
                if run in mean_intensity_data.columns:
                    binned_data[rep_diameter[i]].append(mean_intensity_data[run])
                    binned_data2[rep_diameter[i]].append(coverage_100_data[run])
                break

    # Initialize an empty DataFrame to store the binned averages
    df_binned_intensities = pd.DataFrame(index=mean_intensity_data['time'])
    for column, binned_values in binned_data.items():
        if not binned_values:  # If binned_values is empty, skip it
            #print(f"Skipping column '{column}' because it contains no data.")
            continue
    
        # Check if each sublist is non-empty and consistent in length
        if any(len(sublist) != len(binned_values[0]) for sublist in binned_values):
            #print(f"Skipping column '{column}' due to inconsistent sublist lengths.")
            continue
    
        # Calculate the average for each index across sublists
        averages = [sum(values) / len(values) for values in zip(*binned_values)]
    
        # Calculate the mean absolute deviation for each index across sublists
        mean_absolute_deviation = [sum(abs(value - avg) for value in values) / len(values) for values, avg in zip(zip(*binned_values), averages)]
        
        if len(averages) == len(df_binned_intensities.index):
            # Assign the average values and MAD to the DataFrame
            df_binned_intensities[round(column,2)] = averages
            df_binned_intensities[str(round(column,2)) + '_MAD'] = mean_absolute_deviation
        else:
            print(f"Skipping column '{column}' due to mismatch between averages length and DataFrame index length.")

    # Save the binned data to a text file
    df_binned_intensities.to_csv(f"{sample_name}_binned_mean_intensity_summary.txt", sep="\t", index=True)
    print("Binned data processed and saved successfully.")          

    # Initialize an empty DataFrame to store the binned averages
    df_binned_coverage = pd.DataFrame(index=mean_intensity_data['time'])
    for column, binned_values in binned_data2.items():
        if not binned_values:  # If binned_values is empty, skip it
            #print(f"Skipping column '{column}' because it contains no data.")
            continue
    
        # Check if each sublist is non-empty and consistent in length
        if any(len(sublist) != len(binned_values[0]) for sublist in binned_values):
            #print(f"Skipping column '{column}' due to inconsistent sublist lengths.")
            continue
    
        # Calculate the average for each index across sublists
        averages = [sum(values) / len(values) for values in zip(*binned_values)]
    
        # Calculate the mean absolute deviation for each index across sublists
        mean_absolute_deviation = [sum(abs(value - avg) for value in values) / len(values) for values, avg in zip(zip(*binned_values), averages)]
        
        if len(averages) == len(df_binned_intensities.index):
            # Assign the average values and MAD to the DataFrame
            df_binned_coverage[round(column,2)] = averages
            df_binned_coverage[str(round(column,2)) + '_MAD'] = mean_absolute_deviation
        else:
            print(f"Skipping column '{column}' due to mismatch between averages length and DataFrame index length.")

    # Save the binned data to a text file
    df_binned_coverage.to_csv(f"{sample_name}_binned_coverage_summary.txt", sep="\t", index=True)
    print("Binned data processed and saved successfully.")  


"""
Created on Wed Nov  6 20:16:48 2024

@author: Siva Kumar Valluri
"""
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import os

class PalantíriGUI:

    def __init__(self, master):
        self.master = master
        self.master.title("Palantír of Avallónë")
        self.master.configure(bg="#2e3b55")
        
        # Folder path variable
        self.folder_path = tk.StringVar()
        
        # SIMX frames variable with default
        self.simx_frames = tk.StringVar(value="8")
        
        # Capture contiguity and exposure consistency choices
        self.capture_contiguous = tk.StringVar(value="y")
        self.exposure_same = tk.StringVar(value="y")

        # Browse button and folder selection
        #tk.Label(master, text="Select folder with SIMX images:", bg="#2e3b55", fg="white", font=("Helvetica", 12, "bold")).grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.folder_entry = tk.Entry(master, textvariable=self.folder_path, width=40, state="readonly", font=("Helvetica", 10))
        self.folder_entry.grid(row=0, column=0, padx=10, pady=10)
        self.browse_button = tk.Button(master, text="Browse", command=self.select_folder, bg="#4c5c79", fg="white", font=("Helvetica", 10, "bold"))
        self.browse_button.grid(row=0, column=1, padx=10, pady=10)
        
        # SIMX Frames selection
        tk.Label(master, text="SIMX frame count (4 or 8):", bg="#2e3b55", fg="white", font=("Helvetica", 12, "bold")).grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.frames_dropdown = tk.OptionMenu(master, self.simx_frames, "4", "8")
        self.frames_dropdown.config(bg="#4c5c79", fg="white", font=("Helvetica", 10, "bold"))
        self.frames_dropdown.grid(row=1, column=1, padx=10, pady=10, sticky="w")
        
        # Capture contiguity selection
        tk.Label(master, text="Is the capture contiguous?:", bg="#2e3b55", fg="white", font=("Helvetica", 12, "bold")).grid(row=2, column=0, padx=10, pady=10, sticky="w")
        self.capture_dropdown = tk.OptionMenu(master, self.capture_contiguous, "y", "n")
        self.capture_dropdown.config(bg="#4c5c79", fg="white", font=("Helvetica", 10, "bold"))
        self.capture_dropdown.grid(row=2, column=1, padx=10, pady=10, sticky="w")
        
        # Exposure consistency selection
        tk.Label(master, text="Is the exposure same for all?:", bg="#2e3b55", fg="white", font=("Helvetica", 12, "bold")).grid(row=3, column=0, padx=10, pady=10, sticky="w")
        self.exposure_dropdown = tk.OptionMenu(master, self.exposure_same, "y", "n")
        self.exposure_dropdown.config(bg="#4c5c79", fg="white", font=("Helvetica", 10, "bold"))
        self.exposure_dropdown.grid(row=3, column=1, padx=10, pady=10, sticky="w")
        
        # Submit button centered in the window
        self.submit_button = tk.Button(master, text="Submit", command=self.submit, bg="#4c5c79", fg="white", font=("Helvetica", 12, "bold"))
        self.submit_button.grid(row=4, column=0, columnspan=3, pady=20)
        
        # Variables to store final values for use in other scripts
        self.address = None
        self.SIMX_frames = None
        self.choice1 = None
        self.choice2 = None
        self.exposures = []
        self.delays = []

        # Handle window close using the 'X' icon
        self.master.protocol("WM_DELETE_WINDOW", self.close_window)

    def select_folder(self):
        folder_selected = filedialog.askdirectory(title="Select Folder with SIMX Images")
        if folder_selected:
            self.folder_path.set(folder_selected)

    def submit(self):
        # Retrieve and validate folder selection
        self.address = self.folder_path.get()
        if not self.address:
            messagebox.showerror("Error", "You must select a folder!")
            return

        # Retrieve and validate SIMX frames
        self.SIMX_frames = self.simx_frames.get()
        if self.SIMX_frames not in ["4", "8"]:
            messagebox.showerror("Error", "Invalid input! SIMX frames can only be '4' or '8'.")
            return

        # Retrieve choices for exposure consistency and capture contiguity
        self.choice1 = self.exposure_same.get().lower()
        self.choice2 = self.capture_contiguous.get().lower()

        # Close the initial window
        self.master.destroy()
        
        # Open the next frame for additional details
        self.open_additional_details()

    def open_additional_details(self):
        # Create a new window for additional details
        new_window = tk.Tk()
        new_window.title("Palantír of Avallónë ósanwe")
        new_window.configure(bg="#2e3b55")

        # Determine which frame to show based on capture contiguity and exposure consistency
        if self.choice1 == "n" and self.choice2 == "n":
            self.create_frame_2a(new_window)
        elif self.choice1 == "y" and self.choice2 == "n":
            self.create_frame_2b(new_window)
        elif self.choice1 == "n" and self.choice2 == "y":
            self.create_frame_2c(new_window)
        else:
            self.create_frame_2d(new_window)

        new_window.mainloop()

    def create_frame_2a(self, window):
        # Frame 2a - Capture not contiguous and exposure not same
        tk.Label(window, text="Delays", bg="#2e3b55", fg="white", font=("Helvetica", 12, "bold")).grid(row=0, column=0, padx=10, pady=10)
        tk.Label(window, text="Exposures", bg="#2e3b55", fg="white", font=("Helvetica", 12, "bold")).grid(row=0, column=2, padx=10, pady=10)
        
        self.delays = []
        self.exposures = []
        for i in range(int(self.SIMX_frames)):
            delay_entry = tk.Entry(window, width=10, font=("Helvetica", 10))
            delay_entry.grid(row=i+1, column=0, padx=5, pady=5)
            tk.Label(window, text="ns", bg="#2e3b55", fg="white").grid(row=i+1, column=1, padx=5, pady=5)
            self.delays.append(delay_entry)

            exposure_entry = tk.Entry(window, width=10, font=("Helvetica", 10))
            exposure_entry.grid(row=i+1, column=2, padx=5, pady=5)
            tk.Label(window, text="ns", bg="#2e3b55", fg="white").grid(row=i+1, column=3, padx=5, pady=5)
            self.exposures.append(exposure_entry)

        tk.Button(window, text="Submit", command=lambda: self.collect_and_close(window), bg="#4c5c79", fg="white", font=("Helvetica", 12, "bold")).grid(row=int(self.SIMX_frames)+1, column=0, columnspan=4, pady=20)

    def create_frame_2b(self, window):
        # Frame 2b - Capture not contiguous and exposure same
        tk.Label(window, text="Delays", bg="#2e3b55", fg="white", font=("Helvetica", 12, "bold")).grid(row=0, column=0, padx=10, pady=10)
        tk.Label(window, text="Exposures", bg="#2e3b55", fg="white", font=("Helvetica", 12, "bold")).grid(row=0, column=2, padx=10, pady=10)
        
        self.delays = []
        for i in range(int(self.SIMX_frames)):
            delay_entry = tk.Entry(window, width=10, font=("Helvetica", 10))
            delay_entry.grid(row=i+1, column=0, padx=5, pady=5)
            tk.Label(window, text="ns", bg="#2e3b55", fg="white").grid(row=i+1, column=1, padx=5, pady=5)
            self.delays.append(delay_entry)
        
        exposure_entry = tk.Entry(window, width=10, font=("Helvetica", 10))
        exposure_entry.grid(row=1, column=2, padx=5, pady=5)
        tk.Label(window, text="ns", bg="#2e3b55", fg="white").grid(row=1, column=3, padx=5, pady=5)
        self.exposures = [exposure_entry]

        tk.Button(window, text="Submit", command=lambda: self.collect_and_close(window), bg="#4c5c79", fg="white", font=("Helvetica", 12, "bold")).grid(row=int(self.SIMX_frames)+1, column=0, columnspan=4, pady=20)

    def create_frame_2c(self, window):
        # Frame 2c - Capture contiguous and exposure not same
        tk.Label(window, text="Delays", bg="#2e3b55", fg="white", font=("Helvetica", 12, "bold")).grid(row=0, column=0, padx=10, pady=10)
        tk.Label(window, text="Exposures", bg="#2e3b55", fg="white", font=("Helvetica", 12, "bold")).grid(row=0, column=2, padx=10, pady=10)
        
        self.delays = []
        self.exposures = []
        delay_entry = tk.Entry(window, width=10, font=("Helvetica", 10))
        delay_entry.grid(row=1, column=0, padx=5, pady=5)
        tk.Label(window, text="ns", bg="#2e3b55", fg="white").grid(row=1, column=1, padx=5, pady=5)
        self.delays.append(delay_entry)

        for i in range(int(self.SIMX_frames)):
            exposure_entry = tk.Entry(window, width=10, font=("Helvetica", 10))
            exposure_entry.grid(row=i+1, column=2, padx=5, pady=5)
            tk.Label(window, text="ns", bg="#2e3b55", fg="white").grid(row=i+1, column=3, padx=5, pady=5)
            self.exposures.append(exposure_entry)

        tk.Button(window, text="Submit", command=lambda: self.collect_and_close(window), bg="#4c5c79", fg="white", font=("Helvetica", 12, "bold")).grid(row=int(self.SIMX_frames)+1, column=0, columnspan=4, pady=20)

    def create_frame_2d(self, window):
        # Frame 2d - Capture contiguous and exposure same
        tk.Label(window, text="Delays", bg="#2e3b55", fg="white", font=("Helvetica", 12, "bold")).grid(row=0, column=0, padx=10, pady=10)
        tk.Label(window, text="Exposures", bg="#2e3b55", fg="white", font=("Helvetica", 12, "bold")).grid(row=0, column=2, padx=10, pady=10)
        
        self.delays = []
        delay_entry = tk.Entry(window, width=10, font=("Helvetica", 10))
        delay_entry.grid(row=1, column=0, padx=5, pady=5)
        tk.Label(window, text="ns", bg="#2e3b55", fg="white").grid(row=1, column=1, padx=5, pady=5)
        self.delays.append(delay_entry)

        exposure_entry = tk.Entry(window, width=10, font=("Helvetica", 10))
        exposure_entry.grid(row=1, column=2, padx=5, pady=5)
        tk.Label(window, text="ns", bg="#2e3b55", fg="white").grid(row=1, column=3, padx=5, pady=5)
        self.exposures = [exposure_entry]

        tk.Button(window, text="Submit", command=lambda: self.collect_and_close(window), bg="#4c5c79", fg="white", font=("Helvetica", 12, "bold")).grid(row=2, column=0, columnspan=4, pady=20)

    def collect_and_close(self, window):
        # Collect data from entries
        try:
            self.delays = [int(entry.get()) for entry in self.delays]
            self.exposures = [int(entry.get()) for entry in self.exposures]
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numerical values for all fields.")
            return
        
        # Organize data similar to the original script
        address_set, name_set = self.organize()
        sample_name = self.address.rpartition('/')[2]
        SIMX_frames = int(self.SIMX_frames)

        # Close the additional details window
        window.quit()
        window.destroy()

        # Return the organized data
        self.address_set = address_set
        self.name_set = name_set
        self.sample_name = sample_name
        self.SIMX_frames = SIMX_frames

    def organize(self):
        image_set_names = []
        tiff_images_addresses = []
        for root, subfolders, filenames in os.walk(self.address):
            for filename in filenames:
                if filename.lower().endswith(".tiff") or filename.lower().endswith(".tif"):
                    image_set_names.append(root.rpartition('/')[2])
                    tiff_images_addresses.append(os.path.join(root, filename))
                      
        address_set = []
        name_set = []
        run_set = []
        previous_name = ''
        i = 0
        for image_name in image_set_names:
            current_name = image_name.rpartition('\\')[2]
            if current_name != previous_name and i != 0:
                address_set.append(run_set)
                name_set.append(current_name)
                run_set = []
                run_set.append(tiff_images_addresses[i])
            elif current_name != previous_name and i == 0:
                name_set.append(current_name)
                run_set = []
                run_set.append(tiff_images_addresses[i])
            else:
                run_set.append(tiff_images_addresses[i])
            
            previous_name = current_name
            i += 1
        # Last cycle data added
        address_set.append(run_set)
        return address_set, name_set

    def close_window(self):
        # Gracefully close the window without any errors
        self.master.quit()
        self.master.destroy()




"""
Created on Tue Feb 09 19:38:12 2023

@author: Siva Kumar Valluri
"""
import cv2
import numpy as np
import itertools
import tkinter as tk
from PIL import Image, ImageTk
import matplotlib.pyplot as plt
import pandas as pd

class Palantíri:
    # Emission frame processing
    smoothing_choice = 'n'              # default choice to smoothing emission frame # Smoothing convolutional kernel size
    kernel_size = 5                     # default value for smoothing emission frame
    
    # Stitched imageset for every run
    scale_percent = 20                  # default for 8 frame
    write_choice = 'y'
    write_color = [255, 0, 0]
    write_size = 0.5
    write_linethickness = 2
    see_image_choice = 'y'
    save_image_choice = 'n'
       
    def __init__(self, address_set, name, delays, exposures, SIMX_frames):
        self.address_set = address_set
        self.name = name
        self.delays, self.exposures = self.populate_entries(delays, exposures)
        self.SIMX_frames = SIMX_frames
 
    
    def populate_entries(self, delays, exposures):
        if len(delays) == 8 and len(exposures) == 8:
            return delays, exposures
        elif len(delays) == 1 and len(exposures) == 8:
            delays = [delays[0] + sum(exposures[:i]) for i in range(8)]
            return delays, exposures
        elif len(exposures) == 1 and len(delays) == 8:
            exposures = exposures * 8
            return delays, exposures
        elif len(delays) == 1 and len(exposures) == 1:
            delays = [delays[0] + i * exposures[0] for i in range(8)]
            exposures = exposures * 8
            return delays, exposures
        else:
            raise ValueError("Invalid number of entries for delays and exposures. They must be either 1 or 8 items each.")

    def display_with_tkinter(self, image, title):
        # Convert the OpenCV image to PIL format
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image_pil = Image.fromarray(image_rgb)
        # Set up the tkinter window
        root = tk.Tk()
        root.title(title)
        # Convert the PIL image to ImageTk format
        image_tk = ImageTk.PhotoImage(image_pil)
        # Create a label widget to hold the image
        label = tk.Label(root, image=image_tk)
        label.pack()
        def save_image():
            save_path = f"{self.name}_stitched_from_tkinter.tif"
            image_pil.save(save_path)
            print(f"Image saved at {save_path}")
        # Add a button to save the image
        save_button = tk.Button(root, text="Save Image", command=save_image)
        save_button.pack()
        # Run the tkinter main loop
        root.mainloop()

    def display_plot_with_tkinter(self, plt, title):
        # Set up the tkinter window
        root = tk.Tk()
        root.title(title)
        # Draw the plot on a canvas using Matplotlib
        canvas = plt.gcf().canvas
        canvas.draw()
        plt_image = Image.frombytes('RGB', canvas.get_width_height(), canvas.tostring_rgb())
        # Convert the PIL image to ImageTk format
        image_tk = ImageTk.PhotoImage(plt_image)
        # Create a label widget to hold the image
        label = tk.Label(root, image=image_tk)
        label.pack()
        # Run the tkinter main loop
        root.mainloop()

    def lúmëa(self):  # Calculate plotting time series and error bars
        # Calculate plotting time as (delays[i] + exposures[i]) / 2 for each entry
        plotting_time = [self.delays[i] + (self.exposures[i] / 2) for i in range(0,len(self.delays),1)] 
        # Calculate error as exposures[i] / 2 for each entry
        error = [self.exposures[i] / 2 for i in range(0,len(self.exposures),1)]    
        return plotting_time, error
    
    def olos(self):  # "dreams" - import images in run folder
        static_images = []
        emission_images = []
        # Importing static and emission images in run
        for image_number in range(len(self.address_set)):
            if image_number < len(self.address_set) // 2:
                static_image = cv2.imread(self.address_set[image_number], cv2.IMREAD_GRAYSCALE)
                static_image = cv2.normalize(static_image, None, 0, 255, cv2.NORM_MINMAX, cv2.CV_8U)
                static_images.append(static_image)
            else:
                # Based on the choice the emission frame is smoothed or presented as is
                emission_fr = cv2.imread(self.address_set[image_number], cv2.IMREAD_GRAYSCALE)
                emission_fr = cv2.normalize(emission_fr, None, 0, 255, cv2.NORM_MINMAX, cv2.CV_8U)
                if self.smoothing_choice.lower() in ["y", "yes"]:
                    kernel = np.ones((self.kernel_size, self.kernel_size), np.float32) / (self.kernel_size ** 2)
                    gaus_image = cv2.filter2D(emission_fr, -1, kernel)
                    emission_image = cv2.normalize(gaus_image, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
                else:
                    emission_image = emission_fr
                emission_images.append(emission_image)
        
        return static_images, emission_images

    def ósanwë(self):  # to communicate - stitch images within run folder
        # Get static and emission images
        static_images, emission_images = self.olos()  
        # Ensure delays and exposures have 8 entries each
        delays, exposures = self.populate_entries(self.delays, self.exposures)
        imagename = "run " + self.name
        
        resized_images = []
        for static_image, delay, exposure in itertools.zip_longest(static_images, delays, exposures):
            image = cv2.cvtColor(static_image, cv2.COLOR_GRAY2RGB)
            wscale = int(image.shape[1] * self.scale_percent / 100)
            hscale = int(image.shape[0] * self.scale_percent / 100)
            resized_image = cv2.resize(image, (wscale, hscale), interpolation=cv2.INTER_LINEAR)
            if self.write_choice.lower() in ["y", "yes"] and delay is not None and exposure is not None:
                font = cv2.FONT_HERSHEY_SIMPLEX  # Other options: cv2.FONT_HERSHEY_COMPLEX, cv2.FONT_HERSHEY_TRIPLEX, etc.
                text = f"{delay}-{int(delay) + int(exposure)} ns"
                # To center the text, find its length and then use it to give position value
                textsize = cv2.getTextSize(text, font, self.write_size, self.write_linethickness)[0]
                textX = int((resized_image.shape[1] - textsize[0]) * 0.5)
                textY = int((resized_image.shape[0] + textsize[1]) * 0.1)
                resized_image = cv2.putText(resized_image, text, (textX, textY), font, self.write_size, self.write_color, self.write_linethickness)
            resized_images.append(resized_image)
        
        for emission_image in emission_images:
            image = cv2.cvtColor(emission_image, cv2.COLOR_GRAY2RGB)
            wscale = int(image.shape[1] * self.scale_percent / 100)
            hscale = int(image.shape[0] * self.scale_percent / 100)
            resized_image = cv2.resize(image, (wscale, hscale), interpolation=cv2.INTER_LINEAR)
            resized_images.append(resized_image)
        
        # Create stitched image
        image = resized_images[0]
        height = image.shape[0] * 2
        width = image.shape[1] * int(self.SIMX_frames)
        
        if len(image.shape) == 3:
            stitched = np.zeros((height, width, 3), np.uint8)
        else:
            stitched = np.zeros((height, width), np.uint8)
        
        # Stitch static and emission images
        for x in range(2 * int(self.SIMX_frames)):
            if x < int(self.SIMX_frames):
                h, w, c = resized_images[x].shape
                stitched[0:h, x * w:(x + 1) * w] = resized_images[x]
            else:
                h, w, c = resized_images[x].shape
                stitched[h:2 * h, (x - int(self.SIMX_frames)) * w:(x - int(self.SIMX_frames) + 1) * w] = resized_images[x]
        
        # Display or save the stitched image
        if self.see_image_choice.lower() in ["y", "yes"]:
            self.display_with_tkinter(stitched, imagename)
        if self.save_image_choice.lower() in ["y", "yes"]:
            save_path = f"{self.name}_stitched.tif"
            cv2.imwrite(save_path, stitched)
            print(f"Image saved at {save_path}")

    def silivros(self):  # Read pixel intensities in emission image masked by respective static image
        static_images, emission_images = self.olos()
        pixel_intensities = []
        mean_intensities = []
        for static_image, emission_image in zip(static_images, emission_images):
            # Ensure both images are of the same size
            if static_image.shape != emission_image.shape:
                raise ValueError("Static and emission images must have the same dimensions.")        
            # Create a mask where static image is not zero
            mask = static_image > 0  
            # Apply the mask to emission image to get intensities
            masked_intensities = emission_image[mask]
            mean_intensity = masked_intensities.mean()
            mean_intensities.append(mean_intensity) 
            pixel_intensities.append(masked_intensities) 
            
        # Create a box plot of the pixel intensities using Matplotlib
        plt.figure(figsize=(10, 6))
        plt.clf()
        plt.boxplot(pixel_intensities, notch=True, patch_artist=True)
        # Set x-axis labels as the delays
        plt.xticks(ticks=np.arange(1, len(self.delays) + 1), labels=self.delays, rotation=0)
        plt.xlabel("Delays (ns)")
        plt.ylabel("Pixel Intensities")
        plt.ylim(0,255)
        plt.title("Pixel Intensities within Field-of-view")      
        # Show the plot using Tkinter
        self.display_plot_with_tkinter(plt, "Pixel Intensities within Field-of-view")      
        plt.close()
        # Convert pixel_intensities to DataFrame with plotting_time as column headers
        plotting_time, _ = self.lúmëa()
        df_pixel_intensities = pd.DataFrame(pixel_intensities).T
        df_pixel_intensities.columns = [f"{time} ns" for time in plotting_time]
        df_mean_intensities = pd.DataFrame(mean_intensities).T
        df_mean_intensities.columns = [f"{time} ns" for time in plotting_time]
        return df_pixel_intensities, df_mean_intensities

    def wathar(self):  # Threshold emission images and calculate area of thresholded regions
        static_images, emission_images = self.olos()
        thresholds = [5, 15, 25, 50, 100, 150, 200] # 2~2010K,  15~2635K, 50~3098K, 200~3731K estimated by IntegratedI = (5.10254E-25)*T**7.4451 Plank's equation for black body inetgrated between 300-800 nm

        areas_by_threshold = {threshold: [] for threshold in thresholds}
        
        # Get plotting time and error from lúmëa
        plotting_time, error = self.lúmëa()
        
        for threshold in thresholds:
            for static_image, emission_image in zip(static_images, emission_images):
                # Ensure both images are of the same size
                if static_image.shape != emission_image.shape:
                    raise ValueError("Static and emission images must have the same dimensions.")
                
                # Threshold emission image
                _, thresholded_image = cv2.threshold(emission_image, threshold, 255, cv2.THRESH_BINARY)
                
                # Create a mask where static image is not zero
                mask = static_image > 0
                
                # Apply mask to thresholded image
                masked_image = np.zeros_like(thresholded_image)
                masked_image[mask] = thresholded_image[mask]
                
                # Calculate area covered by thresholded region as percentage
                total_pixels = np.sum(mask)
                thresholded_pixels = np.sum(masked_image > 0)
                if total_pixels > 0:
                    area_percentage = (thresholded_pixels / total_pixels) * 100
                else:
                    area_percentage = 0

                areas_by_threshold[threshold].append(area_percentage)

        df_areas_by_threshold = pd.DataFrame.from_dict(areas_by_threshold)
        df_areas_by_threshold['Error'] = error
        df_areas_by_threshold.set_index(pd.Index(plotting_time), inplace=True)
        df_areas_by_threshold = df_areas_by_threshold[['Error'] + [col for col in df_areas_by_threshold.columns if col != 'Error']]
        # Plot areas as a function of plotting time with error bars
        plt.figure(figsize=(10, 6))
        plt.clf()
        for threshold, areas in areas_by_threshold.items():
            plt.errorbar(plotting_time, areas, xerr=error, label=f'Threshold {threshold}', fmt='-o', capsize=5)
        
        plt.xlabel("Delays (ns)")
        plt.ylabel("Area Covered (%)")
        plt.ylim(0,100)
        plt.title("Area of Thresholded Regions as a Function of Time")
        plt.legend()
        
        # Show the plot using Tkinter
        self.display_plot_with_tkinter(plt, "Area of Thresholded Regions as a Function of Time")
        plt.close()
        return df_areas_by_threshold     
        

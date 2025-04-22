import os
import logging
import numpy as np
import pandas as pd
from Plotter import Plotter

class CSVProcessor:
    def __init__(self, reference_file, input_folder, output_folder, wavelength, color):
        self.reference_file = reference_file
        self.input_folder = input_folder
        self.wavelength = wavelength
        self.reference_df = None
        self.bandwidths = []
        self.amp_mods = []
        self.plotter = Plotter(
            input_folder=input_folder,
            output_folder=output_folder,
            wavelength=wavelength,
            color=color
        )
        
    def rtp(self, x, y):
        r = np.sqrt(x**2 + y**2)
        theta = np.arctan2(y, x)
        return r, theta
    
    def process_file(self, file_path, ref=False):
        # Read the CSV, skipping comment lines starting with '%'
        logging.info(f"Reading CSV: {file_path}")
        df = pd.read_csv(file_path, skiprows=1, comment='%', header=None)
        
        # Rename columns for clarity
        df.columns = ['lam', 'S21']
        
        # Convert wavelength from meters to nanometers
        df['lam_nm'] = df['lam'] * 1e9
        df['S21'] = df['S21'].str.replace('i', 'j').astype(complex)
        df['real'] = df['S21'].apply(lambda z: z.real)
        df['imag'] = df['S21'].apply(lambda z: z.imag)
        
        # Convert from polar to rectangular form
        df[['|S21|', 'phase_rad']] = df.apply(
            lambda row: pd.Series(self.rtp(float(row['real']), float(row['imag']))),
            axis=1
        )
        df["|S21|^2"] = df["|S21|"] ** 2
        df['phase_unwrapped'] = np.unwrap(df['phase_rad'])
        df['phase_unwrapped_degrees'] = np.degrees(df['phase_unwrapped'])

        # Compute the phase difference if needed
        if not ref:
            # logging.info("Computing phase gradient...")

            # unwrap(arg50) - unwrap(arg70)
            df['phase_diff'] = self.reference_df['phase_unwrapped'] - df['phase_unwrapped']
            df['phase_diff_deg'] = np.degrees(df['phase_diff']) 
            while (df['phase_diff_deg'] < 0).any():
                df['phase_diff_deg'] = df['phase_diff_deg'] + 360

            # Restore lam as a column for plotting
            df = df.reset_index()
        return df
    
    def compute_phase_bandwidth(self, df, tolerance):
        if 'phase_diff_deg' not in df.columns:
            return None
        
        # Find what the phase graident is at the
        idx = (df['lam_nm'] - self.wavelength).abs().idxmin()
        center_phase = df.loc[idx, 'phase_diff_deg']
        
        # Get plus minus 10 of y_val and find their wavelength values
        lower_bound = center_phase - tolerance
        upper_bound = center_phase + tolerance
        
        # Find their corresponding wavelength values
        window_df = df[(df['phase_diff_deg'] >= lower_bound) & (df['phase_diff_deg'] <= upper_bound)]
        if window_df.empty:
            logging.warning("No data points within ±10° of center phase.")
            return None
        
        lam_min = window_df['lam_nm'].min()
        lam_max = window_df['lam_nm'].max()
        bandwidth = lam_max - lam_min
        
        self.bandwidths.append(bandwidth)
        return window_df
    
    def compute_amp_mod(self, window_df):
        if window_df is None:
            logging.error("WINDOW_DF IS NONE")
            return
        max_T = window_df["|S21|^2"].max()
        min_T = window_df["|S21|^2"].min()
       
        amp_mod = max_T - min_T
        self.amp_mods.append(amp_mod)
    
    def generate_plots(self):
        # reference file
        reference_path = os.path.join(self.input_folder, self.reference_file)
        self.reference_df = self.process_file(reference_path, ref=True)
        self.plotter.plot_data(self.reference_df, self.reference_file[:-4], ref=True)

        for fname in os.listdir(self.input_folder):
            if not fname.endswith('.csv') or fname == self.reference_file:
                continue
            file_path = os.path.join(self.input_folder, fname)
            df = self.process_file(file_path)
            self.plotter.plot_data(df, fname[:-4])
                
    def results_analysis(self, tolerance, plot=False):
        # reference file
        reference_path = os.path.join(self.input_folder, self.reference_file)
        self.reference_df = self.process_file(reference_path, ref=True)
        
        # For Each Meta Atom
        for fname in os.listdir(self.input_folder):
            if not fname.endswith('.csv') or fname == self.reference_file:
                continue
            # ready for processing
            file_path = os.path.join(self.input_folder, fname)
            df = self.process_file(file_path)
            
            window_df = self.compute_phase_bandwidth(df, tolerance)
            self.compute_amp_mod(window_df)
            
            # Annotate the graph of transmittance and phase to show visually what I did
            if plot:
                self.plotter.plot_data(df, fname[:-4], window_df=window_df)

        # Now that the bandwidths for this metalens is filled up
        # find the limiting bandwidth
        boo = min(self.bandwidths)
        print(f"The Minimum Bandwidth from all Phase Gradients is {boo}[nm]")
        
        am = max(self.amp_mods)
        print(f"The Maximum Amplitude Modulation is {am * 100:.2f}% within ")
        
        
    def tolerance_sweep(self, start, end, plot=False):
        # reference file
        reference_path = os.path.join(self.input_folder, self.reference_file)
        self.reference_df = self.process_file(reference_path, ref=True)
        
        boo = []
        am = []
        for t in range(start, end):
            # For Each Meta Atom
            for fname in os.listdir(self.input_folder):
                if not fname.endswith('.csv') or fname == self.reference_file:
                    continue
                # ready for processing
                file_path = os.path.join(self.input_folder, fname)
                df = self.process_file(file_path)
                
                window_df = self.compute_phase_bandwidth(df, t)
                self.compute_amp_mod(window_df)
                
                # if plot:
                #     self.plotter.plot_data(df, fname[:-4], window_df=window_df)

            # Now that the bandwidths for this metalens is filled up
            # find the limiting bandwidth
            boo.append(min(self.bandwidths))
            am.append(max(self.amp_mods))
            self.bandwidths.clear()
            self.amp_mods.clear()
        print(boo)
        print(am)
        if plot:
            self.plotter.plot_tolerances(start, end, boo, am)
            
        
        
            
            
        

        
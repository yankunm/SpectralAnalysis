import os
import logging
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

class Plotter:
    def __init__(self, input_folder, output_folder, reference_file, wavelength, color):
        self.input_folder = input_folder
        self.output_folder = output_folder
        self.reference_file = reference_file
        self.wavelength = wavelength
        self.color = color
        self.reference_df = None

        os.makedirs(self.output_folder, exist_ok=True)
        
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
    
    
    def plot_data(self, df, filename, ref=False):
        fig, ax = plt.subplots(1, 2, figsize=(16, 5))

        # Magnitude plot
        ax[0].plot(df['lam_nm'], df['|S21|^2'], label='|T|^2', color=self.color)
        ax[0].set_xlabel('Wavelength λ (nm)')
        ax[0].set_ylabel('|T|^2')
        ax[0].set_title(f'|T|^2 vs Wavelength for {filename}')
        ax[0].grid(True)
        ax[0].axvline(self.wavelength, color='black', linestyle='--', linewidth=1, label='Desired Wavelength')
        ax[0].legend()
        ax[0].set_ylim(0, 1)  # Set the y-axis to go from 0 to 1

        idx = (df['lam_nm'] - self.wavelength).abs().idxmin()
        x_val = df.loc[idx, 'lam_nm']
        y_val = df.loc[idx, '|S21|^2']
        ax[0].plot(x_val, y_val, 'ko')
        ax[0].hlines(y_val, xmin=ax[0].get_xlim()[0], xmax=x_val, colors='black', linestyles='--')

        # Phase plot
        ax[1].set_xlabel('Wavelength λ (nm)')
        # Annotate y-axis value
        ax[0].annotate(f'{y_val:.5f}',
                    xy=(ax[0].get_xlim()[0], y_val),
                    xytext=(ax[0].get_xlim()[0], y_val - 0.05),
                    fontsize=14,
                    color='black')
        if ref:
            ax[1].plot(df['lam_nm'], df['phase_unwrapped_degrees'], color=self.color)
            ax[1].set_ylabel('arg(T) (degrees)')
            ax[1].set_title(f'Unwrapped arg(T) for {filename[-7:]}')
            y_val = df.loc[idx, 'phase_unwrapped_degrees']
        else:
            ax[1].plot(df['lam_nm'], df['phase_diff_deg'], color=self.color)
            ax[1].set_ylabel('Phase Difference (degrees)')
            ax[1].set_title(f'Δarg(T): R50 - {filename[-7:]}')
            y_val = df.loc[idx, 'phase_diff_deg']
        ax[1].grid(True)
        ax[1].axvline(self.wavelength, color='black', linestyle='--', linewidth=1, label='Desired Wavelength')
        ax[1].plot(x_val, y_val, 'ko')
        ax[1].legend()
        ax[1].hlines(y_val, xmin=ax[1].get_xlim()[0], xmax=x_val, colors='black', linestyles='--')

        # Choose the correct y value depending on reference
        if 'phase_diff_deg' in df.columns:
            y_val = df.loc[idx, 'phase_diff_deg']
        else:
            y_val = df.loc[idx, 'phase_unwrapped_degrees']

        # Plot black dot
        ax[1].plot(x_val, y_val, 'ko')  # black dot

        # Vertical dashed line to x-axis
        ax[1].axvline(x_val, color='black', linestyle='--', linewidth=1)

        # Horizontal dashed line to y-axis (extends to full axis)
        ax[1].hlines(y_val, xmin=ax[1].get_xlim()[0], xmax=x_val, colors='black', linestyles='--', linewidth=1)

        # Annotate y-axis value
        ax[1].annotate(f'{y_val:.1f}°',
                    xy=(ax[1].get_xlim()[0], y_val),
                    xytext=(ax[1].get_xlim()[0], y_val + 10),
                    fontsize=14,
                    color='black')
        
        plt.tight_layout()
        plt.savefig(f'{self.output_folder}/{filename}.png')
        logging.info(f"Saved plot as {filename}.png")
    
    def process_all(self):
        # reference file
        reference_path = os.path.join(self.input_folder, self.reference_file)
        self.reference_df = self.process_file(reference_path, ref=True)
        self.plot_data(self.reference_df, self.reference_file[:-4], ref=True)

        for fname in os.listdir(self.input_folder):
            if not fname.endswith('.csv') or fname == self.reference_file:
                continue
            file_path = os.path.join(self.input_folder, fname)
            df = self.process_file(file_path)
            self.plot_data(df, fname[:-4])
import os
import logging
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch

class Plotter:
    def __init__(self, input_folder, output_folder, wavelength, color):
        self.input_folder = input_folder
        self.output_folder = output_folder
        self.wavelength = wavelength
        self.color = color
        self.fontsize = 17
        self.yvallabel = 0.07
        os.makedirs(self.output_folder, exist_ok=True)
        
    def plot_data(self, df, filename, ref=False, window_df=None):
        fig, ax = plt.subplots(1, 2, figsize=(16, 5))
        
        # Transmittance plot
        ax[0].plot(df['lam_nm'], df['|S21|^2'], label='|T|^2', color=self.color)
        ax[0].set_xlabel('Wavelength λ (nm)')
        ax[0].set_ylabel('|T|^2')
        ax[0].set_title(f'|T|^2 vs Wavelength for {filename}')
        ax[0].grid(True)
        ax[0].axvline(self.wavelength, color='black', linestyle='--', linewidth=1, label='Desired Wavelength')
        ax[0].legend()
        ax[0].set_ylim(0, 1)  # Set the y-axis to go from 0 to 1
        ax[0].set_xlim(400, 800)  # Set the y-axis to go from 0 to 1
        idx = (df['lam_nm'] - self.wavelength).abs().idxmin()
        x_val = df.loc[idx, 'lam_nm']
        y_val = df.loc[idx, '|S21|^2']
        ax[0].plot(x_val, y_val, 'ko')
        ax[0].hlines(y_val, xmin=ax[0].get_xlim()[0], xmax=x_val, colors='black', linestyles='--')
        ax[0].annotate(f'{y_val:.5f}',
                    xy=(ax[0].get_xlim()[0], y_val),
                    xytext=(ax[0].get_xlim()[0], y_val - self.yvallabel),
                    fontsize=self.fontsize,
                    color='black')
        ax[0].annotate(f'{self.wavelength:.0f} nm',
                    xy=(self.wavelength, ax[1].get_ylim()[0]),
                    xytext=(self.wavelength, ax[1].get_ylim()[0] - 10),  # adjust -10 as needed
                    ha='center', va='top',
                    fontsize=self.fontsize - 2,
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
        ax[1].set_xlim(400, 800)  # Set the y-axis to go from 0 to 1
        ax[1].hlines(y_val, xmin=ax[1].get_xlim()[0], xmax=x_val, colors='black', linestyles='--')

        # Choose the correct y value depending on reference
        if 'phase_diff_deg' in df.columns:
            y_val = df.loc[idx, 'phase_diff_deg']
        else:
            y_val = df.loc[idx, 'phase_unwrapped_degrees']

        ax[1].plot(x_val, y_val, 'ko')  # black dot
        ax[1].axvline(x_val, color='black', linestyle='--', linewidth=1)
        ax[1].hlines(y_val, xmin=ax[1].get_xlim()[0], xmax=x_val, colors='black', linestyles='--', linewidth=1)
        ax[1].annotate(f'{y_val:.1f}°',
                    xy=(ax[1].get_xlim()[0], y_val),
                    xytext=(ax[1].get_xlim()[0], y_val + 10),
                    fontsize=self.fontsize,
                    color='black')
        ax[1].annotate(f'{self.wavelength:.0f} nm',
                    xy=(self.wavelength, ax[1].get_ylim()[0]),
                    xytext=(self.wavelength, ax[1].get_ylim()[0] - 10),  # adjust -10 as needed
                    ha='center', va='top',
                    fontsize=self.fontsize - 2,
                    color='black')
        
        # annotate the transmittance
        if not ref and window_df is not None:
            lam_min = window_df['lam_nm'].min()
            lam_max = window_df['lam_nm'].max()
            max_T = window_df['|S21|^2'].max()
            min_T = window_df['|S21|^2'].min()

            # Vertical pink lines for lam_min and lam_max
            ax[0].axvline(lam_min, color='magenta', linestyle='--', linewidth=1)
            ax[0].axvline(lam_max, color='magenta', linestyle='--', linewidth=1)
            ax[0].annotate(f'{lam_min:.1f} nm', xy=(lam_min, 0.05), rotation=90, color='magenta', fontsize=self.fontsize, ha='right')
            ax[0].annotate(f'{lam_max:.1f} nm', xy=(lam_max, 0.05), rotation=90, color='magenta', fontsize=self.fontsize, ha='left')

            # Horizontal pink lines for max_T and min_T
            ax[0].hlines(max_T, xmin=lam_min, xmax=lam_max, colors='magenta', linestyles='--')
            ax[0].hlines(min_T, xmin=lam_min, xmax=lam_max, colors='magenta', linestyles='--')

            ax[0].text(0.98, 0.85,
                    f'Max: {max_T*100:.2f}%',
                    transform=ax[0].transAxes,
                    ha='right', va='top',
                    fontsize=self.fontsize, color='magenta')

            ax[0].text(0.98, 0.75,
                    f'Min: {min_T*100:.2f}%',
                    transform=ax[0].transAxes,
                    ha='right', va='top',
                    fontsize=self.fontsize, color='magenta')
            
            ax[0].text(0.98, 0.65,
                    f'A.M.: {(max_T - min_T)*100:.2f}%',
                    transform=ax[0].transAxes,
                    ha='right', va='top',
                    fontsize=self.fontsize, color='magenta')
            
            # Annotate the phase plot with
            # 1. horizontal pink line showing the plus and minus ten degrees from the center_phase
            # 2. vertical pink lines showing their corresponding wavelengths
                    # Use window_df to get lam_min, lam_max and ±10° bounds
            phase_min = window_df['phase_diff_deg'].min()
            phase_max = window_df['phase_diff_deg'].max()

            # Horizontal pink lines at phase_min and phase_max (±10° around center)
            # Horizontal dashed lines
            ax[1].hlines([phase_min, phase_max],
                        xmin=ax[1].get_xlim()[0],
                        xmax=ax[1].get_xlim()[1],
                        colors='magenta',
                        linestyles='--')

            # Labels to the left, aligned with line height
            ax[1].annotate(f'{phase_min:.1f}°',
                        xy=(ax[1].get_xlim()[0], phase_min),
                        xytext=(ax[1].get_xlim()[0] - 5, phase_min),  # 5 units left
                        fontsize=self.fontsize -2,
                        color='magenta',
                        ha='right',
                        va='center')

            ax[1].annotate(f'{phase_max:.1f}°',
                        xy=(ax[1].get_xlim()[0], phase_max),
                        xytext=(ax[1].get_xlim()[0] - 5, phase_max),
                        fontsize=self.fontsize -2,
                        color='magenta',
                        ha='right',
                        va='center')


            # Vertical pink lines at lam_min and lam_max
            ax[1].axvline(lam_min, color='magenta', linestyle='--', linewidth=1)
            ax[1].axvline(lam_max, color='magenta', linestyle='--', linewidth=1)
            # Add fixed text in the upper-right corner (axes coordinates)
            ax[1].text(0.98, 0.85,
                    f'Left: {lam_min:.2f} nm',
                    transform=ax[1].transAxes,
                    ha='right', va='top',
                    fontsize=self.fontsize, color='magenta')

            ax[1].text(0.98, 0.75,
                    f'Right: {lam_max:.2f} nm',
                    transform=ax[1].transAxes,
                    ha='right', va='top',
                    fontsize=self.fontsize, color='magenta')
            
            bandwidth_nm = lam_max - lam_min
            ax[1].text(0.98, 0.65,
                    f'Bandwidth: {bandwidth_nm:.2f} nm',
                    transform=ax[1].transAxes,
                    ha='right', va='top',
                    fontsize=self.fontsize, color='magenta')

            # Use axis limits for stable coordinate mapping
            xlim = ax[1].get_xlim()
            x_range = xlim[1] - xlim[0]

            # Normalize lam_min and lam_max to axes [0, 1] using the current x-axis limits
            start = (lam_min - xlim[0]) / x_range
            end = (lam_max - xlim[0]) / x_range
            arrow_y = 0.50  # position below the x-axis

            # Draw arrow in axes coordinates
            arrow = FancyArrowPatch(
                (start, arrow_y), (end, arrow_y),
                transform=ax[1].transAxes,
                arrowstyle='<->', color='magenta',
                linewidth=3, mutation_scale=15
            )
            ax[1].add_patch(arrow)

       
        plt.tight_layout()
        plt.savefig(f'{self.output_folder}/{filename}.png')
        logging.info(f"Saved plot as {filename}.png")
    
    def plot_tolerances(self, start, end, boo, am, desired_tolerance=10):
        tolerances = list(range(start, end))
        idx = tolerances.index(desired_tolerance)
        desired_bw = boo[idx]
        desired_am = am[idx]

        # Bandwidth plot
        plt.figure(figsize=(10, 6))
        plt.plot(tolerances, boo, 'o-', color=self.color, label='Min Bandwidth')
        plt.plot(desired_tolerance, desired_bw, 'ko')  # black point

        # Dashed lines to the point only
        plt.plot([desired_tolerance, desired_tolerance], [0, desired_bw],
                color='black', linestyle='--', linewidth=1)
        plt.plot([start, desired_tolerance], [desired_bw, desired_bw],
                color='black', linestyle='--', linewidth=1)

        # Label near left edge
        plt.text(start + 0.5, desired_bw + 1.5,
                f'{desired_bw:.1f} nm',
                color='black', fontsize=self.fontsize)

        plt.xlabel('Tolerance (± degrees)')
        plt.ylabel('Bandwidth of Operation [nm]')
        plt.title('Tolerance Sweep vs Bandwidth')
        plt.grid(True)
        plt.tight_layout()
        plt.xlim(start, end)
        plt.savefig(os.path.join(self.output_folder, 'tolerance_vs_bandwidth.png'))
        plt.close()

        # Amplitude Modulation plot
        plt.figure(figsize=(10, 6))
        plt.plot(tolerances, am, 's--', color=self.color, label='Max Amplitude Modulation')
        plt.plot(desired_tolerance, desired_am, 'ko')

        # Dashed lines to the point only
        plt.plot([desired_tolerance, desired_tolerance], [0, desired_am],
                color='black', linestyle='--', linewidth=1)
        plt.plot([start, desired_tolerance], [desired_am, desired_am],
                color='black', linestyle='--', linewidth=1)

        # Label near left edge
        plt.text(start + 0.5, desired_am + 0.03,
                f'{desired_am * 100:.1f}%',
                color='black', fontsize=self.fontsize)

        plt.xlabel('Tolerance (± degrees)')
        plt.ylabel('Amplitude Modulation [%]')
        plt.title('Tolerance Sweep vs Amplitude Modulation')
        plt.grid(True)
        plt.tight_layout()
        plt.xlim(start, end)
        plt.ylim(0, 1)
        plt.savefig(os.path.join(self.output_folder, 'tolerance_vs_amplitude_modulation.png'))
        plt.close()

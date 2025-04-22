import json
import logging
import warnings
from CSVProcessor import CSVProcessor

def load_config(config_path):
    with open(config_path, 'r') as f:
        return json.load(f)
    
if __name__ == '__main__':
    warnings.filterwarnings("ignore")
    logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')
    config_all = load_config("config.json")
    
    for key, config in config_all.items():
        print(f"Processing color: {key}")
        processor = CSVProcessor(
            reference_file=config["reference_file"],
            input_folder=config["input_folder"],
            output_folder=config["output_folder"],
            wavelength=config["wavelength"],
            color=config["color"]
        )
        print(f"Generating all plots for {key} MetaLens...")
        # processor.generate_plots() # generate non-annotated plots
        # processor.results_analysis(tolerance=10, plot=True) # generate annotated data with plots
        # processor.results_analysis(tolerance=5) # generate annotated data without plots
        processor.tolerance_sweep(0, 20, plot=True)
        print("DONE.")
    
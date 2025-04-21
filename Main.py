import json
import logging
import warnings
from Plotter import Plotter

def load_config(config_path):
    with open(config_path, 'r') as f:
        return json.load(f)
    
if __name__ == '__main__':
    warnings.filterwarnings("ignore")
    logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')
    config_all = load_config("config.json")
    
    for key, config in config_all.items():
        logging.info(f"Processing color: {key}")
        processor = Plotter(
            input_folder=config["input_folder"],
            output_folder=config["output_folder"],
            reference_file=config["reference_file"],
            wavelength=config["wavelength"],
            color=config["color"]
        )
        print("Generating all plots...")
        processor.process_all()
        print("DONE.")
    
import io
import sys

stream = io.StringIO()
sys.stdout = stream
sys.stderr = stream

import sys
import logging
import os
from datetime import datetime

# Setup logging to file
def setup_logging():
    """Setup logging to write to a file in the application directory"""
    try:
        # Use absolute path for logs directory (works with PyInstaller)
        log_dir = r"C:\Program Files (x86)\IBDS\Datapilot\logs"
        
        # Try to create the logs directory
        try:
            os.makedirs(log_dir, exist_ok=True)
        except PermissionError:
            # If permission denied, try user's temp directory as fallback
            import tempfile
            log_dir = os.path.join(tempfile.gettempdir(), "DataPilot_logs")
            os.makedirs(log_dir, exist_ok=True)
        
        # Create log filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_filename = f"datapilot_debug_{timestamp}.log"
        log_filepath = os.path.join(log_dir, log_filename)
        
        # Configure logging
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
            handlers=[
                logging.FileHandler(log_filepath, mode='w', encoding='utf-8'),
                # Also keep a rotating handler for the latest log
                logging.FileHandler(os.path.join(log_dir, "datapilot_latest.log"), mode='w', encoding='utf-8')
            ]
        )
        
        # Create a logger instance
        logger = logging.getLogger('DataPilot')
        logger.info("=== DataPilot Application Started ===")
        logger.info(f"Log directory: {log_dir}")
        logger.info(f"Log file: {log_filepath}")
        logger.info(f"Python version: {sys.version}")
        logger.info(f"Working directory: {os.getcwd()}")
        logger.info(f"Frozen (PyInstaller): {getattr(sys, 'frozen', False)}")
        if getattr(sys, 'frozen', False):
            logger.info(f"Executable path: {sys.executable}")
            if hasattr(sys, '_MEIPASS'):
                logger.info(f"PyInstaller temp dir: {sys._MEIPASS}")
        
        return logger
    except Exception as e:
        # If logging setup fails, create a minimal logger that writes to temp
        import tempfile
        temp_log = os.path.join(tempfile.gettempdir(), "datapilot_error.log")
        logging.basicConfig(filename=temp_log, level=logging.ERROR)
        logger = logging.getLogger('DataPilot')
        logger.error(f"Failed to setup main logging: {e}")
        logger.error(f"Attempted log directory: C:\\Program Files (x86)\\IBDS\\Datapilot\\logs")
        return logger

# Initialize logger
logger = setup_logging()

# Splash screen initiation
if getattr(sys, 'frozen', False):
    import pyi_splash

import eel
eel.init(r"C:\Program Files (x86)\IBDS\DataPilot")

# DBC Signal to Unit Mapping from Microlite.dbc
DBC_SIGNAL_UNITS = {
    'Accelerometer_X': 'g',
    'Accelerometer_Y': 'g', 
    'Accelerometer_Z': 'g',
    'Gyroscope_X': 'deg/s',
    'Gyroscope_Y': 'deg/s',
    'Gyroscope_Z': 'deg/s',
    'Accelerometer X': 'g',
    'Accelerometer Y': 'g', 
    'Accelerometer Z': 'g',
    'Gyroscope X': 'deg/s',
    'Gyroscope Y': 'deg/s',
    'Gyroscope Z': 'deg/s',
    'LATITUDE': 'deg',
    'DATETIME': 'Epoch',
    'LONGITUDE': 'deg',
    'ALTITUDE': 'm',
    'SPEED_OVER_GROUND': 'km/h',
    'GROUND_DISTANCE': 'nm',
    'COURSE_OVER_GROUND': 'deg',
    'GEOID_SEPARATION': 'm',
    'NUMBER_SATELLITES': 'count',
    'QUALITY': 'index',
    'GPS_Date_time': 'Epoch',
    'Acceleration_x_longitudinal': 'm/s2',
    'Acceleration_y_lateral': 'm/s2',
    'Acceleration_z_normal': 'm/s2',
    'Vertical_speed': 'fpm',
    'Indicated_airspeed': 'knot',
    'Barometric_correction_QNH': 'hPa',
    'Baro_corrected_altitude': 'ft',
    'Standard_altitude': 'ft',
    'Differentialpressure': 'hPa',
    'Static_pressure': 'hPa',
    'Engine_Speed': 'RPM',
    'Engine_fuel_flowrate': 'l/h',
    'Manifold_pressure': 'Inhg',
    'Engine_oil_pressure': 'PSI',
    'Engine_oil_temperature': '°C',
    'Fuel_level': 'liters',
    'Fuel_pressure': 'PSI',
    'Bat_Voltage_DC': 'V',
    'CT_1': '°C',
    'CT_2': '°C',
    'EGT_1': '°C',
    'EGT_2': '°C',
    'EGT1': '°C',
    'EGT2': '°C',
    'Engine_totaltime': 'h',
    'Flight_time': 's'
}

# Unit conversions - signals that need additional converted columns
DBC_SIGNAL_UNITS_CONVERTED = {
    'Vertical_speed': 'fpm',
    'Indicated_airspeed': 'knot',
    'Baro_corrected_altitude': 'ft',
    'Standard_altitude': 'ft',
    'Manifold_pressure': 'Inhg',
    'Engine_oil_pressure': 'PSI',
    'Fuel_level': '%',
    'Fuel_pressure': 'PSI',
    'GROUND_DISTANCE': 'nm'
}

def convert_unit_value(value, signal_name):
    """Convert a single value based on signal name"""
    try:
        val = float(value)
        
        if signal_name == 'Vertical_speed':
            # m/s to feet per minute: 1 m/s = 196.85 fpm
            return val * 196.85
        elif signal_name == 'Indicated_airspeed':
            # m/s to knots: 1 m/s = 1.943844 knots
            return val * 1.943844
        elif signal_name == 'Baro_corrected_altitude' or signal_name == 'Standard_altitude':
            # meters to feet: 1 m = 3.28084 ft
            return val * 3.28084
        elif signal_name == 'Manifold_pressure':
            # bar to InHg: 1 bar = 29.5300 InHg
            return val * 29.5300
        elif signal_name == 'Engine_oil_pressure' or signal_name == 'Fuel_pressure':
            # bar to PSI: 1 bar = 14.5038 PSI
            return val * 14.5038
        elif signal_name == 'Fuel_level':
            # Convert liters to percentage (max tank capacity is 52 liters)
            # Ensure the percentage doesn't exceed 100% and handle edge cases
            if val < 0:
                return 0.0  # Negative fuel levels should be 0%
            elif val > 52.0:
                return 100.0  # Cap at 100% for values above tank capacity
            else:
                return (val / 52.0) * 100.0
        elif signal_name == 'GROUND_DISTANCE':
            # meters to nautical miles: 1 m = 0.000539957 nautical miles
            return val * 0.000539957
        
        return val
    except (ValueError, TypeError):
        return value


def update_csv_units_from_dbc(csv_file_path):
    """Update CSV file units based on DBC signal mapping"""
    import csv
    try:
        # Read the CSV file
        with open(csv_file_path, 'r') as file:
            reader = csv.reader(file)
            rows = list(reader)
        
        if len(rows) < 1:
            return  # No headers available
        
        headers = rows[0]  # First row: signal names
        
        # Initialize units row with empty strings for all headers
        units_row = [''] * len(headers)
        
        # If there's already a units row, preserve it as starting point
        if len(rows) > 1:
            existing_units = rows[1]
            for i in range(min(len(existing_units), len(units_row))):
                units_row[i] = existing_units[i]
        
        # Update units based on DBC mapping, but keep empty for unmapped signals
        for i, header in enumerate(headers):
            if header in DBC_SIGNAL_UNITS:
                units_row[i] = DBC_SIGNAL_UNITS[header]
            else:
                # Keep as empty string if not in DBC mapping
                units_row[i] = ''
        
        # Update or insert the units row
        if len(rows) > 1:
            rows[1] = units_row
        else:
            rows.insert(1, units_row)  # Insert units row if it doesn't exist
        
        # Write back to CSV
        with open(csv_file_path, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(rows)
            
        logger.debug(f"Successfully updated units in CSV: {csv_file_path}")
        
    except Exception as e:
        logger.error(f"Error updating CSV units for {csv_file_path}: {e}")


def add_converted_unit_columns(csv_file_path):
    """Convert units for specified signals - replace original columns except for Fuel_level which gets additional column"""
    import csv
    try:
        # Read the CSV file
        with open(csv_file_path, 'r') as file:
            reader = csv.reader(file)
            rows = list(reader)
        
        if len(rows) < 2:
            return  # Need at least headers and units row
        
        headers = rows[0]  # First row: signal names
        units_row = rows[1]  # Second row: units
        
        # Find columns that need conversion
        conversion_columns = []
        fuel_level_columns = []  # Special handling for Fuel_level
        
        for i, header in enumerate(headers):
            if header in DBC_SIGNAL_UNITS_CONVERTED:
                if header == 'Fuel_level':
                    fuel_level_columns.append((i, header))
                else:
                    conversion_columns.append((i, header))
        
        # Handle regular conversions (replace original columns)
        for original_idx, signal_name in conversion_columns:
            converted_unit = DBC_SIGNAL_UNITS_CONVERTED[signal_name]
            # Update the units row to reflect the new unit
            units_row[original_idx] = converted_unit
            
            # Convert all data values in this column
            for row_idx in range(2, len(rows)):
                if original_idx < len(rows[row_idx]):
                    original_value = rows[row_idx][original_idx]
                    converted_value = convert_unit_value(original_value, signal_name)
                    rows[row_idx][original_idx] = f"{converted_value:.2f}" if isinstance(converted_value, float) else str(converted_value)
        
        # Handle Fuel_level special case (add new column, keep original)
        if fuel_level_columns:
            for original_idx, signal_name in fuel_level_columns:
                converted_unit = DBC_SIGNAL_UNITS_CONVERTED[signal_name]
                new_header = f"{signal_name}_{converted_unit}"
                
                # Add new header and unit
                rows[0].append(new_header)
                rows[1].append(converted_unit)
                
                # Add converted data for each data row
                for row_idx in range(2, len(rows)):
                    if original_idx < len(rows[row_idx]):
                        original_value = rows[row_idx][original_idx]
                        converted_value = convert_unit_value(original_value, signal_name)
                        rows[row_idx].append(f"{converted_value:.2f}" if isinstance(converted_value, float) else str(converted_value))
                    else:
                        rows[row_idx].append('')
        
        # Write back to CSV
        with open(csv_file_path, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(rows)
            
        logger.debug(f"Successfully updated unit conversions in CSV: {csv_file_path}")
        
    except Exception as e:
        logger.error(f"Error converting units for {csv_file_path}: {e}")





process = None


@eel.expose
def convert_multiple_files(input, output):
    logger.info(f"=== CONVERT MULTIPLE FILES STARTED ===")
    logger.info(f"Input folder: {input}")
    logger.info(f"Output folder: {output}")

    import psutil
    global process
    time_ad = True
    time_fz = False
    single_tb = True
    if process is not None:  # if process is already running
        try:
            logger.info(f"Terminating existing process with PID: {process.pid}")
            parent = psutil.Process(process.pid)
            for child in parent.children(recursive=True):
                child.kill()
            parent.kill()
            process = None  # reset the global variable
            logger.info("Successfully terminated existing process")
        except Exception as e:
            logger.error(f"Error terminating process: {e}")

    raster_rate = float('0.25')
    if input == "" or output == "":
        logger.warning("Input or output folder is empty")
        return "empty"
    else:
        logger.info("Starting file conversion process")
        from pathlib import Path
        from asammdf import MDF
        from pathlib import Path
        import glob
        import sys
        import os
        from datetime import timedelta
        

        in_folder = "{}".format(input)
        out_folder = "{}".format(output)

        # set variables
        mdf_extension = ".MF4"
        input_folder = "{}".format(in_folder)
        output_folder = "{}".format(out_folder)

        from zipfile import ZipFile
        import glob

        zip_files = glob.glob(f"{input_folder}/*.zip")

        if zip_files:  # Check if the list is not empty
            zip_file = zip_files[0]  # Take the first ZIP file from the list
            logger.info(f"Found ZIP file: {zip_file}, extracting...")
            passwd = b'0000'
            with ZipFile(zip_file, 'r') as zObject:
                zObject.extractall(path=input_folder, pwd=passwd)
            logger.info("ZIP file extracted successfully")
        else:
            logger.info("No ZIP files found in input folder")


        # RXD to MF4 Conversion
        import subprocess
        import time
        dbc_file_path = r'C:\Program Files (x86)\IBDS\DataPilot\Microlite.dbc'



        import os
        import glob
        import subprocess
        import time
        import psutil

        def terminate_process_and_children(pid):
            try:
                main_process = psutil.Process(pid)
                for child_process in main_process.children(recursive=True):
                    child_process.terminate()
                main_process.terminate()
            except psutil.NoSuchProcess:
                pass

        def monitor_file_size(file_path, pid, interval=1):
            initial_size = -1

            try:
                initial_size = os.path.getsize(file_path)
            except FileNotFoundError:
                initial_size = 0

            time.sleep(interval)

            try:
                current_size = os.path.getsize(file_path)
            except FileNotFoundError:
                current_size = 0

            if current_size == initial_size:
                terminate_process_and_children(pid)
                return True
            else:
                return False

        dbc_file_path = r'C:\Program Files (x86)\IBDS\DataPilot\Microlite.dbc'

        #while True:
            # try:  # Begin try block
            #     input_files = [os.path.splitext(os.path.basename(file))[0] for file in glob.glob(os.path.join(input_folder, "*.rxd"))]
            #     hello = [os.path.splitext(os.path.basename(file))[0] for file in glob.glob(os.path.join(output_folder, "*.mf4"))]

            #     unconverted_files = [file for file in input_files if file not in hello]

            #     if not unconverted_files:
            #         break

            #     for file in unconverted_files:
            #         rxd_file_path = os.path.join(input_folder, f"{file}.rxd")
            #         output_mf4_path = os.path.join(output_folder, f"{file}.mf4")

            #         rxd_mf4 = '&&'.join([
            #             'CD "C:\\Program Files (x86)\\IBDS\\DataPilot\\ReXdeskConvert"',
            #             f'rexdeskconvert convert-file -i "{rxd_file_path}" -o "{output_mf4_path}" -s can0 "{dbc_file_path}"'
            #         ])

            #         process = subprocess.Popen(rxd_mf4, shell=True, stderr=subprocess.PIPE)  # Capture errors

            #         if monitor_file_size(output_mf4_path, process.pid):
            #             print(f"File size didn't change for 2 seconds for {file}, terminating process and moving to next file.")
            #             error_output = process.stderr.read().decode()
            #             if error_output:
            #                 print(f"Error from rexdeskconvert for {file}: {error_output}")

            # except Exception as e:
            #     return(f"An error occurred: {e}")

        

    
        os.environ['PATH'] += os.pathsep + \
            r"C:\Program Files (x86)\IBDS\DataPilot\ReXdeskConvert"
        rxd_mf4 = [
            r'CD "C:\Program Files (x86)\IBDS\DataPilot\ReXdeskConvert"',
            'rexdeskconvert convert-folder -F mf4 -i "{}" -o "{}" -s can0 "{}"'.format(
                input_folder, output_folder, dbc_file_path
            )
        ]
        logger.info("Starting RXD to MF4 conversion")
        logger.debug(f"Conversion command: {' && '.join(rxd_mf4)}")
        subprocess.run('&&'.join(rxd_mf4), shell=True)
        logger.info("RXD to MF4 conversion completed")
    

        # load MDF/DBC files from input folder
        # contains output of the parent folder -- scratches
        
        path = Path(__file__).parent.absolute()
        path_in = Path(path, input_folder)  # input folder path
        path_out = Path(path, output_folder)  # output folder path

        # contains path of the DBC file (Customise)
        dbc_path = Path(r"C:\Program Files (x86)\IBDS\DataPilot")
        dbc_files = {"CAN": [(dbc, 0)
                                for dbc in list(dbc_path.glob("*" + ".dbc"))]}
        # DBC files loaded
        logger.info(f"DBC files loaded: {dbc_files}")
        # contains path of the log files
        logfiles = list(path_out.glob("*" + mdf_extension))
        
        from glob import glob
        file_list = glob(os.path.join(output_folder, '*.mf4'))
        logger.info(f"Found {len(file_list)} MF4 files to process: {file_list}")
        
        try:
            # Extract File Name from MF4
            for a in file_list:
                filename = os.path.splitext(os.path.basename(a))[0]
                logger.info(f"Processing MF4 file: {filename}")
                
                newlist = []
                newlist.append(a)
                mdf = MDF.concatenate(newlist)
                newlist = []

                # Scaled
                try:
                    available_signals = set(mdf.channels_db.keys())
                    logger.debug(f"Available signals in {filename}: {len(available_signals)} total")
                    logger.debug(f"First 10 available signals: {list(sorted(available_signals))[:10]}")
                    
                    signals = [
                        'Accelerometer_X',
                        'Accelerometer_Y', 
                        'Accelerometer_Z',
                        'Gyroscope_X',
                        'Gyroscope_Y',
                        'Gyroscope_Z',
                        'Accelerometer X',
                        'Accelerometer Y', 
                        'Accelerometer Z',
                        'Gyroscope X',
                        'Gyroscope Y',
                        'Gyroscope Z',
                        'DATETIME',
                        'LATITUDE',
                        'LONGITUDE',
                        'ALTITUDE',
                        'SPEED_OVER_GROUND',
                        'GROUND_DISTANCE',
                        'COURSE_OVER_GROUND',
                        'GEOID_SEPARATION',
                        'NUMBER_SATELLITES',
                        'QUALITY',
                        'GPS_Date_time',
                        'Acceleration_x_longitudinal',
                        'Acceleration_y_lateral',
                        'Acceleration_z_normal',
                        'Vertical_speed',
                        'Indicated_airspeed',
                        'Barometric_correction_QNH',
                        'Baro_corrected_altitude',
                        'Standard_altitude',
                        'Differentialpressure',
                        'Static_pressure',
                        'Engine_Speed',
                        'Engine_fuel_flowrate',
                        'Manifold_pressure',
                        'Engine_oil_pressure',
                        'Engine_oil_temperature',
                        'Fuel_level',
                        'Fuel_pressure',
                        'Bat_Voltage_DC',
                        'CT_1',
                        'CT_2',
                        'EGT_1',
                        'EGT_2',
                        'Engine_totaltime',
                        'Flight_time'
                    ]

                    # Find exact matches
                    filtered_signals = [signal for signal in signals if signal in available_signals]
                    
                    # Find missing signals
                    missing_signals = [signal for signal in signals if signal not in available_signals]
                    
                    logger.info(f"Found {len(filtered_signals)} exact signal matches")
                    logger.info(f"Missing {len(missing_signals)} signals, searching for similar ones...")
                    
                    # Try to find similar signal names for missing ones
                    for missing_sig in missing_signals:
                        # Look for signals that contain parts of the missing signal name
                        similar = [avail_sig for avail_sig in available_signals 
                                 if any(part.lower() in avail_sig.lower() 
                                       for part in missing_sig.replace('_', ' ').split() 
                                       if len(part) > 2)]
                        if similar:
                            # Add the first similar match to filtered signals
                            filtered_signals.append(similar[0])
                            logger.debug(f"Found similar signal for {missing_sig}: {similar[0]}")

                    # Remove problematic channels that cause ambiguity issues
                    problematic_channels = ['Timestamp', 'Time', 'time', 'timestamp']
                    cleaned_signals = []
                    removed_signals = []
                    
                    for signal in filtered_signals:
                        if signal in problematic_channels:
                            removed_signals.append(signal)
                            logger.debug(f"Removing problematic signal: {signal}")
                        else:
                            cleaned_signals.append(signal)
                    
                    if removed_signals:
                        logger.info(f"Removed {len(removed_signals)} problematic signals: {removed_signals}")
                    
                    logger.info(f"Final signal count for {filename}: {len(cleaned_signals)}")
                    
                    if cleaned_signals:
                        logger.info(f"Filtering and exporting signals for {filename}")
                        try:
                            mdf_scaled_signal_list = mdf.filter(cleaned_signals)

                            mdf_scaled_signal_list.save(
                                "{}".format(filename), overwrite=True)

                            mdf_scaled_signal_list.export("csv", filename=Path(path_out, "{}".format(
                                filename)), time_as_date=time_ad, time_from_zero=time_fz, single_time_base=single_tb, raster=raster_rate, add_units=True)
                            logger.info(f"Successfully exported CSV for {filename}")
                        except Exception as filter_error:
                            logger.error(f"Error during signal filtering for {filename}: {filter_error}")
                            # Try alternative approach - export without filtering
                            try:
                                logger.info(f"Attempting alternative export method for {filename}")
                                mdf.export("csv", filename=Path(path_out, "{}".format(
                                    filename)), time_as_date=time_ad, time_from_zero=time_fz, single_time_base=single_tb, raster=raster_rate, add_units=True)
                                logger.info(f"Successfully exported CSV using alternative method for {filename}")
                            except Exception as export_error:
                                logger.error(f"Alternative export also failed for {filename}: {export_error}")
                                raise export_error
                    else:
                        logger.warning(f"No signals found for {filename}")
                        
                except ValueError as e:
                    logger.error(f"ValueError during signal processing for {filename}: {e}")

                # Update CSV units based on DBC mapping
                myfilepath = os.path.join(output_folder, f"{filename}.csv")
                logger.info(f"Updating CSV units for {filename}")
                update_csv_units_from_dbc(myfilepath)
                
                # Add converted unit columns
                logger.info(f"Adding converted unit columns for {filename}")
                add_converted_unit_columns(myfilepath)

                import csv
                from datetime import datetime, timedelta

                # Read the CSV file and store the rows in a list
                logger.info(f"Processing CSV timestamps and formatting for {filename}")
                with open(myfilepath, 'r') as file:
                    reader = csv.reader(file)
                    rows = [row for row in reader]

                logger.debug(f"CSV has {len(rows)} rows")
                
                # Rename DATETIME column to GPS_DATE_TIME in the header row (if it exists)
                if rows and len(rows[0]) > 0:
                    for i, header in enumerate(rows[0]):
                        if header == 'DATETIME':
                            rows[0][i] = 'GPS_DATE_TIME'
                            logger.info(f"Renamed DATETIME column to GPS_DATE_TIME at index {i}")
                            break

                # Modify the rows
                for i, row in enumerate(rows):
                    # Skip the first two rows (headers and units)
                    if i < 2:
                        continue
                        
                    # Process timestamp column (first column)
                    text = row[0].strip()

                    if '+' in text:
                        new_str, _, _ = text.partition('+')
                    elif '-' in text:
                        new_str, _, _ = text.partition('-')
                    else:
                        new_str = text

                    # Truncate microseconds to six digits
                    if '.' in new_str:
                        base, micro = new_str.split('.')
                        truncated_micro = micro[:6]  # Keep only the first six digits
                        new_str = f"{base}.{truncated_micro}"

                    try:
                        dt = datetime.strptime(new_str, '%Y-%m-%d %H:%M:%S.%f')
                    except ValueError:
                        try:
                            dt = datetime.strptime(new_str, '%Y-%m-%d %H:%M:%S')
                        except ValueError:
                            logger.warning(f"Failed to parse date in row {i}: {new_str}")
                            continue

                    # Adjust the datetime by subtracting hours and minutes
                    dt = dt - timedelta(hours=5, minutes=30)

                    if '.' in new_str:
                        edit_str = dt.strftime('%Y-%m-%d %H:%M:%S.%f')
                    else:
                        edit_str = dt.strftime('%Y-%m-%d %H:%M:%S')

                    rows[i][0] = edit_str
                    
                    # Format numeric columns to 2 decimal places
                    for j in range(1, len(row)):
                        try:
                            # Try to convert to float and format to 2 decimal places
                            value = float(row[j])
                            rows[i][j] = f"{value:.2f}"
                        except (ValueError, TypeError):
                            # Keep original value if it's not a number
                            pass

                # Write the modified rows back to the CSV file
                with open(myfilepath, 'w', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerows(rows)


                file.close()

        except Exception as e:
            logger.error(f"Critical error in convert_multiple_files: {e}", exc_info=True)
            return f"An error occurred: {e}"

        # file_list = glob(os.path.join(output_folder, '*.mf4'))
        # for file in file_list:
        #     os.remove(file)

        # file_list = glob(os.path.join(path, '*.mf4'))
        # for file in file_list:
        #     os.remove(file)
        
        zip_files = glob(os.path.join(input_folder, '*.zip'))
        if zip_files:
            file_list = glob(os.path.join(input_folder, '*.rxd'))
            for file in file_list:
                os.remove(file)

        service_log = glob(os.path.join(input_folder, 'service.log'))
        for file in service_log:
            os.remove(file)

        file_list = glob(os.path.join(output_folder, '*.mf4'))
        for file in file_list:
            os.remove(file)

        file_list = glob(os.path.join(
            r"C:\Program Files (x86)\IBDS\DataPilot", '*.mf4'))
        for file in file_list:
            os.remove(file)

        file_list = glob(os.path.join(
            r"C:\Program Files (x86)\IBDS\DataPilot\ReXdeskConvert", '*.mf4'))
        for file in file_list:
            os.remove(file)
            
        # dist folder Mf4 removal
        file_list = glob(os.path.join(
            r"C:\Program Files (x86)\IBDS\DataPilot\dist", '*.mf4'))
        for file in file_list:
            os.remove(file)

        # dist folder Mf4 removal -- root folder
        file_list = glob(os.path.join(
            r"C:\Program Files (x86)\IBDS", '*.mf4'))
        for file in file_list:
            os.remove(file)

        logger.info("=== CONVERT MULTIPLE FILES COMPLETED SUCCESSFULLY ===")
        return "Congratulations! Your files have been converted."


@eel.expose
def pythonFunction(output, wildcard="*"):  
    logger.info("=== SINGLE FILE CONVERSION STARTED ===")
    logger.info(f"Output folder: {output}")
    logger.info(f"Wildcard: {wildcard}")

    import psutil
    global process
    time_ad = True
    time_fz = False
    single_tb = True
    if process is not None:  # if process is already running
        try:
            logger.info(f"Terminating existing process with PID: {process.pid}")
            parent = psutil.Process(process.pid)
            for child in parent.children(recursive=True):
                child.kill()
            parent.kill()
            process = None  # reset the global variable
            logger.info("Successfully terminated existing process")
        except Exception as e:
            logger.error(f"Error terminating process: {e}")


    # Get the path of the uploaded file
    global path_single
    import wx
    app = wx.App(None)
    style = wx.FD_OPEN | wx.FD_FILE_MUST_EXIST
    dialog = wx.FileDialog(None, 'Open', wildcard=wildcard, style=style)
    if dialog.ShowModal() == wx.ID_OK:
        path_single = dialog.GetPath()
        logger.info(f"User selected input file: {path_single}")
    else:
        path_single = None
        logger.warning("User cancelled file selection")
    dialog.Destroy()

    # Output folder selected
    output_folder = output

    raster_rate = float('0.25')
    from glob import glob
    from pathlib import Path
    from asammdf import MDF
    from pathlib import Path
    import glob
    import sys
    import os
    from datetime import timedelta

    if output_folder == "":
        pass
    else:
        input = r"{}".format(path_single)
        output_folder = r"{}".format(output_folder)

        pos = input.find(".rxd")
        count = 0
        icount = 0
        for i in input:
            icount += 1
            if i == "\\":
                count += 1
            else:
                pass
        count2 = 0
        jcount = 0
        for j in input:
            jcount += 1
            if j == "\\":
                count2 += 1
                if count2 == count:
                    break
            else:
                pass
        filename = input[jcount:pos]

        # set variables
        mdf_extension = ".MF4"
        input_file = input
        output_file = os.path.join(output_folder, f"{filename}.mf4")

    # Extract input file path
    input_folder = "{}".format(input_file)
    input_folder_path = os.path.dirname(input_folder)

    # RXD to MF4 Conversion
    import subprocess
    dbc_file_path = r'C:\Program Files (x86)\IBDS\DataPilot\Microlite.dbc'

    # Update the PATH environment variable
    os.environ['PATH'] += os.pathsep + r"C:\Program Files (x86)\IBDS\DataPilot\ReXdeskConvert"

    # Function to terminate a process and its children
    def terminate_process_and_children(pid):
        try:
            main_process = psutil.Process(pid)
            for child_process in main_process.children(recursive=True):
                child_process.terminate()
            main_process.terminate()
        except psutil.NoSuchProcess:
            pass

    # Function to monitor file size for changes
    def monitor_file_size(file_path, process, interval=2, retries=3):
        last_size = -1
        retry_count = 0
        
        while retry_count < retries:
            time.sleep(interval)
            
            # Check if file exists and get its size
            try:
                current_size = os.path.getsize(file_path)
            except FileNotFoundError:
                current_size = 0
            
            # If size hasn't changed, increase retry_count
            if current_size == last_size:
                retry_count += 1
            else:
                retry_count = 0  # Reset retry count if size changed
            
            # Update the last known size
            last_size = current_size

        # If maximum retries reached without size change, terminate process
        if retry_count == retries:
            terminate_process_and_children(process.pid)

    # Create the command dynamically
    basename_without_extension = os.path.splitext(os.path.basename(input_file))[0]
    output_file_path = os.path.join(output_folder, f"{basename_without_extension}.mf4")

    command = f'"C:\\Program Files (x86)\\Influx Technology\\ReXdeskConvert\\rexdeskconvert.exe" convert-file -F -I "{input_file}" -O "{output_file_path}" -s can0 "{dbc_file_path}"'
    process = subprocess.Popen(command, shell=True)

    # Monitor the output file for size changes
    monitor_file_size(output_file_path, process)

    
    # load MDF/DBC files from input folder
    # contains output of the parent folder -- scratches
    path = Path(__file__).parent.absolute()
    path_in = Path(path, input_folder_path)  # input folder path
    path_out = Path(path, output_folder)  # output folder path

    # Output folder path determined

    # contains path of the DBC file (Customise)
    


    from glob import glob
    file_list = glob(os.path.join(output_folder, '*.mf4'))
    
    
    # Extract File Name from MF4
    for a in file_list:       
        newlist = []
        newlist.append(a)
        mdf = MDF.concatenate(newlist)
        newlist = []
        filename = os.path.splitext(os.path.basename(a))[0]

        # Scaled
        # mdf_scaled = mdf.extract_bus_logging(
        #     dbc_files, ignore_invalid_signals=True)
        try:
            available_signals = set(mdf.channels_db.keys())
            
            signals = [
                'Accelerometer X',
                'Accelerometer Y',
                'Accelerometer Z',
                'Gyroscope X',
                'Gyroscope Y',
                'Gyroscope Z',
                'Accelerometer_X',
                'Accelerometer_Y',
                'Accelerometer_Z',
                'Gyroscope_X',
                'Gyroscope_Y',
                'Gyroscope_Z',
                'LATITUDE',
                'LONGITUDE',
                'ALTITUDE',
                'SPEED_OVER_GROUND',
                'GROUND_DISTANCE',
                'COURSE_OVER_GROUND',
                'GEOID_SEPARATION',
                'NUMBER_SATELLITES',
                'QUALITY',
                'SG_Accelerationinx_longitudinal',
                'SG_Accelerationiny_lateral',
                'SG_Accelerationinz_normal',
                'SG_Indicatedairspeed',
                'SG_Differentialpressure',
                'SG_EngineRPM',
                'SG_Enginefuelflowrate',
                'SG_Manifoldpressure',
                'SG_Engineoilpressure',
                'SG_Engine_oil_temperature',
                'SG_Fuellevel',
                'SG_Fuelsystempressure',
                'SG_Voltage_DC',
                'SG_CHT_indexinregisterA1',
                'SG_EGT_indexinregisterA1',
                'SG_Flighttime_section',
                'SG_Verticalspeed',
                'SG_Barometriccorrection_QNH',
                'SG_Barocorrectedaltitude',
                'SG_Standard_altitude',
                'SG_Static_pressure',
                'SG_Enginetotaltime',
            ]

            # Find exact matches
            filtered_signals = [signal for signal in signals if signal in available_signals]
            
            # Find missing signals
            missing_signals = [signal for signal in signals if signal not in available_signals]
            
            # Try to find similar signal names for missing ones
            for missing_sig in missing_signals:
                # Look for signals that contain parts of the missing signal name
                similar = [avail_sig for avail_sig in available_signals 
                         if any(part.lower() in avail_sig.lower() 
                               for part in missing_sig.replace('_', ' ').split() 
                               if len(part) > 2)]
                if similar:
                    # Add the first similar match to filtered signals
                    filtered_signals.append(similar[0])

            # Remove problematic channels that cause ambiguity issues
            problematic_channels = ['Timestamp', 'Time', 'time', 'timestamp']
            cleaned_signals = []
            removed_signals = []
            
            for signal in filtered_signals:
                if signal in problematic_channels:
                    removed_signals.append(signal)
                    logger.debug(f"Removing problematic signal: {signal}")
                else:
                    cleaned_signals.append(signal)
            
            if removed_signals:
                logger.info(f"Removed {len(removed_signals)} problematic signals: {removed_signals}")
            
            if cleaned_signals:
                try:
                    mdf_scaled_signal_list = mdf.filter(cleaned_signals)

                    mdf_scaled_signal_list.save(
                        "{}".format(filename), overwrite=True)

                    mdf_scaled_signal_list.export("csv", filename=Path(path_out, "{}".format(
                        filename)), time_as_date=time_ad, time_from_zero=time_fz, single_time_base=single_tb, raster=raster_rate, add_units=True)
                    logger.info(f"Successfully exported single file CSV for {filename}")
                except Exception as filter_error:
                    logger.error(f"Error during single file signal filtering for {filename}: {filter_error}")
                    # Try alternative approach - export without filtering
                    try:
                        logger.info(f"Attempting alternative export method for single file {filename}")
                        mdf.export("csv", filename=Path(path_out, "{}".format(
                            filename)), time_as_date=time_ad, time_from_zero=time_fz, single_time_base=single_tb, raster=raster_rate, add_units=True)
                        logger.info(f"Successfully exported single file CSV using alternative method for {filename}")
                    except Exception as export_error:
                        logger.error(f"Alternative export also failed for single file {filename}: {export_error}")
                        raise export_error
            else:
                logger.warning(f"No signals found for single file {filename}")
                
        except ValueError:
            pass

        # Update CSV units based on DBC mapping
        myfilepath = os.path.join(output_folder, f"{filename}.csv")
        update_csv_units_from_dbc(myfilepath)
        
        # Add converted unit columns
        add_converted_unit_columns(myfilepath)

        import csv
        from datetime import datetime, timedelta

        # Read the CSV file and store the rows in a list
        with open(myfilepath, 'r') as file:
            reader = csv.reader(file)
            rows = [row for row in reader]

        # Rename DATETIME column to GPS_DATE_TIME in the header row (if it exists)
        if rows and len(rows[0]) > 0:
            for i, header in enumerate(rows[0]):
                if header == 'DATETIME':
                    rows[0][i] = 'GPS_DATE_TIME'
                    break

        # Modify the rows
        for i, row in enumerate(rows):
            # Skip the first two rows (headers and units)
            if i < 2:
                continue
                
            # Process timestamp column (first column)
            text = row[0].strip()

            if '+' in text:
                new_str, _, _ = text.partition('+')
            elif '-' in text:
                new_str, _, _ = text.partition('-')
            else:
                new_str = text

            # Truncate microseconds to six digits
            if '.' in new_str:
                base, micro = new_str.split('.')
                truncated_micro = micro[:6]  # Keep only the first six digits
                new_str = f"{base}.{truncated_micro}"

            try:
                dt = datetime.strptime(new_str, '%Y-%m-%d %H:%M:%S.%f')
            except ValueError:
                try:
                    dt = datetime.strptime(new_str, '%Y-%m-%d %H:%M:%S')
                except ValueError:
                    continue

            # Adjust the datetime by subtracting hours and minutes
            dt = dt - timedelta(hours=5, minutes=30)

            if '.' in new_str:
                edit_str = dt.strftime('%Y-%m-%d %H:%M:%S.%f')
            else:
                edit_str = dt.strftime('%Y-%m-%d %H:%M:%S')

            rows[i][0] = edit_str
            
            # Format numeric columns to 2 decimal places
            for j in range(1, len(row)):
                try:
                    # Try to convert to float and format to 2 decimal places
                    value = float(row[j])
                    rows[i][j] = f"{value:.2f}"
                except (ValueError, TypeError):
                    # Keep original value if it's not a number
                    pass

        # Write the modified rows back to the CSV file
        with open(myfilepath, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(rows)


        file.close()

    
        # file_list = glob(os.path.join(output_folder, '*.mf4'))
        # for file in file_list:
        #     os.remove(file)

        # file_list = glob(os.path.join(path, '*.mf4'))
        # for file in file_list:
        #     os.remove(file)

        file_list = glob(os.path.join(input_folder, '*.rxd'))
        for file in file_list:
            os.remove(file)

        # dist folder Mf4 removal
        file_list = glob(os.path.join(
            r"C:\Program Files (x86)\IBDS\DataPilot\dist", '*.mf4'))
        for file in file_list:
            os.remove(file)

        # dist folder Mf4 removal -- root folder
        file_list = glob(os.path.join(
            r"C:\Program Files (x86)\IBDS", '*.mf4'))
        for file in file_list:
            os.remove(file)

        logger.info("=== SINGLE FILE CONVERSION COMPLETED SUCCESSFULLY ===")
        return path_single


@eel.expose
def select_input_folder():
    """Select input folder using file dialog"""
    import wx
    import os
    try:
        # Check if app already exists, if not create one
        app = wx.GetApp()
        if not app:
            app = wx.App(None)
        
        # Set default path
        default_path = r"C:\Program Files\Airforce_Application\Data"
        
        # Check if default path exists, if not use current directory
        if not os.path.exists(default_path):
            default_path = os.getcwd()
        
        dialog = wx.DirDialog(None, "Select RXD Files Folder", defaultPath=default_path, style=wx.DD_DEFAULT_STYLE)
        if dialog.ShowModal() == wx.ID_OK:
            selected_path = dialog.GetPath()
        else:
            selected_path = None
        dialog.Destroy()
        return selected_path
    except Exception:
        return None

@eel.expose
def select_output_folder():
    """Select output folder using file dialog"""
    import wx
    try:
        # Check if app already exists, if not create one
        app = wx.GetApp()
        if not app:
            app = wx.App(None)
        
        dialog = wx.DirDialog(None, "Select Save Destination", style=wx.DD_DEFAULT_STYLE)
        if dialog.ShowModal() == wx.ID_OK:
            selected_path = dialog.GetPath()
        else:
            selected_path = None
        dialog.Destroy()
        return selected_path
    except Exception:
        return None

@eel.expose
def create_automatic_output_folder(input_folder_path):
    """Create automatic output folder structure in Desktop/DataPilotFiles"""
    logger.info(f"Creating automatic output folder for: {input_folder_path}")
    import os
    import winreg
    
    def get_desktop_path():
        """Try multiple methods to get the desktop path"""
        desktop_paths_to_try = []
        
        # Method 1: Try modern registry key first
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders") as key:
                desktop_path = winreg.QueryValueEx(key, "Desktop")[0]
                # Expand environment variables if present (like %USERPROFILE%)
                desktop_path = os.path.expandvars(desktop_path)
                desktop_paths_to_try.append(desktop_path)
        except Exception:
            pass
        
        # Method 2: Try legacy registry key
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders") as key:
                desktop_path = winreg.QueryValueEx(key, "Desktop")[0]
                desktop_paths_to_try.append(desktop_path)
        except Exception:
            pass
        
        # Method 3: Use Windows API via environment variables
        try:
            userprofile = os.environ.get('USERPROFILE')
            if userprofile:
                desktop_path = os.path.join(userprofile, 'Desktop')
                desktop_paths_to_try.append(desktop_path)
        except Exception:
            pass
        
        # Method 4: Use os.path.expanduser
        try:
            home_path = os.path.expanduser("~")
            desktop_path = os.path.join(home_path, "Desktop")
            desktop_paths_to_try.append(desktop_path)
        except Exception:
            pass
        
        # Method 5: Try common Windows desktop locations
        try:
            common_paths = [
                os.path.join(os.environ.get('HOMEDRIVE', 'C:'), os.environ.get('HOMEPATH', ''), 'Desktop'),
                r"C:\Users\{}\Desktop".format(os.environ.get('USERNAME', 'Default')),
            ]
            
            for path in common_paths:
                if path and path not in desktop_paths_to_try:
                    desktop_paths_to_try.append(path)
        except Exception:
            pass
        
        # Test each path and return the first one that exists or can be accessed
        for desktop_path in desktop_paths_to_try:
            if desktop_path:
                try:
                    # Normalize the path
                    desktop_path = os.path.normpath(desktop_path)
                    
                    # Check if it exists or the parent directory exists
                    if os.path.exists(desktop_path) or os.path.isdir(os.path.dirname(desktop_path)):
                        logger.info(f"Found valid desktop path: {desktop_path}")
                        return desktop_path
                except Exception:
                    continue
        
        # If all methods fail, return None
        return None
    
    try:
        # Get desktop path using multiple methods
        desktop_path = get_desktop_path()
        
        if not desktop_path:
            # Ultimate fallback - use a folder in the user's home directory
            fallback_base = os.path.expanduser("~")
            if not fallback_base or fallback_base == "~":
                fallback_base = os.environ.get('USERPROFILE', r"C:\Users\Default")
            
            datapilot_folder = os.path.join(fallback_base, "DataPilotFiles")
        else:
            # Create DataPilotFiles folder on desktop
            datapilot_folder = os.path.join(desktop_path, "DataPilotFiles")
        
        # Create the DataPilot folder
        os.makedirs(datapilot_folder, exist_ok=True)
        
        # Get input folder name
        input_folder_name = os.path.basename(input_folder_path.rstrip(os.sep))
        if not input_folder_name:
            input_folder_name = "DataPilot_Output"
        
        # Create subfolder with same name as input folder
        output_folder = os.path.join(datapilot_folder, input_folder_name)
        os.makedirs(output_folder, exist_ok=True)
        
        logger.info(f"Successfully created output folder: {output_folder}")
        return output_folder
        
    except Exception:
        # Final emergency fallback
        try:
            import tempfile
            temp_dir = tempfile.gettempdir()
            emergency_folder = os.path.join(temp_dir, "DataPilotFiles")
            
            input_folder_name = os.path.basename(input_folder_path.rstrip(os.sep))
            if not input_folder_name:
                input_folder_name = "DataPilot_Output"
                
            output_folder = os.path.join(emergency_folder, input_folder_name)
            os.makedirs(output_folder, exist_ok=True)
            
            return output_folder
            
        except Exception as e:
            logger.error(f"Failed to create emergency fallback folder: {e}")
            return None


@eel.expose
def setup_logger(format_logger):
    logger.info(f"Setup logger called with format_logger={format_logger}")
    import subprocess
    import os

    import win32com.client

    wmi = win32com.client.GetObject("winmgmts:")
    list = []
    
    # Format logger parameter received
    for usb in wmi.InstancesOf("Win32_USBHub"):
        if 'ReXgen' in usb.Name:
            list.append('1')
            logger.info(f"Found ReXgen device: {usb.Name}")
        else:
            list.append('0')

    if '1' in list:
        # if firmware_update == True:
        #     # Reflash Rexgen Logger
        #     # Add the path to the system PATH
        #     os.environ['PATH'] += os.pathsep + \
        #         r"C:\Program Files (x86)\IBDS\DataPilot\ReXdeskConvert"

        #     # Directory where the .bin files are located
        #     dir_path = r"C:\Program Files (x86)\IBDS\DataPilot\firmware"

        #     # Find the .bin files in the directory
        #     bin_files = [f for f in os.listdir(dir_path) if f.endswith('.bin')]

        #     if bin_files:
        #         # Construct the reflash command using the first .bin file found
        #         reflash = r'''cd C:\Program Files (x86)\IBDS\DataPilot\ReXdeskConvert && rexdeskconvert reflash -I "{}"'''.format(
        #             os.path.join(dir_path, bin_files[0]))

        #         # Execute the command
        #         reflash_proc = subprocess.Popen(reflash, shell=True)
        #         reflash_proc.wait()
        #     else:
        #         pass

        if format_logger == True:
            # Format Rexgen Logger
            logger.info("Starting ReXgen logger formatting")
            os.environ['PATH'] += os.pathsep + \
                r"C:\Program Files (x86)\IBDS\DataPilot\ReXdeskConvert"
            format = r'''cd "C:\Program Files (x86)\IBDS\DataPilot\ReXdeskConvert" && rexdeskconvert format '''
            format_proc = subprocess.Popen(format, shell=True)
            format_proc.wait()
            logger.info("ReXgen logger formatting completed")

        # if send_config == True:
        #     # Send Configuration to Rexgen Logger
        #     # Add the path to the system PATH
        #     os.environ['PATH'] += os.pathsep + \
        #         r"C:\Program Files (x86)\IBDS\DataPilot\ReXdeskConvert"

        #     # Directory where the .rxc files are located
        #     dir_path = r"C:\Program Files (x86)\IBDS\DataPilot\configuration"

        #     # Find the .rxc files in the directory
        #     rxc_files = [f for f in os.listdir(dir_path) if f.endswith('.rxc')]

        #     if rxc_files:
        #         # Construct the configure command using the first .rxc file found
        #         config = r'''cd C:\Program Files (x86)\IBDS\DataPilot\ReXdeskConvert && rexdeskconvert configure -I "{}"'''.format(
        #             os.path.join(dir_path, rxc_files[0]))

        #         # Execute the command
        #         config_proc = subprocess.Popen(config, shell=True)
        #         config_proc.wait()
        #         return "done"
        #     else:
        #         pass

    else:
        logger.warning("No ReXgen device found - not connected")
        return "not connected"


@eel.expose
def extract_data():
    logger.info("Starting data extraction process")
    import subprocess
    global process
    try:
        process = subprocess.Popen(
            r"C:\Program Files (x86)\IBDS\DataPilot\InfluxSelfExtract.exe", shell=True)
        logger.info("Data extraction process started successfully")
        return "done"
    except Exception as e:
        logger.error(f"Failed to start data extraction process: {e}")
        return "error"


@eel.expose
def test_debug():
    """Simple test function to verify eel communication"""
    return "Test function executed successfully"

@eel.expose
def set_date_time():
    """Function called when Set Date Time button is clicked"""
    
    # Return debug info immediately without any complex logic
    import sys
    import os
    
    debug_info = []
    debug_info.append("FUNCTION ENTRY: set_date_time called")
    
    try:
        debug_info.append(f"Python version: {sys.version}")
        debug_info.append(f"Frozen: {getattr(sys, 'frozen', False)}")
        debug_info.append(f"Current working directory: {os.getcwd()}")
        
        # Check for the script file existence immediately
        script_paths = [
            r"C:\Program Files (x86)\IBDS\DataPilot\set_device_time_32bit.py",
            os.path.join(os.getcwd(), "set_device_time_32bit.py"),
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "set_device_time_32bit.py"),
        ]
        
        if getattr(sys, 'frozen', False):
            script_paths.insert(0, os.path.join(sys._MEIPASS, "set_device_time_32bit.py"))
        
        debug_info.append(f"Checking {len(script_paths)} script paths:")
        for i, path in enumerate(script_paths, 1):
            exists = os.path.exists(path)
            debug_info.append(f"  {i}. {'EXISTS' if exists else 'MISSING'}: {path}")
        
        # Find working script
        script_path = None
        for path in script_paths:
            if os.path.exists(path):
                script_path = path
                break
        
        if script_path:
            debug_info.append(f"FOUND SCRIPT: {script_path}")
        else:
            debug_info.append("NO SCRIPT FOUND!")
            return " | ".join(debug_info)
        
        # Check USB devices
        try:
            import win32com.client
            wmi = win32com.client.GetObject("winmgmts:")
            rexgen_found = False
            
            for usb in wmi.InstancesOf("Win32_USBHub"):
                if 'ReXgen' in usb.Name:
                    rexgen_found = True
                    break
            
            debug_info.append(f"ReXgen device found: {rexgen_found}")
            
            if not rexgen_found:
                debug_info.append("RETURNING: not connected")
                return "not connected"
                
        except Exception as usb_error:
            debug_info.append(f"USB check error: {str(usb_error)}")
            return " | ".join(debug_info)
        
        # Try to run the subprocess
        debug_info.append("ATTEMPTING SUBPROCESS...")
        return " | ".join(debug_info) + " | SHOULD NOT REACH HERE YET"
        
    except Exception as e:
        debug_info.append(f"EXCEPTION: {str(e)}")
        return " | ".join(debug_info)


# splash screen close
if getattr(sys, 'frozen', False):
    pyi_splash.close()

logger.info("Starting EEL web interface")
eel.start('opening.html', size=(1500, 700))

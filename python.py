import io
import sys

stream = io.StringIO()
sys.stdout = stream
sys.stderr = stream

# Splash screen initiation
if getattr(sys, 'frozen', False):
    import pyi_splash

import eel
eel.init("C:\Program Files (x86)\IBDS\DataPilot")

process = None


@eel.expose
def convert_multiple_files(input, output, time_ad, time_fz, single_tb):

    import psutil
    global process
    if process is not None:  # if process is already running
        try:
            print('Process found, attempting to terminate...')
            parent = psutil.Process(process.pid)
            for child in parent.children(recursive=True):
                print(f'Terminating child process {child.pid}...')
                child.kill()
            print(f'Terminating parent process {parent.pid}...')
            parent.kill()
            print('Successfully terminated process.')
            process = None  # reset the global variable
        except Exception as e:
            print(f'Error while terminating process: {e}')
    else:  # if process is not running
        print('No process found, proceeding...')

    raster_rate = float('0.5')
    if input == "" or output == "":
        return "empty"
    else:
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
            passwd = b'0000'
            with ZipFile(zip_file, 'r') as zObject:
                zObject.extractall(path=input_folder, pwd=passwd)
        else:
            print("No ZIP files found. Moving on...")


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
                for child_process in main_process.children(recursive=True):  # or parent.children() for recursive=False
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

        while True:
            try:  # Begin try block
                input_files = [os.path.splitext(os.path.basename(file))[0] for file in glob.glob(os.path.join(input_folder, "*.rxd"))]
                hello = [os.path.splitext(os.path.basename(file))[0] for file in glob.glob(os.path.join(output_folder, "*.mf4"))]

                unconverted_files = [file for file in input_files if file not in hello]

                if not unconverted_files:
                    break

                for file in unconverted_files:
                    rxd_file_path = os.path.join(input_folder, f"{file}.rxd")
                    output_mf4_path = os.path.join(output_folder, f"{file}.mf4")

                    rxd_mf4 = '&&'.join([
                        'CD "C:\\Program Files (x86)\\IBDS\\DataPilot\\ReXdeskConvert"',
                        f'rexdeskconvert convert-file -i "{rxd_file_path}" -o "{output_mf4_path}" -s can0 "{dbc_file_path}"'
                    ])

                    process = subprocess.Popen(rxd_mf4, shell=True, stderr=subprocess.PIPE)  # Capture errors

                    if monitor_file_size(output_mf4_path, process.pid):
                        print(f"File size didn't change for 2 seconds for {file}, terminating process and moving to next file.")
                        error_output = process.stderr.read().decode()
                        if error_output:
                            print(f"Error from rexdeskconvert for {file}: {error_output}")

            except Exception as e:
                return(f"An error occurred: {e}")

        

    
    # os.environ['PATH'] += os.pathsep + \
        #     r"C:\Program Files (x86)\IBDS\DataPilot\ReXdeskConvert"
        # rxd_mf4 = [
        #     'CD "C:\Program Files (x86)\IBDS\DataPilot\ReXdeskConvert"',
        #     'rexdeskconvert convert-folder -F mf4 -i "{}" -o "{}" -s can0 "{}"'.format(
        #         input_folder, output_folder, dbc_file_path
        #     )
        # ]
        # subprocess.run('&&'.join(rxd_mf4), shell=True)
    

        # load MDF/DBC files from input folder
        # contains output of the parent folder -- scratches
        
        path = Path(__file__).parent.absolute()
        path_in = Path(path, input_folder)  # input folder path
        path_out = Path(path, output_folder)  # output folder path

        # contains path of the DBC file (Customise)
        dbc_path = Path(r"C:\Program Files (x86)\IBDS\DataPilot")
        dbc_files = {"CAN": [(dbc, 0)
                                for dbc in list(dbc_path.glob("*" + ".dbc"))]}
        print('DBC FILESS---', dbc_files)
        # contains path of the log files
        logfiles = list(path_out.glob("*" + mdf_extension))
        
        from glob import glob
        file_list = glob(os.path.join(output_folder, '*.mf4'))
        
        try:
            # Extract File Name from MF4
            for a in file_list:
                newlist = []
                newlist.append(a)
                mdf = MDF.concatenate(newlist)
                newlist = []
                filename = os.path.splitext(os.path.basename(a))[0]
                print(filename)

                # Scaled
                # mdf_scaled = mdf.extract_bus_logging(
                #     dbc_files, ignore_invalid_signals=True)
                try:
                    available_signals = set(mdf.channels_db.keys())
                    signals = [
                        'SG_EngineRPM11',
                        'Accelerometer X',
                        'Accelerometer Y',
                        'Accelerometer Z',
                        'Gyroscope X',
                        'Gyroscope Y',
                        'Gyroscope Z',
                        'SG_Accelerationinx(longitudinal)1',
                        'SG_Accelerationiny(lateral)1',
                        'SG_Accelerationinz(normal)1',
                        'SG_Indicatedairspeed1',
                        'SG_Differentialpressure1',
                        'SG_Flighttime(section2.2.3)1',
                        'SG_Manifoldpressure11',
                        'SG_Engineoilpressure11',
                        'SG_Fuelsystempressure11',
                        'SG_Voltage(DC)11',
                        'SG_Engine_oil_temperature11',
                        'SG_CHT+indexinregisterA1',
                        'SG_EGT+indexinregisterA1',
                        'SG_Fuellevel11',
                        'LATITUDE',
                        'LONGITUDE',
                        'ALTITUDE',
                        'SPEED_OVER_GROUND',
                        'GROUND_DISTANCE',
                        'COURSE_OVER_GROUND',
                        'GEOID_SEPARATION',
                        'NUMBER_SATELLITES',
                        'QUALITY',
                        'SG_Barocorrectedaltitude_81',
                        'SG_Standard_altitude_81',
                        'SG_Verticalspeed_81',
                        'SG_Barometriccorrection(QNH)_81',
                        'SG_Static_pressure_81',
                        'SG_Enginetotaltime_81'
                    ]

                    filtered_signals = [
                        signal for signal in signals if signal in available_signals]

                    mdf_scaled_signal_list = mdf.filter(filtered_signals)

                    mdf_scaled_signal_list.save(
                        "{}".format(filename), overwrite=True)

                    mdf_scaled_signal_list.export("csv", filename=Path(path_out, "{}".format(
                        filename)), time_as_date=time_ad, time_from_zero=time_fz, single_time_base=single_tb, raster=raster_rate)
                except ValueError:
                    pass

                import csv
                myfilepath = r"{}\{}.csv".format(output_folder, filename)
                # Read the CSV file and store the rows in a list
                with open(myfilepath, 'r') as file:
                    reader = csv.reader(file)
                    rows = [row for row in reader]

                # Modify the rows
                from datetime import datetime, timedelta

                is_first_row = True
                for i, row in enumerate(rows):
                    if is_first_row:
                        is_first_row = False
                        continue  # Skip the first row
                    text = row[0]
                    pos = text.find('+')
                    new_str = text[0:pos]

                    # Parsing with the potential timezone information
                    new_str = new_str.strip()
                    try:
                        # Try to parse with microseconds and timezone
                        dt = datetime.strptime(new_str, '%Y-%m-%d %H:%M:%S.%f%z')
                    except ValueError:
                        try:
                            # If the above fails, try without the microseconds but with timezone
                            dt = datetime.strptime(new_str, '%Y-%m-%d %H:%M:%S%z')
                        except ValueError:
                            try:
                                # Try without timezone but with microseconds
                                dt = datetime.strptime(new_str, '%Y-%m-%d %H:%M:%S.%f')
                            except ValueError:
                                try:
                                    # If all above fail, try without microseconds and without timezone
                                    dt = datetime.strptime(new_str, '%Y-%m-%d %H:%M:%S')
                                except ValueError:
                                    # If all fails, raise the original error to alert you
                                    raise ValueError(f"Could not parse date: {new_str}")

                    # Adjust the time
                    dt = dt - timedelta(hours=5, minutes=30)
                    # Format the datetime object into a string
                    edit_str = dt.strftime('%Y-%m-%d %H:%M:%S.%f') if dt.microsecond else dt.strftime('%Y-%m-%d %H:%M:%S')
                    rows[i][0] = edit_str

                # Write the modified rows back to the CSV file
                with open(myfilepath, 'w', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerows(rows)


                file.close()
                
        except Exception as e:
            return f"An error occurred: {e}"

        file_list = glob(os.path.join(output_folder, '*.mf4'))
        for file in file_list:
            os.remove(file)

        file_list = glob(os.path.join(path, '*.mf4'))
        for file in file_list:
            os.remove(file)
        
        zip_files = glob(os.path.join(input_folder, '*.zip'))
        if zip_files:
            file_list = glob(os.path.join(input_folder, '*.rxd'))
            for file in file_list:
                os.remove(file)

        # dist folder Mf4 removal
        file_list = glob(os.path.join(
            "C:\Program Files (x86)\IBDS\DataPilot\dist", '*.mf4'))
        for file in file_list:
            os.remove(file)

        # dist folder Mf4 removal -- root folder
        file_list = glob(os.path.join(
            "C:\Program Files (x86)\IBDS", '*.mf4'))
        for file in file_list:
            os.remove(file)

        return "Congratulations! Your files have been converted."


@eel.expose
def pythonFunction(output, time_ad, time_fz, single_tb, wildcard="*"):

    import psutil
    global process
    if process is not None:  # if process is already running
        try:
            print('Process found, attempting to terminate...')
            parent = psutil.Process(process.pid)
            for child in parent.children(recursive=True):
                print(f'Terminating child process {child.pid}...')
                child.kill()
            print(f'Terminating parent process {parent.pid}...')
            parent.kill()
            print('Successfully terminated process.')
            process = None  # reset the global variable
        except Exception as e:
            print(f'Error while terminating process: {e}')
    else:  # if process is not running
        print('No process found, proceeding...')


    # Get the path of the uploaded file
    global path_single
    import wx
    app = wx.App(None)
    style = wx.FD_OPEN | wx.FD_FILE_MUST_EXIST
    dialog = wx.FileDialog(None, 'Open', wildcard=wildcard, style=style)
    if dialog.ShowModal() == wx.ID_OK:
        path_single = dialog.GetPath()
    else:
        path_single = None
    dialog.Destroy()

    print("output:::: ", output)
    output_folder = output

    raster_rate = float('0.5')
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
        output_file = "{}\{}.mf4".format(output_folder, filename)

    print("input: ", input_file)
    print("output: ", output_file)

    # Extract input file path
    input_folder = "{}".format(input_file)
    input_folder_path = os.path.dirname(input_folder)
    print("folder: ", input_folder_path)

    # RXD to MF4 Conversion
    import subprocess
    dbc_file_path = r'C:\Program Files (x86)\IBDS\DataPilot\Microlite.dbc'

    # RXD to MF4 Conversion
    import subprocess
    import time

    def terminate_process_and_children(pid):
        try:
            main_process = psutil.Process(pid)
            for child_process in main_process.children(recursive=True):  # or parent.children() for recursive=False
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


    rxd_mf4 = ['CD "C:\Program Files (x86)\IBDS\DataPilot\ReXdeskConvert"',
           'rexdeskconvert convert-file -i "{}" -o "{}" -s can0 "{}"'
           .format(input_file, output_file, dbc_file_path)]

    print(rxd_mf4)

    # Switch to subprocess.Popen
    process = subprocess.Popen('&&'.join(rxd_mf4), shell=True)

    # Make sure to wait for the process to complete before checking file size
    process.wait()

    if monitor_file_size(output_file, process.pid):
        print('done')
                


    # os.environ['PATH'] += os.pathsep + \
    #     r"C:\Program Files (x86)\IBDS\DataPilot\ReXdeskConvert"
    # import subprocess
    # command = f'"C:\\Program Files (x86)\\IBDS\\DataPilot\\ReXdeskConvert\\rexdeskconvert.exe" convert-file -F -I "{input_file}" -O "{output_file}" -s can0 "{dbc_file_path}"'
    # subprocess.run(command, shell=True)




    # load MDF/DBC files from input folder
    # contains output of the parent folder -- scratches
    path = Path(__file__).parent.absolute()
    path_in = Path(path, input_folder_path)  # input folder path
    path_out = Path(path, output_folder)  # output folder path

    print("OUTPUT FOLDER ----", path_out)

    # contains path of the DBC file (Customise)
    dbc_path = Path(
        r"C:\Program Files (x86)\IBDS\DataPilot\Microlite.dbc")
    dbc_files = {"CAN": [(dbc, 0)
                         for dbc in list(dbc_path.glob("*" + ".DBC"))]}
    print("DBCFILEEEEE-----", dbc_files)
    # contains path of the log files
    logfiles = list(path_out.glob("*" + mdf_extension))

    from glob import glob
    file_list = glob(os.path.join(output_folder, '*.mf4'))

    # Extract File Name from MF4
    for a in file_list:
        newlist = []
        newlist.append(a)
        mdf = MDF.concatenate(newlist)
        newlist = []
        filename = os.path.splitext(os.path.basename(a))[0]
        print(filename)

        # Scaled
        # mdf_scaled = mdf.extract_bus_logging(
        #     dbc_files, ignore_invalid_signals=True)
        try:
            available_signals = set(mdf.channels_db.keys())
            signals = [
                'SG_EngineRPM11',
                'Accelerometer X',
                'Accelerometer Y',
                'Accelerometer Z',
                'Gyroscope X',
                'Gyroscope Y',
                'Gyroscope Z',
                'SG_Accelerationinx(longitudinal)1',
                'SG_Accelerationiny(lateral)1',
                'SG_Accelerationinz(normal)1',
                'SG_Indicatedairspeed1',
                'SG_Differentialpressure1',
                'SG_Flighttime(section2.2.3)1',
                'SG_Manifoldpressure11',
                'SG_Engineoilpressure11',
                'SG_Fuelsystempressure11',
                'SG_Voltage(DC)11',
                'SG_Engine_oil_temperature11',
                'SG_CHT+indexinregisterA1',
                'SG_EGT+indexinregisterA1',
                'SG_Fuellevel11',
                'LATITUDE',
                'LONGITUDE',
                'ALTITUDE',
                'SPEED_OVER_GROUND',
                'GROUND_DISTANCE',
                'COURSE_OVER_GROUND',
                'GEOID_SEPARATION',
                'NUMBER_SATELLITES',
                'QUALITY',
                'SG_Barocorrectedaltitude_81',
                'SG_Standard_altitude_81',
                'SG_Verticalspeed_81',
                'SG_Barometriccorrection(QNH)_81',
                'SG_Static_pressure_81',
                'SG_Enginetotaltime_81'
            ]

            filtered_signals = [
                signal for signal in signals if signal in available_signals]

            mdf_scaled_signal_list = mdf.filter(filtered_signals)

            mdf_scaled_signal_list.save(
                "{}".format(filename), overwrite=True)

            mdf_scaled_signal_list.export("csv", filename=Path(path_out, "{}".format(
                filename)), time_as_date=time_ad, time_from_zero=time_fz, single_time_base=single_tb, raster=raster_rate)
        except ValueError:
            pass

        import csv
        myfilepath = r"{}\{}.csv".format(output_folder, filename)
        # Read the CSV file and store the rows in a list
        with open(myfilepath, 'r') as file:
            reader = csv.reader(file)
            rows = [row for row in reader]

        # Modify the rows
        from datetime import datetime, timedelta
        is_first_row = True
        for i, row in enumerate(rows):
            if is_first_row:
                is_first_row = False
                continue  # Skip the first row
            text = row[0]
            pos = text.find('+')
            new_str = text[0:pos]

            try:
                dt = datetime.strptime(new_str[:26], '%Y-%m-%d %H:%M:%S.%f')
                dt = dt - timedelta(hours=5, minutes=30)

                edit_str = dt.strftime('%Y-%m-%d %H:%M:%S.%f')
                rows[i][0] = edit_str

            except ValueError:
                dt = datetime.strptime(new_str, '%Y-%m-%d %H:%M:%S')
                dt = dt - timedelta(hours=5, minutes=30)

                edit_str = dt.strftime('%Y-%m-%d %H:%M:%S')
                rows[i][0] = edit_str

        # Write the modified rows back to the CSV file
        with open(myfilepath, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(rows)

        file.close()

        file_list = glob(os.path.join(output_folder, '*.mf4'))
        for file in file_list:
            os.remove(file)

        file_list = glob(os.path.join(path, '*.mf4'))
        for file in file_list:
            os.remove(file)

        file_list = glob(os.path.join(input_folder, '*.rxd'))
        for file in file_list:
            os.remove(file)

        # dist folder Mf4 removal
        file_list = glob(os.path.join(
            "C:\Program Files (x86)\IBDS\DataPilot\dist", '*.mf4'))
        for file in file_list:
            os.remove(file)

        # dist folder Mf4 removal -- root folder
        file_list = glob(os.path.join(
            "C:\Program Files (x86)\IBDS", '*.mf4'))
        for file in file_list:
            os.remove(file)

        return path_single


@eel.expose
def setup_logger(firmware_update, format_logger, send_config):
    import subprocess
    import os

    import win32com.client

    wmi = win32com.client.GetObject("winmgmts:")
    list = []

    for usb in wmi.InstancesOf("Win32_USBHub"):
        if 'ReXgen' in usb.Name:
            list.append('1')
        else:
            list.append('0')

    if '1' in list:
        if firmware_update == True:
            # Reflash Rexgen Logger
            # Add the path to the system PATH
            os.environ['PATH'] += os.pathsep + \
                r"C:\Program Files (x86)\IBDS\DataPilot\ReXdeskConvert"

            # Directory where the .bin files are located
            dir_path = r"C:\Program Files (x86)\IBDS\DataPilot\firmware"

            # Find the .bin files in the directory
            bin_files = [f for f in os.listdir(dir_path) if f.endswith('.bin')]

            if bin_files:
                # Construct the reflash command using the first .bin file found
                reflash = r'''cd C:\Program Files (x86)\IBDS\DataPilot\ReXdeskConvert && rexdeskconvert reflash -I "{}"'''.format(
                    os.path.join(dir_path, bin_files[0]))

                # Execute the command
                reflash_proc = subprocess.Popen(reflash, shell=True)
                reflash_proc.wait()
            else:
                pass

        if format_logger == True:
            # Format Rexgen Logger
            os.environ['PATH'] += os.pathsep + \
                r"C:\Program Files (x86)\IBDS\DataPilot\ReXdeskConvert"
            format = r'''cd C:\Program Files (x86)\IBDS\DataPilot\ReXdeskConvert && rexdeskconvert format '''
            format_proc = subprocess.Popen(format, shell=True)
            format_proc.wait()

        if send_config == True:
            # Send Configuration to Rexgen Logger
            # Add the path to the system PATH
            os.environ['PATH'] += os.pathsep + \
                r"C:\Program Files (x86)\IBDS\DataPilot\ReXdeskConvert"

            # Directory where the .rxc files are located
            dir_path = r"C:\Program Files (x86)\IBDS\DataPilot\configuration"

            # Find the .rxc files in the directory
            rxc_files = [f for f in os.listdir(dir_path) if f.endswith('.rxc')]

            if rxc_files:
                # Construct the configure command using the first .rxc file found
                config = r'''cd C:\Program Files (x86)\IBDS\DataPilot\ReXdeskConvert && rexdeskconvert configure -I "{}"'''.format(
                    os.path.join(dir_path, rxc_files[0]))

                # Execute the command
                config_proc = subprocess.Popen(config, shell=True)
                config_proc.wait()
                return "done"
            else:
                pass

    else:
        return "not connected"


@eel.expose
def extract_data():
    import subprocess
    global process
    print('Starting new process...')
    try:
        process = subprocess.Popen(
            r"C:\Program Files (x86)\IBDS\DataPilot\InfluxSelfExtract.exe", shell=True)
        print('Successfully started new process.')
        return "done"
    except Exception as e:
        print(f'Error while starting process: {e}')


# splash screen close
if getattr(sys, 'frozen', False):
    pyi_splash.close()

eel.start('opening.html', size=(1500, 700))

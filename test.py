# from zipfile import ZipFile
# import glob
# input_folder = "D:\SharedFolder\suprava\github"
# zip_files = glob.glob(f"{input_folder}/*.zip")[0]
# passwd = b'0000'
# print(zip_files)
# with ZipFile(zip_files, 'r') as zObject:
#     zObject.extractall(path=input_folder, pwd=passwd)


# import os
# os.startfile("D:\SharedFolder\suprava\VS code\Airforce\InfluxSelfExtract.exe")

# import subprocess
# subprocess.call("InfluxSelfExtract.exe", shell=True)

# import csv

# myfilepath = r'D:\SharedFolder\suprava\github\test\testfile.csv'

# # Read the CSV file and store the rows in a list
# with open(myfilepath, 'r') as file:
#     reader = csv.reader(file)
#     rows = [row for row in reader]

# # Modify the rows
# for row in rows:
#     text = row[0]
#     pos = text.find('+')
#     new_str = text[0:pos]
#     row[0] = new_str

# # Write the modified rows back to the CSV file
# with open(myfilepath, 'w', newline='') as file:
#     writer = csv.writer(file)
#     writer.writerows(rows)

   


from pathlib import Path
from asammdf import MDF
from pathlib import Path
import glob
import sys
import os
from datetime import timedelta

time_ad = True
time_fz = False
single_tb = True
raster_rate = int('4')

input = r'D:\SharedFolder\suprava\github'
output = r'D:\SharedFolder\suprava\github\Output'

in_folder = "{}".format(input)
out_folder = "{}".format(output)

# set variables
mdf_extension = ".MF4"
input_folder = "{}".format(in_folder)
output_folder = "{}".format(out_folder)

#Extract from ZIP file
from zipfile import ZipFile
zip_files = glob.glob(f"{input_folder}/*.zip")[0]
passwd = b'0000'
with ZipFile(zip_files, 'r') as zObject:
    zObject.extractall(path=input_folder, pwd=passwd)

# RXD to MF4 Conversion
os.environ['PATH'] += os.pathsep + \
    r"C:\Program Files (x86)\Influx Technology\Rexdeskconvert"
rxd_mf4 = '''CD C:\Program Files (x86)\Influx Technology\Rexdeskconvert&&rexdeskconvert convert-folder -F mf4 -I "{}" -O "{}" '''.format(
    input_folder, output_folder)
os.system(rxd_mf4)

# load MDF/DBC files from input folder
# contains output of the parent folder -- scratches
path = Path(__file__).parent.absolute()
path_in = Path(path, input_folder)  # input folder path
path_out = Path(path, output_folder)  # output folder path

print("OUTPUT FOLDER ----", path_out)

# contains path of the DBC file (Customise)
dbc_path = Path(r"D:\SharedFolder\suprava\VS code\Airforce")
dbc_files = {"CAN": [(dbc, 0) for dbc in list(dbc_path.glob("*" + ".DBC"))]}
print("DBCFILEEEEE-----",dbc_files)
# contains path of the log files
logfiles = list(path_out.glob("*" + mdf_extension))

from glob import glob
file_list = glob(os.path.join(output_folder, '*.mf4'))

# Extract File Name from MF4
for a in file_list:
    print("The a in the list is ", a)
    newlist = []
    newlist.append(a)
    mdf = MDF.concatenate(newlist)
    newlist = []
    # mdf = a
    pos = a.find(".mf4")
    count = 0
    icount = 0
    for i in a:
        icount += 1
        if i == "\\":
            count += 1
        else:
            pass
    count2 = 0
    jcount = 0
    for j in a:
        jcount += 1
        if j == "\\":
            count2 += 1
            if count2 == count:
                break
        else:
            pass

    filename = a[jcount:pos]

    # Scaled
    mdf_scaled = mdf.extract_bus_logging(
        dbc_files, ignore_invalid_signals=True)            
    mdf_scaled.save("{}".format(filename), overwrite=True)
    mdf_scaled.export("csv", filename=Path(path_out, "{}".format(
        filename)), time_as_date=time_ad, time_from_zero=time_fz, single_time_base=single_tb, raster=raster_rate)
    
    import csv
    myfilepath = r"{}\{}.csv".format(output_folder,filename)
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



# from datetime import datetime, timedelta
# new_str = "2023-02-27 18:32:06.000720128"
# text_s = str(new_str)
# dt = datetime.strptime(text_s[:26], '%Y-%m-%d %H:%M:%S.%f')

# # Subtract 5 hours and 30 minutes from the datetime object
# dt = dt - timedelta(hours=5, minutes=30)

# # Format the datetime object back into a string
# edit_str = dt.strftime('%Y-%m-%d %H:%M:%S.%f')
# print(edit_str)



import pandas as pd
import os
from sys import exit

def exit_or_continue(reason):  # Utility function
    print(reason)
    if input('Exit: e | Press any key to continue...') == 'e':
        exit()

def read_executable_path_info(file_name, split_by='='):
    path_info = dict()
    inputs = read_txt(file_name, exit_on_missing_file=False)
    
    path_info['browser'] = None
    path_info['driver'] = None
    path_info['headless'] = 'false'
    
    for line in inputs:
        try:
            parts = line.split(split_by)
            key = parts[0].strip()
            value = parts[1].strip()
        
            path_info[key] = value
        except:
            pass
    
    return path_info

def read_contact_info(file_name, split_by=':'):
    contact_info = dict()
    inputs = read_txt(file_name, exit_on_missing_file=True)
    
    for line in inputs:
        try:
            parts = line.split(split_by)
            key = parts[0].strip()
            value = parts[1].strip()
        
            contact_info[key] = value
        except:
            break
    
    return contact_info

def read_txt(file_name, exit_on_missing_file=True):
    data = []
    file_dir = os.getcwd() + r"\\" + file_name
    try:
        with open(file_dir, "r", encoding="utf8", errors="surrogateescape") as file:
            str_data = file.read()
            list = str_data.split("\n")
            for line in list:
                data.append(line.strip())
    except Exception as e:
        if exit_on_missing_file:
            exit_or_continue(reason=f'{file_name} not found in {file_dir}\n{e}')
    
    # data = ['a', 'b', 'c', 'd']
    return data

def write_to_txt(data, lable=False, file_name='output.txt'):
    file_dir = os.getcwd() + "/" + file_name
    try:
        with open(file_dir, "w") as file:
            # data = ['a', 'b', 'c', 'd']
            if lable:
                file.write(f'{lable}\n')
            for line in data:
                file.write(f'{line}\n')
    except PermissionError:
        exit_or_continue(reason=f'Permission error, please close the file {file_dir}')
    except Exception as e:
        exit_or_continue(reason=f'{file_name} not found in {file_dir}\n{e}')

def read_csv(file_name, list_of_dictionaries = False, exit_on_empty=True):
    file_dir = os.getcwd() + "/" + file_name
    data = []
    try:
        df = pd.read_csv(file_dir)
        if list_of_dictionaries:
            data = df.to_dict('records')
        else:
            data = df.values.tolist()
    except Exception as e:
        if exit_on_empty:
            exit_or_continue(reason=f'{file_name} is empty.\n{e}')
    
    # Returning data as a list
    return data

def write_to_csv(data, labels=None, file_name = 'output.csv', alternative_filename = ''):
    file_dir = os.getcwd() + "/" + file_name
    alt_file_dir = os.getcwd() + "/" + alternative_filename
        
    header = True if labels else False
    
    try:
        pd.DataFrame(data, columns=labels).to_csv(file_dir, index=False, header=header)
    except PermissionError:
        if alternative_filename != '':
            pd.DataFrame(data, columns=labels).to_csv(alt_file_dir, index=False, header=header)
        else:
            exit_or_continue(reason=f"PermissionError: Can't write to {file_dir} file, Close the file first")
    except Exception as e:
            exit_or_continue(reason=f"Error: Can't write to {file_dir} file.\n{e}")


def write_to_excel(data, labels=None, file_name = 'output.xlsx', alternative_filename= ''):
    header = True if labels else False
    
    file_dir = os.getcwd() + "/" + file_name
    alt_file_dir = os.getcwd() + "/" + alternative_filename    
    
    
    try:
        pd.DataFrame(data, columns=labels).to_excel(file_dir, index=False, header=header)
    except PermissionError:
        if alternative_filename != '':
            pd.DataFrame(data, columns=labels).to_csv(alt_file_dir, index=False, header=header)
        else:
            exit_or_continue(reason=f"PermissionError: Can't write to {file_dir} file, Close the file first")
    except Exception as e:
            exit_or_continue(reason=f"Error: Can't write to {file_dir} file.\n{e}")
        

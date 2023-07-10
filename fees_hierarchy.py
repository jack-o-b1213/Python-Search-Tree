import time
import tkinter
from tkinter import filedialog

import numpy as np
import pandas as pd
from models.data_import import ImportData
from models.tree import Node, Tree, buildHierarchy, getValues, printTree


response = ''

def print_menu(data_object):
    print("Available Departments: ", [agg for agg in data_object.departments])
    print("Available Categories: ", [agg for agg in data_object.categories])
    print("Available Sub Categories: ", [agg for agg in data_object.sub_categories])
    print("Available Fee Types: ", [agg for agg in data_object.types])
    print("Available functions: ", [agg for agg in data_object.aggregate_function])
    print("Enter 'exit' to close app")


def formatQuery(queryData):
    steps = queryData[1:]
    while steps and steps[-1] == '':
        steps = steps[:-1]

    return steps


def calculateFees(hierarchy, steps, q_department, q_agg):
    if not steps and q_department == '' and q_agg == '' or (not steps and q_department == ''):
        print("No valid department or path provided")
        return 'Invalid Query'

    fees = [generateResult(hierarchy[q_department], steps, q_agg)] if q_department != '' else [
        generateResult(tree, steps, q_agg) for tree in hierarchy.values()]
    try:
        match q_agg:
            case 'total':
                returnVal = int(sum(fees))
            case 'max':
                returnVal = int(max(fees))
            case 'min':
                returnVal = int(min(fees))
            case 'avg':
                returnVal = int(np.mean(fees))
            case _:
                returnVal = 'Invalid Query'
        return returnVal if returnVal != 0 else 'Invalid Query'
    except Exception as e:
        print("EXCEPTION - ", e)
        return 'Invalid Query'


def generateResult(tree, node_path, q_agg):
    try:
        nodes = tree.Traverse(node_path)
    except KeyError:
        return 0
    fees_df = pd.DataFrame({'Id': pd.Series(dtype='str'),
                            'Department__c': pd.Series(dtype='str'),
                            'Category__c': pd.Series(dtype='str'),
                            'Sub_Category__c': pd.Series(dtype='str'),
                            'Type__c': pd.Series(dtype='str'),
                            'Fee': pd.Series(dtype='int')})
    for node in nodes:
        fees_df = pd.concat([fees_df, getValues(node)])

    match q_agg:
        case 'total':
            returnVal = fees_df['Fee'].sum()
        case 'max':
            returnVal = fees_df['Fee'].max()
        case 'min':
            returnVal = fees_df['Fee'].min()
        case 'avg':
            returnVal = fees_df['Fee'].mean()
        case _:
            returnVal = 0
    return returnVal


def consoleApp():
    global response
    # print("""Please select the file you wish to load""")
    # time.sleep(3)
    # tkinter.Tk().withdraw()  # prevents an empty tkinter window from appearing
    #
    # folder_path = filedialog.askopenfilename()

    csv_data = ImportData('data/raw_fees.csv')
    csv_data.print_details()
    hierarchy = buildHierarchy(csv_data)
    print_menu(csv_data)
    while response.lower() != 'exit':
        print("Please enter query")
        response = input()
        print(f"You selected the following: {response}")
        response = response.lower()
        q_department, q_category, q_sub_category, q_fee_type, q_agg = csv_data.extractQuery(response)
        query = f"{q_department}:{q_category}:{q_sub_category}:{q_fee_type}".replace(' ', '_').split(':')
        try:

            steps = formatQuery(query)
            total_fees = calculateFees(hierarchy, steps, q_department, q_agg)
            print(total_fees)

        except KeyError as err:
            print(f"Invalid selection please select a valid department = {err}")


if __name__ == '__main__':
    print(consoleApp())
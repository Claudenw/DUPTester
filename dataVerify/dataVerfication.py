#!/usr/bin/python3
# -*- coding:utf-8 -*-

import argparse
import math
import numpy as np, pandas as pd


dataFrame = pd.read_csv('upgrade_failure_study_cases.csv')
df = dataFrame.fillna('N/A')

def verficateAllData():

    res = {}

    for column in df.keys()[2:10]:

        res[column] = {}

        for label in set(df[column]):
            ratio = (len(df[df[column]==label]) / len(df))* 100
            res[column][label] = str(round(ratio, 2)) + "%"

    # output the result

    for column in res.keys():
        print("\n---------------------------------------------------------------------------------------------------")
        print(column + "\n")
        for label in res[column]:
            print(label + '\t' + res[column][label])
        print("\n")

def verficatePartialData():
    i = 0
    for column in df.keys():
        print(str(i) + ". " + column)
        i=i+1

    column_number = int(input("Select the column:"))
    while column_number<0 or column_number>i:
        print("Invaild input")
        column_number = int(input("Select the column:"))

    column = df.keys()[column_number]
    res = {}

    if column == "Priority":
        cass_only = ['Normal', 'Urgent', 'Low']
        case_num = 0
        for ticket in set(df["Issue key"]):
            if ticket.find("CASSANDRA") ==  -1:
                case_num = case_num+1
        for label in set(df[column]):
            if label in cass_only:
                ratio = (len(df[df[column] == label]) / (len(df) - case_num) )* 100
            else:
                ratio = (len(df[df[column] == label]) / case_num) * 100
                         
            res[label] = str(round(ratio, 2)) + "%"

    else:
        for label in set(df[column]):
            ratio = (len(df[df[column] == label]) / len(df)) * 100
            res[label] = str(round(ratio, 2)) + "%"

    print("\n---------------------------------------------------------------------------------------------------")
    print(column + "\n")
    if column == "Priority":
        print("Priority of Cassandra is different from other systems, only include 'Normal', 'Urgent' and 'Low'\n")
    for label in res:
        print(label + '\t' + res[label] + '\t' + str(len(df[df[column] == label])) )
    print("---------------------------------------------------------------------------------------------------\n")



if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="Verify data on the data results obtained from the study of 96 cases.",
                                     epilog="Example usage: python dataVerfication.py")


    while True:
        option = input("A. Percentage of all data \nB. Select a specific column \nC. Exit\n")

        if option not in ['A', 'B', 'C']:
            print("Invaild input")
            continue

        if option == 'C':
            break
        elif option == 'A':
            verficateAllData()
        elif option == 'B':
            verficatePartialData()










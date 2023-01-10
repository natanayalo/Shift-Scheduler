#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Dec 25 06:19:40 2022

@author: ayalo
"""

import PySimpleGUI as sg
import os, json
from pathlib import Path 
import random, copy
from collections import Counter


def build_schedule(restriction_file):
    # List of shifts
    shifts = ["Morning", "Evening", "Night"]
    
    # List of days
    days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
    
    
    #detailed shift list
    open_shifts = []
    for day in days:
        for shift in shifts:
            open_shifts.append(day+" "+shift)
            
    
    
       
    # Load Dictionary of restrictions
    restrictions = json.load(open(restriction_file))
    
    #get list of employees
    employees = list(restrictions.keys())
    
    #probability list
    weights = [100000 for employee in employees]
    
    
    # Flatten the list of restrictions into a single list
    restrictions_list = [shift for shifts in restrictions.values() for shift in shifts]
    
    # Count the number of occurrences of each shift
    rest_counts = Counter(restrictions_list)
    
    #find potential problematic  shifts
    problematic_shifts = [shift for shift in open_shifts if rest_counts[shift]>2]
    
    # List of shifts for each employee
    schedule =  {employee: [] for employee in employees}
    # Create empty shift array
    shift_array = {day: [1,2,3] for day in days}
    
    def block_shifts(employee,shift,day,rest_copy):
        shift_idx = open_shifts.index(day+" "+shift)
        new_restrictions = []
        for i in range(0,3):
            new_restrictions.append(open_shifts[max(0,shift_idx - i)])
            new_restrictions.append(open_shifts[min(len(open_shifts)-1,shift_idx + i)])
        if shift == "Night":
            for day in days:
                new_restrictions.append(day+" "+shift)
        for rest in new_restrictions:
            if rest not in rest_copy[employee]:
                rest_copy[employee].append(rest)
            
    available_employees = None
    empty_slots = []
    
    while(not available_employees):
        #copy the initial start for this attempt
        rest_copy = copy.deepcopy(restrictions)
        schedule_copy = copy.deepcopy(schedule)
        shifts_copy = copy.deepcopy(shift_array)
        open_shifts_copy = copy.deepcopy(open_shifts)
        weights_copy = copy.deepcopy(weights)
        
        #first try to find solution for the problematic shifts
        for problematic_shift in problematic_shifts:
            day = problematic_shift.split(" ")[0]
            shift = problematic_shift.split(" ")[1]
            open_shifts_copy.remove(problematic_shift)
            available_employees = [employee for employee in employees if problematic_shift not in rest_copy[employee]]
            
            if not available_employees:
                #mark the shift as missing
                shifts_copy[day][shifts.index(shift)] = "Missing"
                empty_slots.append(problematic_shift)
                break
            #get the available employees weights
            weight = [weights_copy[employees.index(employee)] for employee in available_employees]
            
            # Choose a random employee from the availables list for this shift
            employee = random.choices(available_employees, weight, k=1)[0]
            
            # Add shift to employee's schedule
            schedule_copy[employee].append((day, shift))
            shifts_copy[day][shifts.index(shift)] = employee
            
            # block overlapping shifts
            block_shifts(employee, shift, day,rest_copy)
            
            #update the weight of the employee
            weights_copy[employees.index(employee)] /= 100
        
            
        for open_shift in open_shifts_copy:
            day = open_shift.split(" ")[0]
            shift = open_shift.split(" ")[1]
    
            # Get list of employees who can work in this shift
            available_employees = [employee for employee in employees if open_shift not in rest_copy[employee]]
            # if we found employees who can work
            if available_employees:
                # Choose a random employee for this shift
                weight = [weights_copy[employees.index(employee)] for employee in available_employees]
                employee = random.choices(available_employees, weight, k=1)[0]
                
                # Add shift to employee's schedule
                schedule_copy[employee].append((day, shift))
                shifts_copy[day][shifts.index(shift)] = employee
                
                # block overlapping shifts
                block_shifts(employee, shift, day,rest_copy)
                
                #update the weight of the employee
                weights_copy[employees.index(employee)] /= 100
            else:
                #add  the shift to the problematic shifts and rerun
                problematic_shifts.append(open_shift)
                break
    
    return schedule_copy, shifts_copy
    
    # # Print the schedule
    # if empty_slots:
    #     print("There are", len(empty_slots),"empty slots in the schedule:")
    #     [print(slot) for slot in empty_slots]
    #     # print("Employees schedule:")
    #     # [print(key,':',value) for key, value in schedule_copy.items()]
    #     print("\nWeek schedule:")
    #     [print(key,':',value) for key, value in shifts_copy.items()]
        
    # #export the schedule and shift lists
    # else:
    #     # Serializing jsons
    #     schedule_json = json.dumps(schedule_copy, indent=4)
    #     shifts_json = json.dumps(shifts_copy, indent=4)
    
    #     # Writing to schedule.json
    #     with open("Schedule.json", "w") as outfile:
    #         outfile.write(schedule_json)        
    #     with open("Shifts.json", "w") as outfile:
    #         outfile.write(shifts_json)   


def is_valid_path(filepath):
    if filepath and Path(filepath).exists():
        return True
    sg.popup_error("The file path is not valid")
    return False

empolyees_shifts = []
weekly_schedule = []

def popup_schedule(restriction_file):
    empolyees_shifts, weekly_schedule = build_schedule(restriction_file)
    schedule_layout = [[sg.VPush()],
                       [sg.Text("Week Schedule", size=(50, 1),text_color = 'Light Grey', font=("Helvetica", 40),justification='center')],
                       [sg.Table(values=list(zip(*weekly_schedule.values())),
                        headings=list(weekly_schedule.keys()),
                        auto_size_columns=False,
                        # col_widths = col_widths,
                        justification = 'center',
                        key='-TABLE-',
                        hide_vertical_scroll=True)],
                       [sg.VPush()],
                       [sg.Text("Employees Shifts", size=(50, 1),text_color = 'Light Grey', font=("Helvetica", 40),justification='center')],
                       [sg.Table(values=list(zip(*empolyees_shifts.values())),
                        headings=list(empolyees_shifts.keys()),
                        auto_size_columns=False,
                        # col_widths = col_widths,
                        justification = 'center',
                        key='-TABLE-',
                        hide_vertical_scroll=True)],
                       [sg.VPush()],
              [sg.Push(),sg.Button("Save Schedule", button_color="green"), sg.Button('Exit')]]
    
    window = sg.Window('Schedule', schedule_layout,resizable=True, font=("Helvetica", 20))
    
    # Create an event loop
    while True:
        event, values = window.read()
        # End program if user closes window or press Exit
        if event in (sg.WINDOW_CLOSED, "Exit"):
            break
               
        #export the schedule and shift list
        if event == "Save Schedule":
            if event in (sg.WINDOW_CLOSED, "Exit"):
                break
            # Serializing jsons
            schedule_json = json.dumps(weekly_schedule, indent=4)
            shifts_json = json.dumps(empolyees_shifts, indent=4)

            out_layout = [[sg.T("Output Directory:",  font=("Helvetica", 20), justification="r"), 
                          sg.I(key="Save_Dir", font=("Helvetica", 15)), sg.FolderBrowse() ],
                          [sg.Push(),sg.Button("Confirm", button_color="green"), sg.Button('Exit')]]
            new_wind = sg.Window('Save', out_layout,resizable=True, font=("Helvetica", 20))
            
            # Create an event loop
            while True:
                event, values = new_wind.read()
                
                if event in (sg.WINDOW_CLOSED, "Exit"):
                    break
            
                if event == "Confirm":
                    if is_valid_path(values["Save_Dir"]):
                        # Writing to schedule.json
                        with open(f'{values["Save_Dir"]}/Schedule.json', "w") as outfile:
                            outfile.write(schedule_json)        
                        with open(f'{values["Save_Dir"]}/Shifts.json', "w") as outfile:
                            outfile.write(shifts_json)   
            new_wind.close()
    window.close()


def build_window():
    sg.theme('Dark Blue 12')
    layout = [[sg.VPush()],
              [sg.Text("NOC Shift Scheduler", size=(50, 1),text_color = 'Light Grey', font=("Helvetica", 40),justification='center')],
              [sg.VPush()],
              [sg.Text('1. Upload restrictions JSON file', size=(25, 1), font=("Helvetica", 20),justification='center'),sg.Button("Example", font=("Helvetica", 15))], 
              [sg.Text('2. Build a schedule and export it', size=(25, 1), font=("Helvetica", 20),justification='center')],
              [sg.T("Restrictions File:",  font=("Helvetica", 20), justification="r"), sg.I(key="-Restrictions-", font=("Helvetica", 15)), sg.FileBrowse(file_types=(("JSON Files", "*.json*"),), font=("Helvetica", 15))],
              [sg.Button("Build Schedule", button_color="green", font=("Helvetica", 15)), sg.Exit(s=16, button_color="tomato", font=("Helvetica", 15))],
              [sg.VPush()]]
    
    # Create the window
    window = sg.Window("NOC Shift Scheduler", layout,size=(1080, 720),element_justification='c')
    
    # Create an event loop
    while True:
        event, values = window.read()
        # End program if user closes window or press Exit
        if event in (sg.WINDOW_CLOSED, "Exit"):
            break
        
        if event == "Example":
            example_layout = [[sg.Text('{\n\t"Natan": [')],[sg.Text('\t\t"Friday Evening",')],[sg.Text('\t\t"Friday Night"\n\t],')],
                              [sg.Text('\t"Lyr": [')],[sg.Text('\t\t"Saturday Morning",')],[sg.Text('\t\t"Saturday Evening"\n\t],\n}')]]
            sg.Window("EXAMPLE",example_layout,modal=True).read(close=True)
        
        if event == "Build Schedule":
           if is_valid_path(values["-Restrictions-"]):
               window.disappear()
               popup_schedule(values["-Restrictions-"])
               window.reappear()
               
        if event == "Save Schedule":
            print("saving")
            #export the schedule and shift lists
            # Serializing jsons
            schedule_json = json.dumps(weekly_schedule, indent=4)
            shifts_json = json.dumps(empolyees_shifts, indent=4)
            
            out_layout = [[sg.T("Output Directory:",  font=("Helvetica", 20), justification="r"), 
                          sg.I(key="Save_Dir", font=("Helvetica", 15)), sg.FolderBrowse() ],
                          [sg.Button("Download", button_color="green", font=("Helvetica", 15))]]
            sg.Window('Save', out_layout,resizable=True, font=("Helvetica", 20)).read(close=True)
        
        if event == "Download":
            if is_valid_path(values["Save_Dir"]):
                # Writing to schedule.json
                with open(f'{values["Save_Dir"]}/Schedule.json', "w") as outfile:
                    outfile.write(schedule_json)        
                with open(f'{values["Save_Dir"]}/Shifts.json', "w") as outfile:
                    outfile.write(shifts_json)   

            
    
    window.close()

if __name__ == '__main__':
    build_window()
    
    
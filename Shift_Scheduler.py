#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Dec  8 20:16:05 2022

@author: ayalo
"""
import os, random, copy, json
from optparse import OptionParser
import pandas as pd
from collections import Counter

parser = OptionParser()
parser.add_option("-b", "--build",
                  dest = "restrictions",
                  help = "Build a schedule from an Resriction input file",
                  metavar = "restrictions")

# List of employees
# employees = ["Natan", "Lyr", "Yotam", "Fares", "Mohammad", "Kostya", "Diogo", "Tiago"]

# List of shifts
shifts = ["Morning", "Evening", "Night"]

# List of days
days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]



#detailed shift list
open_shifts = []
for day in days:
    for shift in shifts:
        open_shifts.append(day+" "+shift)
        
#Script start
(options, args) = parser.parse_args()

#Save new Restrictions.json file
if(options.restrictions):
    # Serializing json
    new_json = json.dumps(options.restrictions, indent=4)
    # Writing to Restrictions.json
    with open("Restrictions.json", "w") as outfile:
        outfile.write(new_json)  
        
        
# Load Dictionary of restrictions
restrictions = json.load(open("Restrictions.json"))

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

while(not available_employees):
    #copy the initial start for this attempt
    rest_copy = copy.deepcopy(restrictions)
    schedule_copy = copy.deepcopy(schedule)
    shifts_copy = copy.deepcopy(shift_array)
    open_shifts_copy = copy.deepcopy(open_shifts)
    weights_copy = copy.deepcopy(weights)
    failed = False
    
    #first try to find solution for the problematic shifts
    for problematic_shift in problematic_shifts:
        day = problematic_shift.split(" ")[0]
        shift = problematic_shift.split(" ")[1]
        open_shifts_copy.remove(problematic_shift)
        available_employees = [employee for employee in employees if problematic_shift not in rest_copy[employee]]
        
        if not available_employees:
            # print("Error, there is no employee available for {0} {1} shift".format(day,shift))
            failed = True
            break
        #add employee to this shift
        weight = [weights_copy[employees.index(employee)] for employee in available_employees]
        employee = random.choices(available_employees, weight, k=1)[0]
        # Add shift to employee's schedule
        schedule_copy[employee].append((day, shift))
        # block overlapping shifts
        block_shifts(employee, shift, day,rest_copy)
        shifts_copy[day][shifts.index(shift)] = employee
        weights_copy[employees.index(employee)] /= 100
        # print("problematic",employee, problematic_shift)
    
    if(failed):
        continue
        
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
            # block overlapping shifts
            block_shifts(employee, shift, day,rest_copy)
            shifts_copy[day][shifts.index(shift)] = employee
            weights_copy[employees.index(employee)] /= 100
            # print(employee, open_shift)
        else:
            #add employee to this shift and rerun withiut this shift in possible shifts
            # print("Adding",open_shift,"to Problematic shifts")
            problematic_shifts.append(open_shift)
            break

# Serializing jsons
schedule_json = json.dumps(schedule_copy, indent=4)
shifts_json = json.dumps(shifts_copy, indent=4)

# Writing to schedule.json
with open("Schedule.json", "w") as outfile:
    outfile.write(schedule_json)        
with open("Shifts.json", "w") as outfile:
    outfile.write(shifts_json)   

# Print the schedule
print("Employees schedule:")
[print(key,':',value) for key, value in schedule_copy.items()]
print("\nWeek schedule:")
[print(key,':',value) for key, value in shifts_copy.items()]
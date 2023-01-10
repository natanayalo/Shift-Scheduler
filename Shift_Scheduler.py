# -*- coding: utf-8 -*-
"""
Created on Tue Jan 10 19:38:08 2023

@author: natan
"""

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Dec  8 20:16:05 2022

@author: ayalo
"""
import random, copy, json
from collections import Counter
from tabulate import tabulate
from itertools import zip_longest

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

if __name__ == '__main__':
    # Load Dictionary of restrictions
    restriction_file = "Restrictions.json"
    
    #Print result
    empolyees_shifts, weekly_schedule = build_schedule(restriction_file)
    print("Week Schedule:")
    print (tabulate(list(zip(*weekly_schedule.values())), list(weekly_schedule.keys()), tablefmt="mixed_outline"))
    print("Employees Shifts:")
    joined_values = list(zip_longest(*[[i[0]+' '+i[1] for i in sub] for sub in list(empolyees_shifts.values())]))
    print (tabulate(joined_values , list(empolyees_shifts.keys()), tablefmt="mixed_outline"))
    
    #Export result to jsons
    
    # Serializing jsons
    schedule_json = json.dumps(weekly_schedule, indent=4)
    shifts_json = json.dumps(empolyees_shifts, indent=4)
    
    # Writing to schedule.json
    with open("Schedule.json", "w") as outfile:
        outfile.write(schedule_json)        
    with open("Shifts.json", "w") as outfile:
        outfile.write(shifts_json)   

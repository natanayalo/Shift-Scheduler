# Shift-Scheduler
This is a script for generating a schedule for employees based on shift availability and restrictions. It does this by first parsing command line arguments to potentially save a new "Restrictions" file which contains an updated list of shifts that each employee is unavailable for. It then loads this "Restrictions" file and creates a list of all employees, as well as a list of all shifts for each day.

Next, the code identifies any shifts that have more restrictions than there are employees available to work them, and attempts to assign employees to these "problematic" shifts first. If there are no employees available for a shift, the script marks this attempt as a failure and exit. If there are available employees, it assigns one to the shift using a weighted random selection based on how many shifts each employee has already been assigned.

The code then continues on to assign all remaining shifts, again using a weighted random selection to choose which employee gets assigned to each shift. When all shifts have been assigned, the script checks to ensure that no employee has been assigned to more than 3 shifts in a row.

Once a valid schedule has been generated, the code export it in JSON files and prints it to the console.

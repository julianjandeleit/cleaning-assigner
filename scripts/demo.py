# %%
#%load_ext autoreload
#%autoreload 2
from cleaning_assigner import *
# %%
# Example usage
Z = [[0, 1], [2, 3], [ 4, 5]]
W = [[0, 1], [2, 3], [4, 5]]
S = list(range(0, 6))

# Read data from Excel
X, X_timetable = read_advanced_timetables("../ressources/cleaners.xlsx")

# Example usage of optimization
M_results = optimize_cleaning_assignment(Z, W, S,num_solutions=8)
len(M_results)
# %%
# Extract assigned tuples
for M in M_results:
    assigned_tuples = extract_assigned_tuples (M)
    print("Assigned Tuples:", assigned_tuples)
# %%

cleaners, c_timetable = read_advanced_timetables("../ressources/cleaners.xlsx")
appartments, a_timetable = read_advanced_timetables("../ressources/appartments.xlsx")

# %%
time_slots = find_unique_tuples_between_lists([cleaners.values(),appartments.values()])
S = list(range(len(time_slots)))
# %%
Z = convert_to_index_representation(cleaners.values(), time_slots)
W = convert_to_index_representation(appartments.values(), time_slots)
# %%
Z, W, S
M_results = optimize_cleaning_assignment(Z, W, S,num_solutions=1)
len(M_results)
# %%
# Extract assigned tuples
for M in M_results:
    assigned_tuples = extract_assigned_tuples (M)
    print("Assigned Tuples:", assigned_tuples)
    names = convert_assigned_tuples_to_names(assigned_tuples, cleaners, appartments, time_slots)
    print(names)
# %%
all_cleaner_timetables = generate_cleaner_timetables(convert_assigned_tuples_to_names(assigned_tuples, cleaners, appartments, time_slots), c_timetable)
# %%

    
write_cleaner_timetables_to_excel(all_cleaner_timetables, '../ressources/assignments.xlsx')
# %%

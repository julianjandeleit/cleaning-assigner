# %%
from cleaning_assigner import pipeline, extract_assigned_tuples

M_results, assignments, c_times, a_times = pipeline("../ressources/cleaners.xlsx", "../ressources/appartments.xlsx", 10)

# %%
# Extract assigned tuples
for a in assignments:
    print("Assigned Tuples:", a)

# %%

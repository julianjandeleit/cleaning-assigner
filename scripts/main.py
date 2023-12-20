# %%
from cleaning_assigner import pipeline

assignments, c_times, a_times = pipeline("../ressources/cleaners.xlsx", "../ressources/appartments.xlsx", 10)
# %%

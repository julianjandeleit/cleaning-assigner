import pandas as pd
def read_advanced_timetables(file_path):
    # Open Excel file
    xls = pd.ExcelFile(file_path)

    # Initialize dictionary X_dict
    X_dict = {}

    # Initialize dictionary for all present timeslots
    all_timeslots_dict = {}

    # Loop through sheets
    for sheet_name in xls.sheet_names:
        # Extract data from the sheet
        df = xls.parse(sheet_name)
        
        # Initialize list for the current sheet
        x_list = []

        # Loop through rows (time slots)
        for row in range(df.shape[0]):
            # Loop through columns (days of the week or date)
            for col in range(1, df.shape[1]):
                if not pd.isnull(df.iloc[row, col]) and df.iloc[row, col] == "X":
                    # If the cell is highlighted, add the content of the row and column names to the list
                    x_list.append((str(df.iloc[row, 0]), str(df.columns[col])))

        # Store the timeslots for the current sheet as a DataFrame in the dictionary
        all_timeslots_dict[sheet_name] = pd.DataFrame(x_list, columns=['Time Slot', 'Day'])

        # Use pd.Categorical to preserve the order of the original columns
        all_timeslots_dict[sheet_name]['Day'] = pd.Categorical(all_timeslots_dict[sheet_name]['Day'], categories=df.columns[1:])

        all_timeslots_dict[sheet_name] = all_timeslots_dict[sheet_name].pivot(index='Time Slot', columns='Day', values='Time Slot')

        X_dict[sheet_name] = sorted(x_list)

    return X_dict, all_timeslots_dict

def find_unique_tuples_between_lists(X_list):
    # Combine all sets from the list of sets
    slots = set()
    for X in X_list:
        for key in X:
            for tup in key:
                slots.add(tup)

    # Flatten the tuples and ensure uniqueness
    flattened_result = sorted(list(set(slots)))

    return flattened_result

def convert_to_index_representation(X, slots):
    S = slots
    # Create a mapping from elements in S to their indices
    index_mapping = {element: index for index, element in enumerate(S)}

    # Convert tuples in X to their index representation
    X_indices = [[index_mapping[tuple(element)] for element in sublist] for sublist in X]

    return X_indices

def convert_assigned_tuples_to_names(assigned_tuples, cleaners, apartments, time_slots):
    name_assigned_tuples = []

    for (i, j, s) in assigned_tuples:
        cleaner_name = list(cleaners.keys())[i]
        apartment_name = list(apartments.keys())[j]
        time_slot_name = time_slots[s]

        name_assigned_tuples.append((cleaner_name, apartment_name, time_slot_name))

    return name_assigned_tuples

def generate_cleaner_timetables(assigned_tuples, all_timeslots_dict):
    # Initialize dictionary for cleaner timetables
    cleaner_timetables = {k: v.copy().applymap(lambda x: None) for k, v in all_timeslots_dict.items()}

    # Loop through assigned_tuples
    for assignment in assigned_tuples:
        cleaner_name, apartment_name, time_slot = assignment
        cleaner_timetables[cleaner_name][time_slot[1]][time_slot[0]] = apartment_name

    return cleaner_timetables

def generate_appartment_timetables(assigned_tuples, all_timeslots_dict):
    # Initialize dictionary for cleaner timetables
    cleaner_timetables = {k: v.copy().applymap(lambda x: None) for k, v in all_timeslots_dict.items()}

    # Loop through assigned_tuples
    for assignment in assigned_tuples:
        cleaner_name, apartment_name, time_slot = assignment
        cleaner_timetables[apartment_name][time_slot[1]][time_slot[0]] = cleaner_name

    return cleaner_timetables

def write_cleaner_timetables_to_excel(all_cleaner_timetables, output_file):
    # Create an Excel writer
    with pd.ExcelWriter(output_file, engine='xlsxwriter') as writer:
        # Loop through cleaner timetables
        for cleaner_name, timetable_df in all_cleaner_timetables.items():
            # Write each cleaner's timetable to a separate sheet
            timetable_df.to_excel(writer, sheet_name=cleaner_name, index=True)

    print(f"Cleaner timetables written to {output_file}")
    
def pipeline(input_path_cleaners, input_path_apartments, num_solutions=1):
    from cleaning_assigner.optimizer import optimize_cleaning_assignment, extract_assigned_tuples
    
    cleaners, c_timetable = read_advanced_timetables(input_path_cleaners)
    appartments, a_timetable = read_advanced_timetables(input_path_apartments)

    time_slots = find_unique_tuples_between_lists([cleaners.values(),appartments.values()])
    S = list(range(len(time_slots)))
    Z = convert_to_index_representation(cleaners.values(), time_slots)
    W = convert_to_index_representation(appartments.values(), time_slots)

    M_results = optimize_cleaning_assignment(Z, W, S,num_solutions=num_solutions)

    # Extract assigned tuples
    assignments = [convert_assigned_tuples_to_names(extract_assigned_tuples(M), cleaners, appartments, time_slots) for M in M_results]
    
    cleaner_timetable = [generate_cleaner_timetables(a, c_timetable) for a in assignments]
    apartment_timetable = [generate_appartment_timetables(a, a_timetable) for a in assignments]
    return assignments, cleaner_timetable, apartment_timetable 

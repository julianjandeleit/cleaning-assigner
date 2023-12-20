# %%
from pulp import LpProblem, LpVariable, lpSum, LpMinimize, LpStatus
import numpy as np

def extract_assigned_tuples(M_result):
    assigned_tuples = []

    # Iterate over the indices of the non-zero elements in the 3D NumPy array
    for indices in np.argwhere(M_result):
        i, j, s = indices
        assigned_tuples.append((i, j, s))

    return assigned_tuples

def optimize_cleaning_assignment(Z, W, S, num_solutions=1):
    all_solutions = []

    for current_solution_index in range(num_solutions):
        # Create a linear programming problem
        prob = LpProblem(name=f"cleaning_assignment_{current_solution_index + 1}", sense=LpMinimize)

        # Define variables
        cleaners = range(len(Z))
        apartments = range(len(W))
        time_slots = S

        M = LpVariable.dicts("M", (cleaners, apartments, time_slots), cat="Binary")
        max_assignments = LpVariable("max_assignments", lowBound=0, cat="Integer")

        # Objective function: minimize the maximum number of assignments among cleaners
        prob += max_assignments, "MaxAssignments"

        # Constraints: Cleaners can only be assigned when they are available
        for i in cleaners:
            for s in time_slots:
                if s not in Z[i]:
                    prob += lpSum(M[i][j][s] for j in apartments) == 0, f"CleanerAvailability_{i}_{s}"

        # Constraints: Apartments should only be cleaned when available
        for j in apartments:
            for s in time_slots:
                if s not in W[j]:
                    prob += lpSum(M[i][j][s] for i in cleaners) == 0, f"ApartmentAvailability_{j}_{s}"

        # Constraints: Every apartment should be cleaned at least once
        for j in apartments:
            prob += lpSum(M[i][j][s] for i in cleaners for s in time_slots) >= 1, f"AtLeastOnceCleaning_{j}"

        # Constraint: max_assignments should be greater than or equal to each cleaner's total assignments
        for i in cleaners:
            prob += max_assignments >= lpSum(M[i][j][s] for j in apartments for s in time_slots), f"MaxAssignmentsConstraint_{i}"

        if all_solutions:
            for prev_solution_index, prev_solution in enumerate(all_solutions):
                # Create a set of cleaner and apartment pairs in the previous solution
                excluded_pairs = set(extract_assigned_tuples(prev_solution))
                print(f"excluding {excluded_pairs}")
                # Exclude the entire combination of cleaner and apartment assignments
                prob += lpSum(M[i][j][s] for i, j, s in excluded_pairs) <= 2, f"ExcludePreviousSolution_{prev_solution_index}_{i}_{j}"

        # Solve the problem
        prob.solve()

        # Check if the optimization was successful
        if LpStatus[prob.status] == 'Optimal':
            # Store the current solution
            current_solution = [[[int(M[i][j][s].value()) for i in cleaners] for j in apartments] for s in time_slots]
            current_solution = np.array(current_solution)
            current_solution = np.transpose(current_solution, (2, 1, 0))
            print(current_solution.shape)
            all_solutions.append(current_solution)
        else:
            print(f"Optimization for solution {current_solution_index + 1} failed. No feasible solution found.")
            break

    return all_solutions
# %%

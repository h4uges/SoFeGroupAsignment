import pulp

import Parser
import Constraints
import Validators
import Reporting
from VariableRepository import VariableRepository

person_file = 'persons.csv'

persons = Parser.parse_persons(person_file)
print(f"Parsed {len(persons)} persons.")

Validators.validate_wishes_age_feasibility(persons)

"""
# STEP 1: Feasibility Check
repo = VariableRepository()
feasibility_problem = pulp.LpProblem("GroupAssignmentFeasibility", pulp.LpMinimize)
Constraints.constraint_person_in_exactly_one_group(repo, feasibility_problem, persons)
Constraints.constraint_group_size_limits(repo, feasibility_problem, persons)
Constraints.constraint_max_age_difference(repo, feasibility_problem, persons)
Constraints.constraint_gender_rule(repo, feasibility_problem, persons)
Constraints.constraint_friend_wish(repo, feasibility_problem, persons)

feasibility_problem += 0

print("🔍 Checking feasibility...")
feasibility_problem.solve()

if pulp.LpStatus[feasibility_problem.status] != "Optimal":
    print("No feasible solution exists. Please check your constraints or input data.")
else:
    print("Feasible solution exists. Proceeding to optimization...")
"""
# STEP 2: Optimization
repo = VariableRepository()
group_assignment_problem = pulp.LpProblem("GroupAssignmentOptimization", pulp.LpMaximize)
Constraints.constraint_person_in_exactly_one_group(repo, group_assignment_problem, persons)
Constraints.constraint_group_size_limits(repo, group_assignment_problem, persons)
Constraints.constraint_max_age_difference_sat_like(repo, group_assignment_problem, persons)
Constraints.constraint_gender_rule_sat_like_aux(repo, group_assignment_problem, persons)
Constraints.constraint_friend_wish_sat_like(repo, group_assignment_problem, persons)
Constraints.add_objective_maximize_friend_wishes(repo, group_assignment_problem, persons)

solver = pulp.PULP_CBC_CMD(threads=4, gapAbs=12)
group_assignment_problem.solve(solver)

Reporting.analyze_solution(repo, persons, group_assignment_problem)
Reporting.export_group_assignments_to_csv(repo, group_assignment_problem, persons, "assignment_solution.csv")
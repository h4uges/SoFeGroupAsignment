from pulp import LpVariable, LpBinary

import Constants

class VariableRepository:
    def __init__(self):
        self.variables = {}

    def get_variable(self, person_id: int, group_index: int):
        if not (0 <= group_index < Constants.number_of_groups):
            raise ValueError(f"Ungültiger Gruppenindex: {group_index}")

        key = (person_id, group_index)
        if key not in self.variables:
            var_name = f"x_{person_id}_{group_index}"
            self.variables[key] = LpVariable(var_name, cat=LpBinary)
        
        return self.variables[key]
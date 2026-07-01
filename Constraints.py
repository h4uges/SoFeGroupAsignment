from pulp import LpVariable, LpMaximize, LpProblem, lpSum, LpBinary

from VariableRepository import VariableRepository
from Person import Person, Gender
import Constants

def constraint_person_in_exactly_one_group(repo: VariableRepository, problem: LpProblem, persons: list[Person]):
    for person in persons:
        vars_for_person = [repo.get_variable(person.id, g) for g in range(Constants.number_of_groups)]
        problem += (sum(vars_for_person) == 1, f"person_{person.id}_in_exactly_one_group")

def constraint_group_size_limits(repo: VariableRepository, problem, persons: list):
    for group in range(Constants.number_of_groups):
        person_in_group = [repo.get_variable(p.id, group) for p in persons]
        problem += (
            sum(person_in_group) >= Constants.min_group_size,
            f"group_{group}_min_size"
        )
        problem += (
            sum(person_in_group) <= Constants.max_group_size,
            f"group_{group}_max_size"
        )

def constraint_max_age_difference(repo: VariableRepository, problem: LpProblem, persons: list[Person]):
    for group in range(Constants.number_of_groups):
        
        min_age_of_group = LpVariable(f"min_age_group_{group}", lowBound=0)
        max_age_of_group = LpVariable(f"max_age_group_{group}", lowBound=0)

        for person in persons:
            age = person.age
            person_in_group = repo.get_variable(person.id, group)
            
            problem += min_age_of_group <= age + (1 - person_in_group) * 1000, f"group_{group}_min_age_person_{person.id}"
            problem += max_age_of_group >= age - (1 - person_in_group) * 1000, f"group_{group}_max_age_person_{person.id}"

        problem += max_age_of_group - min_age_of_group <= Constants.max_age_difference, f"group_{group}_max_age_diff"

def constraint_max_age_difference_sat_like(repo: VariableRepository, problem: LpProblem, persons: list[Person]):
    max_diff = Constants.max_age_difference
    
    for group in range(Constants.number_of_groups):
        for i, person1 in enumerate(persons):
            for j, person2 in enumerate(persons):
                
                if j <= i:
                    continue
                
                age_diff = abs(person1.age - person2.age)
                
                if age_diff > max_diff:
                    var1 = repo.get_variable(person1.id, group)
                    var2 = repo.get_variable(person2.id, group)
                    
                    problem += var1 + var2 <= 1, f"age_diff_conflict_{person1.id}_{person2.id}_group_{group}"

def constraint_gender_rule(repo: VariableRepository, problem: LpProblem, persons: list[Person]):
    for group in range(Constants.number_of_groups):
        male_vars = []
        female_vars = []

        for person in persons:
            person_in_group = repo.get_variable(person.id, group)
            if person.gender == Gender.MALE:
                male_vars.append(person_in_group)
            elif person.gender == Gender.FEMALE:
                female_vars.append(person_in_group)
            else:
                raise ValueError(f"Invalid Gender of Person {person.id}: {person.gender}")

        num_male_in_group = sum(male_vars)
        num_female_in_group = sum(female_vars)

        is_all_male_in_group = LpVariable(f"group_{group}_all_male", cat="Binary")
        is_all_female_in_group = LpVariable(f"group_{group}_all_female", cat="Binary")
        
        big_M = len(persons)

        problem += num_female_in_group <= big_M * (1 - is_all_male_in_group), f"group_{group}_all_male_def"
        problem += num_male_in_group <= big_M * (1 - is_all_female_in_group), f"group_{group}_all_female_def"

        problem += (
            is_all_male_in_group +
            (num_male_in_group >= Constants.n_min_same_gender)
        ) >= 1, f"group_{group}_gender_rule_male"

        problem += (
            is_all_female_in_group +
            (num_female_in_group >= Constants.n_min_same_gender)
        ) >= 1, f"group_{group}_gender_rule_female"
    
def constraint_gender_rule_sat_like_aux(repo: VariableRepository, problem: LpProblem, persons: list[Person]):    
    for group in range(Constants.number_of_groups):
        
        for gender in [Gender.MALE, Gender.FEMALE]:  # Adjust based on your dataset
            persons_of_gender = [p for p in persons if p.gender == gender]
            
            if not persons_of_gender:
                print("DEBUG_SKIP")
                continue  # Skip if no persons of this gender
            
            # Binary variable indicating if group contains at least one person of this gender
            has_gender_in_group = LpVariable(f"has_{gender}_in_group_{group}", cat='Binary')
            
            # Sum of persons of this gender in the group
            sum_gender_in_group = lpSum([repo.get_variable(p.id, group) for p in persons_of_gender])
            
            # Link person assignments to has_gender_in_group
            for person in persons_of_gender:
                person_in_group = repo.get_variable(person.id, group)
                problem += person_in_group <= has_gender_in_group, f"link_{gender}_person_{person.id}_group_{group}"
            
            # Enforce minimum count if group contains at least one person of this gender
            problem += sum_gender_in_group >= Constants.n_min_same_gender * has_gender_in_group, f"min_count_{gender}_group_{group}"

def constraint_friend_wish(repo: VariableRepository, problem: LpProblem, persons: list[Person]):
    name_to_id = {f"{p.first_name} {p.last_name}": p.id for p in persons}

    for person in persons:
        
        wishes = []
        for wish_name in [person.wish_1, person.wish_2]:
            if wish_name and wish_name in name_to_id:
                wishes.append(name_to_id[wish_name])
        
        if not wishes:
            continue

        for group_id in range(Constants.number_of_groups):
            person_in_group = repo.get_variable(person.id, group_id)
            friends_in_group = sum(repo.get_variable(wish_id, group_id) for wish_id in wishes)
            
            problem += friends_in_group >= person_in_group, f"friend_wish_person_{person.id}_group_{group_id}"

def constraint_friend_wish_sat_like(repo: VariableRepository, problem: LpProblem, persons: list[Person]):
    # Full name lookup
    name_to_person = {
        f"{p.first_name.strip().lower()} {p.last_name.strip().lower()}": p
        for p in persons
    }

    for person in persons:
        wishes = []

        for wish in [person.wish_1, person.wish_2]:
            if not wish:
                continue

            wish_key = wish.strip().lower()
            if wish_key not in name_to_person:
                continue  # Wish refers to unknown person

            friend = name_to_person[wish_key]
            if friend.id == person.id:
                continue  # Skip self-wish

            wish_fulfilled_group_vars = []

            for group in range(Constants.number_of_groups):
                person_in_group = repo.get_variable(person.id, group)
                friend_in_group = repo.get_variable(friend.id, group)

                wish_fulfilled = LpVariable(f"wish_{person.id}_{friend.id}_group_{group}", cat="Binary")

                # Logical AND: wish_fulfilled is 1 only if both in group
                problem += wish_fulfilled <= person_in_group
                problem += wish_fulfilled <= friend_in_group
                problem += wish_fulfilled >= person_in_group + friend_in_group - 1

                wish_fulfilled_group_vars.append(wish_fulfilled)

            # Sum over groups, if they are together anywhere, wish is fulfilled
            wishes.append(lpSum(wish_fulfilled_group_vars))

        if wishes:
            # At least one valid wish must be fulfilled
            problem += lpSum(wishes) >= 1, f"at_least_one_wish_fulfilled_person_{person.id}"


def add_objective_maximize_friend_wishes(repo: VariableRepository, problem: LpProblem, persons: list[Person]):
    name_to_id = {f"{p.first_name} {p.last_name}": p.id for p in persons}

    wish_vars = []

    for person in persons:
        wishes = [person.wish_1, person.wish_2]

        for wish_name in wishes:
            if not wish_name or wish_name not in name_to_id:
                continue

            friend_id = name_to_id[wish_name]

            for group_id in range(Constants.number_of_groups):
                person_in_group = repo.get_variable(person.id, group_id)
                friend_in_group = repo.get_variable(friend_id, group_id)

                wish_var = LpVariable(f"wish_{person.id}_{friend_id}_{group_id}", cat=LpBinary)
                wish_vars.append(wish_var)

                # wish_var only active if both are in the same group
                problem += wish_var <= person_in_group, f"def_wish_var_{person.id}_with_{friend_id}_in_group_{group_id}_0"
                problem += wish_var <= friend_in_group, f"def_wish_var_{person.id}_with_{friend_id}_in_group_{group_id}_1"
                problem += wish_var >= person_in_group + friend_in_group - 1, f"def_wish_var_{person.id}_with_{friend_id}_in_group_{group_id}_2"

    problem += lpSum(wish_vars), f"maximize_fulfilled_wishes"

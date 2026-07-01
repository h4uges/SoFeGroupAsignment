from collections import defaultdict
from datetime import date
from pulp import LpStatus, value, LpProblem

import Constants
from VariableRepository import VariableRepository
from Person import Person, Gender

import csv

def analyze_solution(repo : VariableRepository, persons: list[Person], problem: LpProblem):
    """
    Holt Zuordnung aus PuLP-Modell und gibt umfassenden Report aus.
    """
    
    status_str = LpStatus[problem.status]
    if status_str not in ["Optimal", "Feasible"]:
        print("Achtung: Keine zulässige Lösung gefunden!")
        return

    # Zuordnungen bestimmen
    assignments = {}
    for person in persons:
        for group_id in range(Constants.number_of_groups):
            var = repo.get_variable(person.id, group_id)
            if value(var) == 1:
                assignments[person.id] = group_id
                break

    groups = defaultdict(list)
    person_by_id = {p.id: p for p in persons}
    
    for person_id, group_id in assignments.items():
        groups[group_id].append(person_by_id[person_id])

    print(f"\n{'='*20} Gruppenreport {'='*20}\n")
    
    # Gruppen-Statistik
    group_members_by_id = {}
    
    for group_id in range(Constants.number_of_groups):
        members = groups.get(group_id, [])
        num_members = len(members)
        num_male = sum(1 for p in members if p.gender == Gender.MALE)
        num_female = sum(1 for p in members if p.gender == Gender.FEMALE)
        
        if members:
            ages = [(date.today() - p.birth_date).days // 365 for p in members]
            max_age_diff = max(ages) - min(ages)
        else:
            max_age_diff = 0

        group_members_by_id[group_id] = set(p.id for p in members)

        print(f"Gruppe {group_id}:")
        print(f"  Mitglieder: {num_members}")
        print(f"  Davon männlich: {num_male}, weiblich: {num_female}")
        print(f"  Maximale Altersdifferenz: {max_age_diff} Jahre\n")
    
    # Wunsch-Erfüllung
    total_wishes = 0
    fulfilled_wishes = 0
    persons_with_wishes = 0
    persons_with_fulfilled_wish = 0

    all_names_to_ids = {f"{p.first_name} {p.last_name}": p.id for p in persons}
    
    for person in persons:
        wishes = [person.wish_1, person.wish_2]
        wishes = [w for w in wishes if w]  # Nur nicht-leere Wünsche
        
        if not wishes:
            continue

        persons_with_wishes += 1
        group_id = assignments.get(person.id)
        group_members = group_members_by_id.get(group_id, set())

        fulfilled = 0
        for wish_name in wishes:
            wished_id = all_names_to_ids.get(wish_name)
            if wished_id is not None:
                total_wishes += 1
                if wished_id in group_members:
                    fulfilled_wishes += 1
                    fulfilled += 1

        if fulfilled > 0:
            persons_with_fulfilled_wish += 1
        if fulfilled == 0:
            print(f"Wunsch von Person {person.first_name} {person.last_name} not fullfilled.")

    wish_ratio = (fulfilled_wishes / total_wishes * 100) if total_wishes > 0 else 0

    print(f"{'-'*50}")
    print(f"Wunsch-Erfüllung:")
    print(f"  Personen mit mindestens einem Wunsch: {persons_with_wishes}")
    print(f"  Davon mindestens ein Wunsch erfüllt: {persons_with_fulfilled_wish} ({persons_with_fulfilled_wish / persons_with_wishes * 100:.1f}%)")
    print(f"  Gesamtzahl Wünsche: {total_wishes}")
    print(f"  Davon erfüllt: {fulfilled_wishes} ({wish_ratio:.1f}%)")
    print(f"{'-'*50}\n")


def export_group_assignments_to_csv(repo: VariableRepository, problem: LpProblem, persons: list[Person], output_path: str):
    assignments = []

    for person in persons:
        assigned_group = None
        for group_id in range(Constants.number_of_groups):
            var = repo.get_variable(person.id, group_id)
            if var.varValue and var.varValue > 0.5:
                assigned_group = group_id
                break

        if assigned_group is None:
            print(f"Warning: No group assigned for person ID {person.id}")

        assignments.append((person.id, assigned_group))

    # Sort by person ID
    assignments.sort(key=lambda x: x[0])

    # Write to CSV
    with open(output_path, mode="w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["PersonID", "GroupNumber"])

        for person_id, group_number in assignments:
            writer.writerow([person_id, group_number])

    print(f"Group assignments written to {output_path}")
from pathlib import Path
import csv

class Voter:
    def __init__(self, id, sex=None, age=None, subunits=set()):
        self.id = id #unique id
        self.sex = sex
        self.age = age
        self.subunits = subunits

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, v):
        return self.id == v.id

    def __repr__(self):
        return f"v({self.id})"

class Candidate:
    def __init__(self, id, cost, name=None, subunit=None):
        self.id = id #unique id
        self.cost = cost
        self.name = name
        self.subunit = subunit #None for citywide projects

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, c):
        return self.id == c.id

    def __repr__(self):
        return f"c({self.id})"

class Election:
    def __init__(self, voters=set(), profile={}, budget=0, city = None, year = None, subunits = set()):
        self.voters = voters
        self.profile = profile #dict: candidates -> voters -> score
        self.budget = budget
        self.city = city
        self.year = year
        self.subunits = subunits

    def read_from_files(self, pattern): #assumes Pabulib data format
        for filename in Path(".").glob(pattern):
            cand_id_to_obj = {}
            with open(filename, 'r', newline='', encoding="utf-8") as csvfile:
                meta = {}
                section = ""
                header = []
                reader = csv.reader(csvfile, delimiter=';')
                subunit = None
                for i, row in enumerate(reader):
                    if str(row[0]).strip().lower() in ["meta", "projects", "votes"]:
                        section = str(row[0]).strip().lower()
                        header = next(reader)
                    elif section == "meta":
                        if row[0] == "subunit":
                            subunit = row[1].strip()
                            self.subunits.add(subunit)
                        if row[0] == "budget":
                            budget_str = row[1].strip()
                            if "," in budget_str:
                                self.budget += int(budget_str.split(",")[0]) + 1
                            else:
                                self.budget += int(budget_str)
                    elif section == "projects":
                        project = {}
                        for it, key in enumerate(header[1:]):
                            project[key.strip()] = row[it+1].strip()
                        c_id = row[0]
                        c = Candidate(c_id, int(project["cost"]), project["name"], subunit=subunit)
                        self.profile[c] = {}
                        cand_id_to_obj[c_id] = c
                    elif section == "votes":
                        vote = {}
                        for it, key in enumerate(header[1:]):
                            vote[key.strip()] = row[it+1].strip()
                        v_id = row[0]
                        v_age = vote.get("age", None)
                        v_sex = vote.get("sex", None)
                        v = Voter(v_id, v_sex, v_age)
                        self.voters.add(v)
                        v_vote = [cand_id_to_obj[c_id] for c_id in vote["vote"].split(",")]

                        for c in v_vote:
                            self.profile[c][v] = 1

        for c in set(c for c in self.profile):
            if len(self.profile[c]) == 0: #nobody voted for the project; usually means the project was withdrawn
                del self.profile[c]

        return self

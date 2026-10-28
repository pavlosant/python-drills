"""A deliberately messy module for the Day 14 refactoring drill.

Do NOT change what build_report returns - the tests describe the behaviour.
"""


def build_report(records):
    out = ""
    total = 0
    cancer = 0
    metabolic = 0
    respiratory = 0
    other = 0
    problems = []
    for r in records:
        total = total + 1
        if r["category"] == "cancer":
            cancer = cancer + 1
        elif r["category"] == "metabolic":
            metabolic = metabolic + 1
        elif r["category"] == "respiratory":
            respiratory = respiratory + 1
        else:
            other = other + 1
        if r["id"] is None or r["id"] == "":
            problems.append("record with no id")
        else:
            if not ":" in r["id"]:
                problems.append("bad id " + r["id"])
        if r["label"] is None or r["label"] == "":
            problems.append("no label for " + str(r["id"]))
        n = 0
        for s in r["synonyms"]:
            n = n + 1
        if n == 0:
            problems.append("no synonyms for " + str(r["id"]))
    out = out + "Total: " + str(total) + "\n"
    out = out + "Cancer: " + str(cancer) + "\n"
    out = out + "Metabolic: " + str(metabolic) + "\n"
    out = out + "Respiratory: " + str(respiratory) + "\n"
    out = out + "Other: " + str(other) + "\n"
    if len(problems) > 0:
        out = out + "Problems:\n"
        for p in problems:
            out = out + "- " + p + "\n"
    else:
        out = out + "No problems\n"
    return out

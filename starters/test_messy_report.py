from messy_report import build_report


def rec(id_, label, synonyms, category):
    return {"id": id_, "label": label, "synonyms": synonyms, "parents": [], "category": category}


def test_counts_and_no_problems():
    records = [
        rec("DIS:0003", "asthma", ["bronchial asthma"], "respiratory"),
        rec("DIS:0009", "cancer", ["neoplasm"], "cancer"),
        rec("DIS:0006", "diabetes mellitus", ["diabetes"], "metabolic"),
        rec("DIS:0014", "hypertension", ["HTN"], "cardiovascular"),
    ]
    assert build_report(records) == (
        "Total: 4\nCancer: 1\nMetabolic: 1\nRespiratory: 1\nOther: 1\nNo problems\n"
    )


def test_problems_are_listed_in_record_order():
    records = [
        rec("DIS0003", "asthma", ["bronchial asthma"], "respiratory"),  # bad id
        rec("DIS:0009", "", ["neoplasm"], "cancer"),  # no label
        rec("DIS:0011", "breast cancer", [], "cancer"),  # no synonyms
    ]
    assert build_report(records) == (
        "Total: 3\nCancer: 2\nMetabolic: 0\nRespiratory: 1\nOther: 0\n"
        "Problems:\n- bad id DIS0003\n- no label for DIS:0009\n- no synonyms for DIS:0011\n"
    )


def test_missing_ids_are_reported():
    records = [
        rec(None, "asthma", ["x"], "respiratory"),
        rec("", "cancer", ["y"], "cancer"),
    ]
    assert build_report(records).count("record with no id") == 2


def test_empty_input():
    assert build_report([]) == (
        "Total: 0\nCancer: 0\nMetabolic: 0\nRespiratory: 0\nOther: 0\nNo problems\n"
    )

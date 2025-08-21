def estimate_totals(estimate) -> dict:
    equip = sum((i.qty or 0)*(i.price_material or 0) for i in estimate.items)
    labor = sum((i.qty or 0)*(i.price_labor or 0) for i in estimate.items)
    return {"equipment": equip, "labor": labor, "total": equip + labor}

def proposal_totals(proposal) -> dict:
    equip = sum((i.qty or 0)*(i.price or 0) for i in proposal.items)
    labor = sum((i.qty or 0)*(i.price_labor or 0) for i in proposal.items)
    return {"equipment": equip, "labor": labor, "total": equip + labor}

def payment_schedule_100_70_30_from_totals(equip: float, labor: float) -> list[dict]:
    return [
        {"title": "100% оборудования и материалов", "amount": equip},
        {"title": "70% монтажных работ", "amount": labor*0.7},
        {"title": "30% монтажных работ", "amount": labor*0.3},
    ]

def payment_schedule_100_70_30(estimate) -> list[dict]:
    t = estimate_totals(estimate)
    return payment_schedule_100_70_30_from_totals(t["equipment"], t["labor"])

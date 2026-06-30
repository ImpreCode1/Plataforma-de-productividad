from decimal import Decimal


def calculate_kpi_results(
    achieved_value: Decimal,
    achieved_total: Decimal | None,
    target_value: Decimal | None,
    weight: Decimal | None,
    is_descending: bool = False
) -> dict:
    if achieved_total is not None and achieved_total > 0:
        achievement_percentage = (achieved_value / achieved_total) * 100
    elif target_value is not None and target_value > 0:
        achievement_percentage = (achieved_value / target_value) * 100
    else:
        achievement_percentage = Decimal(0)

    weighted_score = (achievement_percentage * (weight or Decimal(0))) / 100

    target_met = False
    if achieved_total is not None and achieved_total > 0:
        percentage = (achieved_value / achieved_total) * 100
        if target_value is not None:
            target_met = percentage <= target_value if is_descending else percentage >= target_value
        else:
            target_met = (achieved_value / achieved_total) <= 1 if is_descending else (achieved_value / achieved_total) >= 1
    elif target_value is not None:
        target_met = achieved_value <= target_value if is_descending else achieved_value >= target_value

    return {
        "achievement_percentage": round(achievement_percentage, 2),
        "weighted_score": round(weighted_score, 2),
        "target_met": target_met,
    }

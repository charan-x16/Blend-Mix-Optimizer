# core/cost.py

def calculate_total_cost(blend_df):
    """
    Calculates total ore cost per tHM
    """
    return (blend_df["opt_share"] * blend_df["cost_rs_per_thm"]).sum() / 100

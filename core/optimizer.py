from config import MANUAL_PENALTY_CAPS


def run_rule_based_optimizer(blend_policy_df, availability_caps=None):
    """
    Rule-based blend optimizer:
    - Respects availability
    - Protects CORE stability
    - Uses FLEX for cost control
    - Uses PENALTY only as fallback
    """

    opt_df = blend_policy_df.copy()

    # --------------------------------------------------
    # STEP 0: Controlled expansion for PENALTY ores
    # --------------------------------------------------
    for vendor, cap in MANUAL_PENALTY_CAPS.items():
        if vendor in opt_df.index:
            opt_df.loc[vendor, ["recommended_min", "recommended_target"]] = 0.0
            opt_df.loc[vendor, "recommended_max"] = cap
            opt_df.loc[vendor, "vendor_class"] = "PENALTY"

    # --------------------------------------------------
    # STEP 1: Apply availability caps (CRITICAL)
    # --------------------------------------------------
    if availability_caps:
        for vendor, cap in availability_caps.items():
            if vendor in opt_df.index:
                if cap <= 0:
                    # Vendor unavailable → fully disable
                    opt_df.loc[vendor, [
                        "recommended_min",
                        "recommended_target",
                        "recommended_max"
                    ]] = 0.0
                else:
                    # Vendor available → respect learned max
                    opt_df.loc[vendor, "recommended_max"] = min(
                        opt_df.loc[vendor, "recommended_max"],
                        cap
                    )

    # --------------------------------------------------
    # STEP 2: Initialize with minimum shares
    # --------------------------------------------------
    opt_df["opt_share"] = opt_df["recommended_min"].astype(float)

    remaining = 100.0 - opt_df["opt_share"].sum()

    if remaining < -1e-6:
        raise ValueError("Infeasible blend: minimum shares exceed 100%")

    # --------------------------------------------------
    # STEP 3: CORE stabilization (availability-aware)
    # --------------------------------------------------
    for vendor, row in opt_df[opt_df["vendor_class"] == "CORE"].iterrows():

        max_allowed = min(
            row["recommended_target"],
            row["recommended_max"]
        )

        add = min(
            max_allowed - opt_df.loc[vendor, "opt_share"],
            remaining
        )

        if add > 0:
            opt_df.loc[vendor, "opt_share"] += add
            remaining -= add

    # --------------------------------------------------
    # STEP 4: FLEX cost optimization
    # --------------------------------------------------
    flex_df = opt_df[opt_df["vendor_class"] == "FLEX"].sort_values(
        by="cost_rs_per_thm"
    )

    for vendor, row in flex_df.iterrows():

        add = min(
            row["recommended_max"] - opt_df.loc[vendor, "opt_share"],
            remaining
        )

        if add > 0:
            opt_df.loc[vendor, "opt_share"] += add
            remaining -= add

    # --------------------------------------------------
    # STEP 5: PENALTY fallback
    # --------------------------------------------------
    pen_df = opt_df[opt_df["vendor_class"] == "PENALTY"].sort_values(
        by="cost_rs_per_thm"
    )

    for vendor, row in pen_df.iterrows():

        add = min(
            row["recommended_max"] - opt_df.loc[vendor, "opt_share"],
            remaining
        )

        if add > 0:
            opt_df.loc[vendor, "opt_share"] += add
            remaining -= add

    # --------------------------------------------------
    # STEP 6: FINAL VALIDATION (FIXED ✅)
    # --------------------------------------------------
    total = opt_df["opt_share"].sum()

    if abs(total - 100.0) > 1e-6:
        err = AssertionError(
            f"Blend does not sum to 100%. Current sum = {total:.4f}"
        )
        err.partial_result = opt_df.copy()   # 🔑 THIS FIXES YOUR UI
        raise err

    return opt_df

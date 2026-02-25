# monitoring/compliance.py

def check_compliance(opt_df):
    """
    Returns compliance status per vendor
    """
    status = []

    for idx, row in opt_df.iterrows():
        if row["opt_share"] < row["recommended_min"]:
            status.append("RED")
        elif row["opt_share"] > row["recommended_max"]:
            status.append("RED")
        else:
            status.append("GREEN")

    opt_df["compliance"] = status
    return opt_df

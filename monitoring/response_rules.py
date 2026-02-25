# monitoring/response_rules.py

def generate_guidance(opt_df):
    msgs = []
    for v, r in opt_df.iterrows():
        if r["vendor_class"]=="CORE" and r["compliance"]=="RED":
            msgs.append(f"CORE vendor {v} violated limits – correct immediately.")
        if r["vendor_class"]=="PENALTY" and r["opt_share"]>0:
            msgs.append(f"PENALTY vendor {v} in use ({r['opt_share']}%). Monitor coke.")
    return msgs


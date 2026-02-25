import streamlit as st
import pandas as pd

from core.optimizer import run_rule_based_optimizer
from core.cost import calculate_total_cost
from monitoring.compliance import check_compliance
from monitoring.response_rules import generate_guidance
from visualization.charts import plot_recommended_blend


# PAGE SETUP
st.set_page_config(
    page_title="Blast Furnace Blend Mix Optimizer",
    layout="wide"
)

st.title("Blast Furnace Blend Mix Optimizer")


# LOAD FROZEN BLEND POLICY
blend_policy = pd.read_csv(
    "data/blend_policy.csv",
    index_col=0
)


# MAIN PAGE — OPERATOR INPUT (AVAILABILITY ONLY)
st.subheader("Select Available Ore Vendors")

availability_caps = {}
vendors = blend_policy.index.unique()

for i, vendor in enumerate(vendors):

    col1, col2 = st.columns([1, 2])

    with col1:
        available = st.checkbox(
            vendor,
            value=True,
            key=f"avail_{vendor}_{i}"
        )

    val = blend_policy.loc[vendor, "recommended_max"]
    max_allowed = float(val.iloc[0]) if isinstance(val, pd.Series) else float(val)

    availability_caps[vendor] = max_allowed if available else 0.0

    with col2:
        st.caption(f"Type: {blend_policy.loc[vendor, 'vendor_class']}")

st.markdown("---")


# SIDEBAR — SYSTEM EXPLANATION
st.sidebar.subheader("How the system treats ores")

st.sidebar.markdown("""
**CORE**
- Stability critical  
- Protected at proven operating levels  

**FLEX**
- Safely adjustable  
- Used for cost control  

**PENALTY**
- Risky / unstable  
- Used only if unavoidable  
""")

st.sidebar.markdown("---")

st.sidebar.markdown("""
**System Principles**
- Stability first  
- Cost second  
- Risk last  
- No black-box ML  
""")


# MAIN ACTION
if st.button("Run Blend Optimization"):

    infeasible = False
    display_df = None
    total_cost = None


    # RUN OPTIMIZER
    try:
        display_df = run_rule_based_optimizer(
            blend_policy,
            availability_caps=availability_caps
        )
    except AssertionError as e:
        infeasible = True

        if hasattr(e, "partial_result"):
            display_df = e.partial_result
        else:
            st.error("❌ Optimizer error: partial result missing.")
            st.stop()


    # STATUS MESSAGE
    if infeasible:
        st.error("❌ No feasible 100% blend can be formed with current availability.")
        st.markdown("**Below is the maximum safe achievable blend.**")
    else:
        st.success("✅ Optimal blend found within safe operating limits.")


    # POST-PROCESSING
    if not infeasible:
        display_df = check_compliance(display_df)
        total_cost = calculate_total_cost(display_df)

    achieved = display_df["opt_share"].sum()


    # RESULTS — ALWAYS SHOWN
    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader(
            "Recommended Blend (%)"
            if not infeasible
            else "Maximum Safe Achievable Blend (%)"
        )

        st.dataframe(
            display_df[
                [
                    "vendor_class",
                    "opt_share",
                    "recommended_min",
                    "recommended_max",
                ]
            ].round(2),
            use_container_width=True
        )

        if infeasible:
            st.warning(f"Only {achieved:.1f}% of burden could be filled safely.")
        else:
            st.metric(
                "Estimated Ore Cost (₹ / tHM)",
                round(total_cost, 2)
            )

    with col2:
        st.subheader(
            "Blend Mix"
            if not infeasible
            else "Blend Mix (Partial – Safety Limited)"
        )
        st.pyplot(plot_recommended_blend(display_df))


    # OPERATOR GUIDANCE
    st.subheader("Operator Guidance")

    if infeasible:
        st.warning(
            "Additional CORE or FLEX ores are required to reach 100% safely."
        )
    else:
        guidance_msgs = generate_guidance(display_df)

        if not guidance_msgs:
            st.success("Blend is within safe operating limits. No action required.")
        else:
            for msg in guidance_msgs:
                st.warning(msg)

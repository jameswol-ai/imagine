# modules/structural/eurocode.py
import streamlit as st
import pandas as pd

# Eurocode partial factors (EN 1990)
PARTIAL_FACTORS = {
    "ULS": {
        "G": {"unfavourable": 1.35, "favourable": 1.0},
        "Q": {"leading": 1.5, "accompanying": 1.5},
        "wind": 1.5,
        "snow": 1.5,
    },
    "SLS": {
        "G": 1.0,
        "Q": 1.0,
        "wind": 0.6,
        "snow": 0.5,
    }
}

# Material factors (EN 1992-1-1 / EN 1993-1-1)
MATERIAL_FACTORS = {
    "Concrete C30/37": {"gamma_c": 1.5, "alpha_cc": 0.85},
    "Steel S355": {"gamma_s": 1.15},
}

def compute_combinations(loads, material):
    """Compute ULS and SLS load combinations."""
    G = loads.get("G", 0.0)       # Permanent (dead)
    Q_leading = loads.get("Q_leading", 0.0)
    Q_acc = loads.get("Q_acc", 0.0)
    wind = loads.get("wind", 0.0)
    snow = loads.get("snow", 0.0)

    # ULS combinations (simplified, using EN 1990)
    uls_cases = []
    # Case 1: 1.35G + 1.5Q_leading + 1.5*ψ₀*Q_acc (we use ψ₀=0.7 for office)
    uls1 = 1.35 * G + 1.5 * Q_leading + 1.5 * 0.7 * Q_acc
    uls_cases.append(("ULS 1 (G + Q_lead + ψ₀Q_acc)", uls1))
    # Case 2: 1.35G + 1.5*wind + 1.5*ψ₀*Q_leading
    uls2 = 1.35 * G + 1.5 * wind + 1.5 * 0.7 * Q_leading
    uls_cases.append(("ULS 2 (G + wind + ψ₀Q_lead)", uls2))
    # Case 3: 1.35G + 1.5*snow + 1.5*ψ₀*Q_leading
    uls3 = 1.35 * G + 1.5 * snow + 1.5 * 0.7 * Q_leading
    uls_cases.append(("ULS 3 (G + snow + ψ₀Q_lead)", uls3))
    # Case 4: 1.0G + 1.5*Q_leading (favourable permanent)
    uls4 = 1.0 * G + 1.5 * Q_leading
    uls_cases.append(("ULS 4 (G_fav + Q_lead)", uls4))

    # Find governing (max) ULS
    uls_df = pd.DataFrame(uls_cases, columns=["Combination", "Value"])
    governing_uls = uls_df.loc[uls_df["Value"].idxmax()]

    # SLS combinations (serviceability)
    sls1 = 1.0 * G + 1.0 * Q_leading + 1.0 * 0.7 * Q_acc
    sls2 = 1.0 * G + 0.6 * wind + 0.7 * Q_leading
    sls3 = 1.0 * G + 0.5 * snow + 0.7 * Q_leading
    sls_df = pd.DataFrame([
        ("SLS 1 (G + Q_lead + ψ₀Q_acc)", sls1),
        ("SLS 2 (G + wind + ψ₀Q_lead)", sls2),
        ("SLS 3 (G + snow + ψ₀Q_lead)", sls3),
    ], columns=["Combination", "Value"])
    governing_sls = sls_df.loc[sls_df["Value"].idxmax()]

    # Material resistance (if concrete)
    if "Concrete" in material:
        f_ck = 30  # MPa for C30/37
        gamma_c = MATERIAL_FACTORS[material]["gamma_c"]
        alpha_cc = MATERIAL_FACTORS[material]["alpha_cc"]
        f_cd = (alpha_cc * f_ck) / gamma_c  # design compressive strength
        mat_resistance = f"f_cd = {f_cd:.1f} MPa"
    elif "Steel" in material:
        f_yk = 355  # MPa for S355
        gamma_s = MATERIAL_FACTORS[material]["gamma_s"]
        f_yd = f_yk / gamma_s
        mat_resistance = f"f_yd = {f_yd:.1f} MPa"
    else:
        mat_resistance = "Not available"

    return uls_df, governing_uls, sls_df, governing_sls, mat_resistance


def render():
    st.subheader("Eurocode Load Combination Calculator")
    st.markdown("**EN 1990 – Basis of structural design**")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Loads (characteristic values)**")
        G = st.number_input("Permanent load G (kN/m²)", value=5.0, step=0.5)
        Q_leading = st.number_input("Leading variable Q (kN/m²)", value=3.0, step=0.5)
        Q_acc = st.number_input("Accompanying variable (ψ₀Q) (kN/m²)", value=2.0, step=0.5)
        wind = st.number_input("Wind load (kN/m²)", value=0.8, step=0.1)
        snow = st.number_input("Snow load (kN/m²)", value=0.5, step=0.1)

    with col2:
        st.markdown("**Material**")
        material = st.selectbox("Select material", ["Concrete C30/37", "Steel S355"])
        st.markdown("**Combination factors**")
        st.caption("ψ₀ = 0.7 (office / residential)")

    if st.button("Calculate Load Combinations"):
        loads = {"G": G, "Q_leading": Q_leading, "Q_acc": Q_acc, "wind": wind, "snow": snow}
        uls_df, gov_uls, sls_df, gov_sls, mat_res = compute_combinations(loads, material)

        st.success("Calculation complete!")

        # Display results
        st.subheader("Ultimate Limit State (ULS)")
        st.dataframe(uls_df, use_container_width=True)
        st.metric("Governing ULS", f"{gov_uls['Combination']}", f"{gov_uls['Value']:.2f} kN/m²")

        st.subheader("Serviceability Limit State (SLS)")
        st.dataframe(sls_df, use_container_width=True)
        st.metric("Governing SLS", f"{gov_sls['Combination']}", f"{gov_sls['Value']:.2f} kN/m²")

        st.subheader("Material Design Strength")
        st.info(f"**{material}** → {mat_res}")

        # Export button
        combined = pd.concat([
            uls_df.assign(Type="ULS"),
            sls_df.assign(Type="SLS")
        ])
        csv = combined.to_csv(index=False)
        st.download_button(
            label="📥 Download results as CSV",
            data=csv,
            file_name="eurocode_combinations.csv",
            mime="text/csv"
        )
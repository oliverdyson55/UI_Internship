import streamlit as st
from MainPage import load_data, plot_macro, load_macro_data
import pandas as pd
from pathlib import Path
import datetime as dt
import matplotlib.pyplot as plt

# Path to the relevant processed Excel file
EXCEL_PATH = Path(r"outputs\spreadsheets\example_nutrient_data.xlsx")

# Root folder where images are stored - CHANGE TO MATCH YOURS
IMAGES_ROOT = Path(r"data/processed")


def main():
    st.title("Macronutrient Tracker") ## MAIN TITLE

    df = load_macro_data()

    # Select Patient
    patients = sorted(df["Patient ID"].dropna().unique())
    selected_patient = st.selectbox("Select Patient", patients)

    # Filter by patient
    df_patient = df[df["Patient ID"] == selected_patient]

    # Select Date / Session (or datetime)
    if "Date and Time" in df_patient.columns:
        df_patient["Month"] = df_patient["Date and Time"].dt.to_period("M")  # e.g. 2025-08
        unique_months = sorted(df_patient["Month"].unique())

        # Create dropdown with formatted month labels
        month_display_map = {m.strftime("%B %Y"): m for m in unique_months}
        selected_month_display = st.selectbox("Select Month", list(month_display_map.keys()))
        selected_month = month_display_map[selected_month_display]

        # Filter sessions within that month
        df_session = df_patient[df_patient["Month"] == selected_month]

        # For display text
        selection_label = selected_month_display

    else:
        sessions = df_patient["Subfolder"].unique()
        selected_session = st.selectbox("Select Session", sessions)
        df_session = df_patient[df_patient["Subfolder"] == selected_session]

        # For display text
        selection_label = selected_session

    st.write(f"Showing data for **{selected_patient}** on **{selection_label}**")
    # Placeholder for nutrient / ML output info
    st.markdown("### Macronutrients Values Over Time") 
    st.write("Macronutrient values for the past month.") 

    plot_macro(selected_patient, selected_month)
    

    # Show raw data rows for this patient & session
    st.markdown("### Raw Data")
    st.dataframe(df_session)

if __name__ == "__main__":
    main()


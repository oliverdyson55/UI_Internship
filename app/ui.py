import streamlit as st
import pandas as pd
from pathlib import Path
import datetime as dt

# Path to the processed Excel file
EXCEL_PATH = Path("outputs/spreadsheets/patient_data.xlsx")


# Root folder where images are stored (adjust if needed)
IMAGES_ROOT = Path("data/processed")

@st.cache_data
def load_data():
    df = pd.read_excel(EXCEL_PATH)
    # Ensure the 'Date and Time' column is datetime type
    if "Date and Time" in df.columns:
        df["Date and Time"] = pd.to_datetime(df["Date and Time"], dayfirst=True, errors="coerce")
    return df

def main():
    st.title("Patient Food Data Viewer") ## MAIN TITLE

    df = load_data()

    # Select Patient
    patients = sorted(df["Patient ID"].dropna().unique())
    selected_patient = st.selectbox("Select Patient", patients)

    # Filter by patient
    df_patient = df[df["Patient ID"] == selected_patient]

    # Select Date / Session (or datetime)
    if "Date and Time" in df_patient.columns:
        unique_datetimes = df_patient["Date and Time"].dropna().unique()
        unique_datetimes = sorted(unique_datetimes)
        session_display_map = {
            dt_val.strftime("%d/%m/%Y, %H:%M"): dt_val for dt_val in unique_datetimes
        }
        selected_session_display = st.selectbox("Select Date/Session", list(session_display_map.keys()))
        selected_session = session_display_map[selected_session_display]
        df_session = df_patient[df_patient["Date and Time"] == selected_session]
    else:
        sessions = df_patient["Subfolder"].unique()
        selected_session = st.selectbox("Select Date/Session", sessions)
        df_session = df_patient[df_patient["Subfolder"] == selected_session]

    st.write(f"Showing data for **{selected_patient}** on **{selected_session_display if 'selected_session_display' in locals() else selected_session}**")

    # Placeholder for nutrient / ML output info
    st.markdown("### Nutrient / ML Output Data") 
    st.write("Here you can display nutrient values or ML results when available.") ##

    ## PUT GRAPHS HERE
    ## WHEN CAN ACCESS DATA: can have bar chart of macronutrients, total sums etc

    ## HAVE A SEPERATE PAGE FOR PATIENT DATA and then linear graphs of calories and macronutrients etc

    # Try to display corresponding image.png
    try:
        if "Subfolder" in df_session.columns:
            subfolder = df_session["Subfolder"].iloc[0]
            img_path = IMAGES_ROOT / str(selected_patient) / subfolder / "image.jpeg" ## image path search
            if img_path.exists():
                st.markdown("### Food Image") ## image section title
                st.image(str(img_path), caption=f"{selected_patient} - {selected_session_display}") ## caption for image
            else:
                st.warning(f"No image.png found for this session: {img_path}")
        else:
            st.info("Subfolder info not available, cannot locate image.")
    except Exception as e:
        st.error(f"Error displaying image: {e}")

    # Show raw data rows for this patient & session
    st.markdown("### Raw Data")
    st.dataframe(df_session)

if __name__ == "__main__":
    main()



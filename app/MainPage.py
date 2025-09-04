import streamlit as st
import pandas as pd
from pathlib import Path
import datetime as dt
import matplotlib.pyplot as plt


# Path to the relevant processed Excel file
EXCEL_PATH = Path(r"outputs\spreadsheets\patient_data.xlsx")
MACRO_PATH = Path(r"outputs\spreadsheets\example_nutrient_data.xlsx")

# Root folder where images are stored - CHANGE TO MATCH YOURS
IMAGES_ROOT = Path(r"data/processed")

@st.cache_data
def load_data():
    df = pd.read_excel(EXCEL_PATH)
    # convert the 'Date and Time' column to handleable type
    if "Date and Time" in df.columns:
        df["Date and Time"] = pd.to_datetime(df["Date and Time"], dayfirst=True, errors="coerce")
    return df

def load_macro_data():
    df = pd.read_excel(MACRO_PATH)
    if "Date and Time" in df.columns:
        df["Date and Time"] = pd.to_datetime(df["Date and Time"], dayfirst=True, errors="coerce")
    return df

def get_before_after_pair(selected_session, sessions):
    """Return a (before, after) tuple for the selected session."""
    sessions = sorted(sessions)
    idx = sessions.index(selected_session)

    if len(sessions) == 1:
        st.warning("Only one session available, cannot create before/after pair.")
        return None, None

    if idx == 0:
        return sessions[idx], sessions[idx + 1]
    elif idx == len(sessions) - 1:
        return sessions[idx - 1], sessions[idx]
    else:
        return sessions[idx], sessions[idx + 1]
    

def plot_weight_chart(patient_id, selected_session, df_patient):
    """
    Display bar chart of 'before' and 'after' weights for the selected session.
    Returns the before_session datetime used for consistent image display.
    """

    # Sort sessions
    sessions = sorted(df_patient["Date and Time"].dropna().unique())
    before_session, after_session = get_before_after_pair(selected_session, sessions)

    if before_session is None or after_session is None:
        return None

    # Load weights
    base_path = IMAGES_ROOT / str(patient_id)
    weight_data = {}

    for session in [before_session, after_session]:
        session_str = session.strftime("%Y-%m-%d_%H-%M")
        matching_folders = list(base_path.glob(f"{session_str}*"))

        if matching_folders:
            weight_file = matching_folders[0] / "weight.txt"
            if weight_file.exists():
                try:
                    content = weight_file.read_text().strip()
                    weight_data[session] = float(content) if content else None
                except ValueError:
                    weight_data[session] = None
            else:
                weight_data[session] = None
        else:
            weight_data[session] = None

    if None in weight_data.values():
        st.warning("Missing weight data for before/after pair. Check folder names and weight.txt files.")
        st.write("Weight data dict:", weight_data)
        return before_session

    # bar chart
    fig, ax = plt.subplots()
    times = [before_session.strftime("%d/%m %H:%M"), after_session.strftime("%d/%m %H:%M")]
    weights = [weight_data[before_session], weight_data[after_session]]
    bars = ax.bar(times, weights, color=["steelblue", "salmon"])

    # data labels
    for bar, wt in zip(bars, weights):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.1,
                f"{wt:.1f} g", ha="center", va="bottom")

    ax.set_title("Weight Comparison (Before vs After)")
    ax.set_ylabel("Weight (g)")
    st.pyplot(fig)

    
    return before_session

def plot_macro(patient_id, selected_month):
    """
    Line graph of macronutrient values
    """
    df_macro = load_macro_data()

    # Filter to this patient
    df_patient_macro = df_macro[df_macro["Patient ID"] == patient_id]
    df_month = df_patient_macro[df_patient_macro["Date and Time"].dt.to_period("M") == selected_month]

    if df_month.empty:
        st.warning("No macronutrient data for this month")
        return
    
    df_month = df_month.copy()
    df_month["Date"] = df_month["Date and Time"].dt.date

    # Get available nutrients (exclude Patient ID + Date columns)
    nutrient_cols = [c for c in df_month.columns if c not in ["Patient ID", "Date and Time", "Date", "Before/After", "Subfolder", "Filename", "Full Path"]]

    # Let user pick which nutrients to plot
    selected_nutrients = st.multiselect(
        "Select macronutrient(s) to display",
        nutrient_cols,
        default=["Calories"],  # start with Calories
    )

    if not selected_nutrients:
        st.info("Select at least one nutrient to display.")
        return

    # Plot each nutrient separately (own subplot) for clear scales
    fig, axes = plt.subplots(len(selected_nutrients), 1, figsize=(8, 4*len(selected_nutrients)), sharex=True)

    if len(selected_nutrients) == 1:
        axes = [axes]  # make iterable

    for ax, nutrient in zip(axes, selected_nutrients):
        df_month[nutrient] = pd.to_numeric(df_month[nutrient], errors="coerce")
        ax.plot(df_month["Date"], df_month[nutrient], marker="o", label=nutrient)
        ax.set_title(f"{nutrient} over {selected_month.strftime('%B %Y')}")
        ax.set_xlabel("Date")
        ax.set_ylabel(nutrient)
        ax.legend()
        ax.grid(True)

    plt.xticks(rotation=45)
    st.pyplot(fig)



def main():
    st.title("Patient Food and Weight Viewer") ## MAIN TITLE

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
    st.markdown("### Weight Values") 
    st.write("Weight value for the current selected meal.") ##
    plot_weight_chart(selected_patient, selected_session, df_patient)

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




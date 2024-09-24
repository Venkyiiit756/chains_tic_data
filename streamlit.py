import streamlit as st
import pandas as pd
from io import BytesIO
import os

# Optional: Set page configuration
st.set_page_config(
    page_title="📊 Interactive Showtimes Viewer",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("📊 Interactive Showtimes Viewer")

# Define the path to the Excel file
EXCEL_FILE_PATH = "showtimes.xlsx"

@st.cache_data
def load_data(path):
    """
    Load Excel data into pandas DataFrames.
    Returns two DataFrames: Sheet1 and Sheet2.
    """
    try:
        xls = pd.ExcelFile(path, engine='openpyxl')
        sheet1 = pd.read_excel(xls, 'Sheet1')
        sheet2 = pd.read_excel(xls, 'Sheet2')
        return sheet1, sheet2
    except FileNotFoundError:
        st.error(f"❌ The file '{path}' was not found in the directory.")
        return None, None
    except Exception as e:
        st.error(f"❌ An error occurred while loading the file: {e}")
        return None, None

# Load data
sheet1_df, sheet2_df = load_data(EXCEL_FILE_PATH)

if sheet1_df is not None and sheet2_df is not None:
    st.sidebar.success("✅ 'showtimes.xlsx' loaded successfully!")

    # Display Sheet1
    st.header("🔍 Detailed Showtimes Data")
    st.dataframe(sheet1_df)

    # Filtering options in the sidebar
    st.sidebar.header("🛠️ Filters for Detailed Data")

    # Initialize filtered dataframe
    filtered_sheet1 = sheet1_df.copy()

    # Create filters based on column types
    for column in sheet1_df.columns:
        if sheet1_df[column].dtype == 'object' or pd.api.types.is_categorical_dtype(sheet1_df[column]):
            unique_values = sheet1_df[column].dropna().unique().tolist()
            selected_values = st.sidebar.multiselect(
                f"Filter by {column}",
                options=unique_values,
                default=unique_values
            )
            if selected_values:
                filtered_sheet1 = filtered_sheet1[filtered_sheet1[column].isin(selected_values)]
        elif pd.api.types.is_numeric_dtype(sheet1_df[column]):
            min_val = float(sheet1_df[column].min())
            max_val = float(sheet1_df[column].max())
            step = (max_val - min_val) / 100 if max_val != min_val else 1
            selected_range = st.sidebar.slider(
                f"Filter by {column}",
                min_value=min_val,
                max_value=max_val,
                value=(min_val, max_val),
                step=step
            )
            filtered_sheet1 = filtered_sheet1[filtered_sheet1[column].between(*selected_range)]
        elif pd.api.types.is_datetime64_any_dtype(sheet1_df[column]):
            min_date = sheet1_df[column].min()
            max_date = sheet1_df[column].max()
            selected_dates = st.sidebar.date_input(
                f"Filter by {column}",
                value=(min_date, max_date),
                min_value=min_date,
                max_value=max_date
            )
            if len(selected_dates) == 2:
                filtered_sheet1 = filtered_sheet1[
                    sheet1_df[column].between(pd.to_datetime(selected_dates[0]), pd.to_datetime(selected_dates[1]))
                ]

    st.subheader("📈 Filtered Detailed Data")
    st.dataframe(filtered_sheet1)

    # Display Sheet2
    st.header("📊 Aggregated Showtimes Data")
    st.dataframe(sheet2_df)

    # Download button for filtered data
    def convert_df_to_excel(df):
        """
        Convert DataFrame to Excel bytes.
        """
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False)
        processed_data = output.getvalue()
        return processed_data

    filtered_excel = convert_df_to_excel(filtered_sheet1)

    st.download_button(
        label="📥 Download Filtered Detailed Data as Excel",
        data=filtered_excel,
        file_name='filtered_showtimes.xlsx',
        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

else:
    st.info(f"📝 Please ensure that '{EXCEL_FILE_PATH}' is present in the project directory.")


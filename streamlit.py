import streamlit as st
import pandas as pd

st.title("Interactive Data Viewer")

# Upload Excel File
uploaded_file = st.file_uploader("Choose an Excel file", type=["xlsx", "xls"])

if uploaded_file is not None:
    # Read the Excel file
    df = pd.read_excel(uploaded_file, engine='openpyxl')
    
    st.write("### Data Preview")
    st.dataframe(df)  # Display dataframe

    st.write("### Filter Data")
    
    # Create filters based on dataframe columns
    for column in df.select_dtypes(include=['object', 'category']).columns:
        unique_values = df[column].unique().tolist()
        selected_values = st.multiselect(f"Filter by {column}", unique_values, default=unique_values)
        df = df[df[column].isin(selected_values)]
    
    for column in df.select_dtypes(include=['int64', 'float64']).columns:
        min_val = df[column].min()
        max_val = df[column].max()
        selected_range = st.slider(f"Filter by {column}", min_val, max_val, (min_val, max_val))
        df = df[df[column].between(*selected_range)]
    
    st.write("### Filtered Data")
    st.dataframe(df)

    # Download filtered data
    @st.cache
    def convert_df_to_excel(df):
        return df.to_excel(index=False).encode('base64')
    
    st.download_button(
        label="Download Filtered Data as Excel",
        data=df.to_excel(index=False),
        file_name='filtered_data.xlsx',
        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
else:
    st.info("Please upload an Excel file to get started.")

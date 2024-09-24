import streamlit as st
import pandas as pd
from io import BytesIO
import re

# Title of the App
st.title("Supply Chain Inventory Management")

# Step 1: Upload Excel file
uploaded_file = st.file_uploader("Upload your Excel file", type=["xlsx"])

# Step 2: Read and display the Excel sheet
if uploaded_file:
    # Load the Excel file
    df = pd.read_excel(uploaded_file)
    
    # Display the first few rows of the dataframe
    st.write("Here's the data from your file:")
    st.dataframe(df)

    # Get the columns from the uploaded file
    columns = df.columns.tolist()
    st.write("Columns in your data:", columns)

    # Step 3: Input the custom equation
    st.write("Enter your equation using column names:")
    equation = st.text_input("Enter equation (e.g., leadtime + thinfg):")
    
    # Create a mapping from user input to column names
    column_mapping = {col: col for col in columns}
    
    # Function to compute the result based on the equation
    def compute_result(row, eq):
        for col in columns:
            eq = eq.replace(col, f"row['{col}']")
        return eval(eq)

    # Validate the equation and compute the results
    if equation:
        try:
            # Apply the equation to each row
            df['result'] = df.apply(lambda row: compute_result(row, equation), axis=1)
            
            # Step 5: Input conditions for status
            st.write("Enter conditions to assign status based on the result:")
            
            # Define thresholds and corresponding statuses
            conditions = {
                "BOM": st.number_input("Enter BOM threshold:", value=100),
                "BAM": st.number_input("Enter BAM threshold:", value=50),
                "BEM": st.number_input("Enter BEM threshold:", value=0)
            }
            
            # Determine status based on the conditions
            def assign_status(value):
                if value >= conditions["BOM"]:
                    return "BOM"
                elif value >= conditions["BAM"]:
                    return "BAM"
                else:
                    return "BEM"

            df['status'] = df['result'].apply(assign_status)
            
            # Display the updated dataframe with the status column
            st.write("Updated DataFrame with the 'result' and 'status' columns:")
            st.dataframe(df)
            
            # Step 6: Create and display pie chart using pandas
            st.write("Status Distribution Pie Chart:")
            if 'status' in df.columns and not df['status'].empty:
                status_counts = df['status'].value_counts()
                st.write("Status Counts:")
                st.write(status_counts)
                
                # Plot pie chart using pandas
                pie_chart = status_counts.plot.pie(autopct='%1.1f%%', startangle=90, figsize=(6, 6))
                st.pyplot(pie_chart.get_figure())
            else:
                st.write("No data to display in pie chart.")
            
            # Step 7: Option to download the updated Excel sheet
            def convert_df_to_excel(df):
                """Convert DataFrame to Excel file."""
                output = BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    df.to_excel(writer, index=False)
                return output.getvalue()
            
            # Provide a download link
            st.download_button(
                label="Download updated Excel",
                data=convert_df_to_excel(df),
                file_name="updated_inventory_with_status.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        
        except Exception as e:
            st.error(f"Error in evaluating the equation: {e}")

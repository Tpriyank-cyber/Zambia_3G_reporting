# -*- coding: utf-8 -*-
"""
Created on Fri Dec 12 17:27:28 2025

@author: tpriyank
"""

import streamlit as st
import pandas as pd
import io

# Streamlit App Title
st.title("📊 3G KPI Data Processing Tool")

# Upload file
uploaded_file = st.file_uploader("📂 Upload your Excel file", type=["xlsx"])

# Dropdown for sheet selection
sheet_type = st.selectbox("Select sheet type:", ["BBH", "Continue"])

# Define KPI Columns
KPI_Obj = [
    'CS RRC Setup Success Rate',
    'PS RRC Setup Success Rate',
    'CS and Video RAB Setup Success Rate',
    'PS and HS RAB Setup Success Rate',
    'CS_drop_rate',
    'HS Drop Call Rate',
    'Act HS-DSCH  end usr thp',
    'Cell Availability, excluding blocked by user state (BLU)',
    'Total CS traffic - Erl',
    'Max simult HSDPA users',
    'Total_Data_Payload_DL_UL',
    'Soft HO Success rate, RT',
    'Average RTWP'
]

required_columns = [
    'cs_rrc_nom', 'cs_rrc_denom', 'PS_RRC_NOM_NOM', 'PS_RRC_DENOM_DENOM',
    'SpeechRAB_Nom', 'SpeechRab_denom', 'PSRAB_NOM', 'PSRAB_DENOM',
    'CSDROPNOM', 'CSDROPDENOM', 'HSdrop_Nom', 'HS Drop_Att'
]

# Function to calculate KPIs
def calculate_kpis(df):
    for col in required_columns:
        if col not in df.columns:
            st.warning(f"Missing column: {col}. Filling with 0.")
            df[col] = 0
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    
    df['CS RRC SR'] = (df['cs_rrc_nom'] / df['cs_rrc_denom']).replace([float('inf'), -float('inf')], 0) * 100
    df['PS RRC SR'] = (df['PS_RRC_NOM_NOM'] / df['PS_RRC_DENOM_DENOM']).replace([float('inf'), -float('inf')], 0) * 100
    df['CS RAB SR'] = (df['SpeechRAB_Nom'] / df['SpeechRab_denom']).replace([float('inf'), -float('inf')], 0) * 100
    df['PS RAB SR'] = (df['PSRAB_NOM'] / df['PSRAB_DENOM']).replace([float('inf'), -float('inf')], 0) * 100
    df['CS DCR'] = (df['CSDROPNOM'] / df['CSDROPDENOM']).replace([float('inf'), -float('inf')], 0) * 100
    df['HS DCR'] = (df['HSdrop_Nom'] / df['HS Drop_Att']).replace([float('inf'), -float('inf')], 0) * 100
    return df

# Button to Process File
if uploaded_file:
    df = pd.read_excel(uploaded_file)
    
    # Convert 'Period start time' to string
    df['Period start time'] = df['Period start time'].astype(str)
    
    # Clean up column names to avoid issues with extra spaces
    df.columns = df.columns.str.strip()

    # Proceed with other transformations
    df['Start Time'] = pd.to_datetime(df['Period start time'], errors='coerce')
    df['Date'] = df['Start Time'].dt.date
    df['Hour'] = df['Start Time'].dt.hour
    df = calculate_kpis(df)
    
    # Selecting Processing Type
    if sheet_type == "BBH":
        pivot = pd.pivot_table(df, index=['RNC name', 'WBTS name'], columns='Date', values=KPI_Obj, aggfunc='sum')
        output_filename = "3G_Day_Site_Level_KPIs_output.csv"
    else:
        selected_hour = st.number_input("Select Hour (0-23):", min_value=0, max_value=23, step=1)
        if selected_hour >= 0:
            df = df[df['Hour'] == selected_hour]
        pivot = pd.pivot_table(df, index=['RNC name', 'WCEL name'], columns='Date', values=KPI_Obj, aggfunc='sum')
        output_filename = "3G_Day_Cell_Level_KPIs_output.csv"
    
    pivot = pivot.stack(level=0).reset_index(drop=False)
    pivot.rename(columns={'level_2': 'KPI NAME'}, inplace=True)
    
    st.success("✅ Data Processed Successfully!")
    st.dataframe(pivot.head())

    # Convert to CSV for Download
    csv = pivot.to_csv(index=False, encoding='utf-8-sig')
    
    st.download_button(
        label="⬇️ Download Processed Data",
        data=csv,
        file_name=output_filename,
        mime="text/csv"
    )
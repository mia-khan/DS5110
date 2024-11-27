import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
from datetime import datetime

st.set_page_config(layout="wide")


@st.cache_resource
def get_connection():
    return sqlite3.connect('Cleaned_DPCA.db')


@st.cache_data
def load_raw_data():
    conn = get_connection()
    df = pd.read_sql("""
        SELECT 
            p.Patient_ID, p.Patient_Name, p.Age, p.Religion,
            p.Marriage_Status, proc.Procedure_Type,
            proc.Procedure_Cost, proc.Amount_Paid_DPCA,
            pf.Occupation, pf.Income, pf.Dependent_Members,
            fa.Aid_Type, ze.Is_Eligible
        FROM Patient p
        LEFT JOIN Procedure proc ON p.Patient_ID = proc.Patient_ID
        LEFT JOIN Patient_Financials pf ON p.Patient_ID = pf.Patient_ID
        LEFT JOIN Financial_Aid fa ON p.Patient_ID = fa.Patient_ID
        LEFT JOIN Zakat_Eligibility ze ON p.Patient_ID = ze.Patient_ID
    """, conn)
    return df


df = load_raw_data()

# Sidebar filters
with st.sidebar:
    st.header('Filters')

    religions = ['All'] + list(df['Religion'].dropna().unique())
    selected_religion = st.selectbox('Religion', religions)

    procedures = ['All'] + list(df['Procedure_Type'].dropna().unique())
    selected_procedure = st.selectbox('Procedure Type', procedures)

    min_income, max_income = float(df['Income'].min()), float(df['Income'].max())
    income_range = st.slider('Income Range', min_income, max_income, (min_income, max_income))

    min_age, max_age = float(df['Age'].min()), float(df['Age'].max())
    age_range = st.slider('Age Range', min_age, max_age, (min_age, max_age))

# Apply filters
filtered_df = df.copy()
if selected_religion != 'All':
    filtered_df = filtered_df[filtered_df['Religion'] == selected_religion]
if selected_procedure != 'All':
    filtered_df = filtered_df[filtered_df['Procedure_Type'] == selected_procedure]
filtered_df = filtered_df[
    (filtered_df['Income'].between(income_range[0], income_range[1])) &
    (filtered_df['Age'].between(age_range[0], age_range[1]))
    ]

# Create tabs with visualizations
tab1, tab2, tab3, tab4 = st.tabs(['Overview', 'Procedures', 'Demographics', 'Financial'])

with tab1:
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Patients", len(filtered_df['Patient_ID'].unique()))
    with col2:
        st.metric("Avg Procedure Cost", f"Rs. {filtered_df['Procedure_Cost'].mean():,.2f}")
    with col3:
        st.metric("Total Aid", f"Rs. {filtered_df['Amount_Paid_DPCA'].sum():,.2f}")

with tab2:
    col1, col2 = st.columns(2)
    with col1:
        proc_counts = filtered_df['Procedure_Type'].value_counts().reset_index()
        proc_counts.columns = ['Procedure_Type', 'Count']
        fig = px.bar(
            proc_counts,
            x='Procedure_Type',
            y='Count',
            title='Procedure Distribution'
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig = px.bar(
            filtered_df.groupby('Procedure_Type')['Procedure_Cost'].mean().reset_index(),
            x='Procedure_Type',
            y='Procedure_Cost',
            title='Average Cost by Procedure'
        )
        st.plotly_chart(fig, use_container_width=True)

with tab3:
    col1, col2 = st.columns(2)
    with col1:
        fig = px.pie(
            filtered_df,
            names='Religion',
            title='Religious Distribution'
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig = px.histogram(
            filtered_df,
            x='Age',
            nbins=20,
            title='Age Distribution'
        )
        st.plotly_chart(fig, use_container_width=True)

with tab4:
    col1, col2 = st.columns(2)
    with col1:
        fig = px.bar(
            filtered_df.groupby('Occupation')['Income'].mean().reset_index(),
            x='Occupation',
            y='Income',
            title='Average Income by Occupation'
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig = px.scatter(
            filtered_df,
            x='Income',
            y='Amount_Paid_DPCA',
            color='Is_Eligible',
            title='Aid Amount vs Income'
        )
        st.plotly_chart(fig, use_container_width=True)

# Display filtered data
st.dataframe(filtered_df)
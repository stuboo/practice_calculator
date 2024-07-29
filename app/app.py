import streamlit as st
import pandas as pd

# Define constants for wRVU values including established patient codes
wrvu_values = {
    '99203': 1.6,
    '99204': 2.6,
    '99205': 3.5,
    '99212': 0.7,
    '99213': 1.3,
    '99214': 1.92,
    '99215': 2.8
}

# Define reimbursement tiers
tier1_threshold = 6017
tier2_threshold = 9402
tier1_rate = 55.26
tier2_rate = 60.65
tier3_rate = 53.91

# Function to calculate projected income based on the tiered reimbursement model
def calculate_projected_income(annual_wrvu):
    if annual_wrvu <= tier1_threshold:
        income = annual_wrvu * tier1_rate
    elif annual_wrvu <= tier2_threshold:
        income = (tier1_threshold * tier1_rate) + ((annual_wrvu - tier1_threshold) * tier2_rate)
    else:
        income = (tier1_threshold * tier1_rate) + ((tier2_threshold - tier1_threshold) * tier2_rate) + ((annual_wrvu - tier2_threshold) * tier3_rate)
    return income

class ProjectionCalculator:
    def __init__(self, new_patients, established_patients, sessions_per_week, weeks_per_year, new_code_dist,
                 est_code_dist, diagnosis_dist, juice_ratio, avg_wrvu):
        self.new_patients = new_patients
        self.established_patients = established_patients
        self.sessions_per_week = sessions_per_week
        self.weeks_per_year = weeks_per_year
        self.new_code_dist = new_code_dist
        self.est_code_dist = est_code_dist
        self.diagnosis_dist = diagnosis_dist
        self.juice_ratio = juice_ratio
        self.avg_wrvu = avg_wrvu

    def calculate_projections(self):
        # Calculate new patient charges based on distribution
        new_patient_charges = sum(self.new_code_dist[code] * wrvu_values[code] for code in self.new_code_dist)

        # Calculate established patient charges based on distribution
        established_patient_charges = sum(self.est_code_dist[code] * wrvu_values[code] for code in self.est_code_dist)

        # Calculate diagnosis group distributions
        pop_patients = self.new_patients * self.diagnosis_dist['POP']
        sui_patients = self.new_patients * self.diagnosis_dist['SUI']
        oab_patients = self.new_patients * self.diagnosis_dist['OAB']

        # Calculate surgery cases and wRVU generation for POP and SUI
        pop_surgeries = pop_patients * self.juice_ratio['POP']
        sui_surgeries = sui_patients * self.juice_ratio['SUI']
        pop_wrvu_or = pop_surgeries * self.avg_wrvu['POP']
        sui_wrvu_or = sui_surgeries * self.avg_wrvu['SUI']

        # Calculate advanced therapy cases and wRVU generation for OAB
        oab_advanced = oab_patients * self.juice_ratio['OAB']
        oab_wrvu_or = oab_advanced * self.avg_wrvu['OAB']

        # Calculate total wRVU for OR
        or_wrvu = pop_wrvu_or + sui_wrvu_or + oab_wrvu_or

        # Calculate total wRVU for office
        office_wrvu = (self.new_patients * new_patient_charges) + (
                    self.established_patients * established_patient_charges)

        # Calculate total wRVU and revenue projections
        sessions_per_year = self.sessions_per_week * self.weeks_per_year
        monthly_office_wrvu = office_wrvu * (sessions_per_year / 12)
        monthly_or_wrvu = or_wrvu * (sessions_per_year / 12)
        monthly_wrvu = monthly_office_wrvu + monthly_or_wrvu
        annual_wrvu = monthly_wrvu * 12

        return (
            round(monthly_wrvu),
            round(annual_wrvu),
            round(monthly_office_wrvu),
            round(monthly_or_wrvu),
            round(pop_patients),
            round(sui_patients),
            round(oab_patients)
        )
    def display_projections(self):
        monthly_wrvu, annual_wrvu, monthly_office_wrvu, monthly_or_wrvu, pop_patients, sui_patients, oab_patients = self.calculate_projections()

        # Calculate total wRVUs
        total_monthly_office_wrvu = monthly_office_wrvu
        total_annual_office_wrvu = monthly_office_wrvu * 12
        total_monthly_or_wrvu = monthly_or_wrvu
        total_annual_or_wrvu = monthly_or_wrvu * 12

        # Create a DataFrame for wRVU summary
        wrvu_data = {
            'POP': [monthly_office_wrvu * self.diagnosis_dist['POP'], monthly_or_wrvu * self.diagnosis_dist['POP'],
                    total_monthly_office_wrvu * self.diagnosis_dist['POP'],
                    total_annual_or_wrvu * self.diagnosis_dist['POP']],
            'SUI': [monthly_office_wrvu * self.diagnosis_dist['SUI'], monthly_or_wrvu * self.diagnosis_dist['SUI'],
                    total_monthly_office_wrvu * self.diagnosis_dist['SUI'],
                    total_annual_or_wrvu * self.diagnosis_dist['SUI']],
            'OAB': [monthly_office_wrvu * self.diagnosis_dist['OAB'], monthly_or_wrvu * self.diagnosis_dist['OAB'],
                    total_monthly_office_wrvu * self.diagnosis_dist['OAB'],
                    total_annual_or_wrvu * self.diagnosis_dist['OAB']],
            'Total': [total_monthly_office_wrvu, total_monthly_or_wrvu, total_annual_office_wrvu, total_annual_or_wrvu]
        }
        wrvu_df = pd.DataFrame(wrvu_data, index=['Monthly Office', 'Monthly OR', 'Annual Office', 'Annual OR'])

        # Display DataFrame
        st.dataframe(wrvu_df)

        st.markdown('</div>', unsafe_allow_html=True)

# Set the page configuration to be wider
st.set_page_config(layout="wide")

# Streamlit interface
st.title("Practice Variables Dashboard")

# Custom CSS for background colors using Tableau palette
st.markdown(
    """
    <style>
    .row-1-col-1 {
        background-color: #4E79A7;
        padding: 10px;
        border-radius: 10px;
        color: white;
    }
    .row-1-col-2 {
        background-color: #F28E2B;
        padding: 10px;
        border-radius: 10px;
        color: white;
    }
    .row-1-col-3 {
        background-color: #E15759;
        padding: 10px;
        border-radius: 10px;
        color: white;
    }
    .row-2-col-1 {
        background-color: #76B7B2;
        padding: 10px;
        border-radius: 10px;
        color: white;
    }
    .row-2-col-2 {
        background-color: #59A14F;
        padding: 10px;
        border-radius: 10px;
        color: white;
    }
    .row-2-col-3 {
        background-color: #EDC948;
        padding: 10px;
        border-radius: 10px;
        color: white;
    }
    .reference {
        background-color: #bab0ac;
        padding: 10px;
        border-radius: 10px;
        color: black;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Create tabs
tab1, tab2 = st.tabs(["Surgeon", "APP"])

# Tab 1 content
with tab1:
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown('<div class="row-1-col-1">', unsafe_allow_html=True)
        st.subheader("General Settings")
        new_patients = st.number_input("New patients per session", min_value=1, value=4)
        sessions_per_week = st.number_input("Sessions per week", min_value=1, value=5)
        weeks_per_year = st.number_input("Weeks per year", min_value=1, value=44)
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="row-1-col-2">', unsafe_allow_html=True)
        st.subheader("Diagnosis Group Distribution (%)")
        diagnosis_dist = {
            'POP': st.slider('Pelvic Organ Prolapse', 0, 100, 30, step=5) / 100,
            'SUI': st.slider('Stress Incontinence', 0, 100, 30, step=5) / 100,
            'OAB': st.slider('Urge Incontinence and OAB', 0, 100, 35, step=5) / 100,
        }
        st.markdown('</div>', unsafe_allow_html=True)

    with col3:
        st.markdown('<div class="row-1-col-3">', unsafe_allow_html=True)
        st.subheader("Juice to Squeeze Ratio (%)")
        juice_ratio = {
            'POP': st.slider('POP Surgery within 6 months', 0, 100, 50, step=5) / 100,
            'SUI': st.slider('SUI Surgery within 6 months', 0, 100, 75, step=5) / 100,
            'OAB': st.slider('OAB Advanced Therapy within 6 months', 0, 100, 10, step=5) / 100,
        }
        st.markdown('</div>', unsafe_allow_html=True)

    col4, col5, col6 = st.columns(3)

    with col4:
        st.markdown('<div class="row-2-col-1">', unsafe_allow_html=True)
        st.subheader("New Patient Charge Distribution (%)")
        new_code_dist = {
            '99203': st.slider('99203 (1.6 wRVU)', 0, 100, 10, step=5) / 100,
            '99204': st.slider('99204 (2.6 wRVU)', 0, 100, 20, step=5) / 100,
            '99205': st.slider('99205 (3.5 wRVU)', 0, 100, 70, step=5) / 100,
        }
        st.markdown('</div>', unsafe_allow_html=True)

    with col5:
        st.markdown('<div class="row-2-col-2">', unsafe_allow_html=True)
        st.subheader("Average wRVU per Case")
        avg_wrvu = {
            'POP': st.number_input('Average wRVU per POP case', min_value=0.0, value=22.0),
            'SUI': st.number_input('Average wRVU per SUI case', min_value=0.0, value=12.0),
            'OAB': st.number_input('Average wRVU per OAB advanced therapy case', min_value=0.0, value=5.0),
        }
        st.markdown('</div>', unsafe_allow_html=True)

    with col6:
        # Calculate projections
        calculator = ProjectionCalculator(new_patients, 0, sessions_per_week, weeks_per_year, new_code_dist, {},
                                          diagnosis_dist, juice_ratio, avg_wrvu)
        monthly_wrvu, annual_wrvu, monthly_office_wrvu, monthly_or_wrvu, pop_patients, sui_patients, oab_patients = calculator.calculate_projections()

        st.markdown('<div class="row-2-col-3">', unsafe_allow_html=True)
        st.subheader("Summary")

        # Calculate total wRVUs
        total_monthly_office_wrvu = monthly_office_wrvu
        total_annual_office_wrvu = monthly_office_wrvu * 12
        total_monthly_or_wrvu = monthly_or_wrvu
        total_annual_or_wrvu = monthly_or_wrvu * 12

        # Create a DataFrame for wRVU summary
        wrvu_data = {
            'POP': [monthly_office_wrvu * diagnosis_dist['POP'], monthly_or_wrvu * diagnosis_dist['POP'],
                    total_monthly_office_wrvu * diagnosis_dist['POP'], total_annual_or_wrvu * diagnosis_dist['POP']],
            'SUI': [monthly_office_wrvu * diagnosis_dist['SUI'], monthly_or_wrvu * diagnosis_dist['SUI'],
                    total_monthly_office_wrvu * diagnosis_dist['SUI'], total_annual_or_wrvu * diagnosis_dist['SUI']],
            'OAB': [monthly_office_wrvu * diagnosis_dist['OAB'], monthly_or_wrvu * diagnosis_dist['OAB'],
                    total_monthly_office_wrvu * diagnosis_dist['OAB'], total_annual_or_wrvu * diagnosis_dist['OAB']],
            'Total': [total_monthly_office_wrvu, total_monthly_or_wrvu, total_annual_office_wrvu, total_annual_or_wrvu]
        }
        wrvu_df = pd.DataFrame(wrvu_data, index=['Monthly Office', 'Monthly OR', 'Annual Office', 'Annual OR'])

        # Display DataFrame
        st.dataframe(wrvu_df)

        # Calculate projected income
        projected_income = calculate_projected_income(annual_wrvu)

        # Display projected income
        st.subheader(f"Projected: ${projected_income:,.2f}")

        st.markdown('</div>', unsafe_allow_html=True)

with tab2:
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown('<div class="row-1-col-1">', unsafe_allow_html=True)
        st.subheader("General Settings")
        new_patients = st.number_input("New patients per session", min_value=1, value=4, key="tab2_new_patients")
        established_patients = st.number_input("Established patients per session", min_value=1, value=8)
        sessions_per_week = st.number_input("Sessions per week", min_value=1, value=5, key="tab2_sessions_per_week")
        weeks_per_year = st.number_input("Weeks per year", min_value=1, value=44, key="tab2_weeks_per_year")
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="row-1-col-2">', unsafe_allow_html=True)
        st.subheader("Diagnosis Group Distribution (%)")
        diagnosis_dist = {
            'POP': st.slider('Pelvic Organ Prolapse', 0, 100, 30, step=5, key="tab2_POP") / 100,
            'SUI': st.slider('Stress Incontinence', 0, 100, 30, step=5, key="tab2_SUI") / 100,
            'OAB': st.slider('Urge Incontinence and OAB', 0, 100, 35, step=5, key="tab2_OAB") / 100,
        }
        st.markdown('</div>', unsafe_allow_html=True)

    with col3:
        st.markdown('<div class="row-1-col-3">', unsafe_allow_html=True)
        st.subheader("Juice to Squeeze Ratio (%)")
        juice_ratio = {
            'POP': st.slider('POP Surgery within 6 months', 0, 100, 50, step=5, key="tab2_POP_juice") / 100,
            'SUI': st.slider('SUI Surgery within 6 months', 0, 100, 75, step=5, key="tab2_SUI_juice") / 100,
            'OAB': st.slider('OAB Advanced Therapy within 6 months', 0, 100, 10, step=5, key="tab2_OAB_juice") / 100,
        }
        st.markdown('</div>', unsafe_allow_html=True)

    col4, col5, col6 = st.columns(3)

    with col4:
        st.markdown('<div class="row-2-col-1">', unsafe_allow_html=True)
        st.subheader("New Patient Charge Distribution (%)")
        new_code_dist = {
            '99203': st.slider('99203 (1.6 wRVU)', 0, 100, 10, step=5, key="tab2_99203") / 100,
            '99204': st.slider('99204 (2.6 wRVU)', 0, 100, 20, step=5, key="tab2_99204") / 100,
            '99205': st.slider('99205 (3.5 wRVU)', 0, 100, 70, step=5, key="tab2_99205") / 100,
        }
        st.markdown('</div>', unsafe_allow_html=True)

    with col5:
        st.markdown('<div class="row-2-col-2">', unsafe_allow_html=True)
        st.subheader("Established Patient Charge Distribution (%)")
        est_code_dist = {
            '99212': st.slider('99212 (0.7 wRVU)', 0, 100, 10, step=5, key="tab2_99212") / 100,
            '99213': st.slider('99213 (1.3 wRVU)', 0, 100, 20, step=5, key="tab2_99213") / 100,
            '99214': st.slider('99214 (1.92 wRVU)', 0, 100, 50, step=5, key="tab2_99214") / 100,
            '99215': st.slider('99215 (2.8 wRVU)', 0, 100, 20, step=5, key="tab2_99215") / 100,
        }
        st.markdown('</div>', unsafe_allow_html=True)

    with col6:
        st.markdown('<div class="row-2-col-3">', unsafe_allow_html=True)
        st.subheader("Average wRVU per Case")
        avg_wrvu = {
            'POP': st.number_input('Average wRVU per POP case', min_value=0.0, value=22.0, key="tab2_avg_POP"),
            'SUI': st.number_input('Average wRVU per SUI case', min_value=0.0, value=12.0, key="tab2_avg_SUI"),
            'OAB': st.number_input('Average wRVU per OAB advanced therapy case', min_value=0.0, value=5.0,
                                   key="tab2_avg_OAB"),
        }
        st.markdown('</div>', unsafe_allow_html=True)

    # Calculate counts
    weekly_new_counts = new_patients * sessions_per_week
    monthly_new_counts = weekly_new_counts * 4
    yearly_new_counts = monthly_new_counts * 12
    weekly_est_counts = established_patients * sessions_per_week
    monthly_est_counts = weekly_est_counts * 4
    yearly_est_counts = monthly_est_counts * 12

    col7, col8, col9 = st.columns(3)

    with col7:
        st.markdown('<div class="row-3-col-1">', unsafe_allow_html=True)
        st.subheader("wRVU Summary")
        calculator = ProjectionCalculator(new_patients, established_patients, sessions_per_week, weeks_per_year,
                                          new_code_dist, est_code_dist, diagnosis_dist, juice_ratio, avg_wrvu)
        calculator.display_projections()
        st.markdown('</div>', unsafe_allow_html=True)

    with col8:
        st.markdown('<div class="row-3-col-2">', unsafe_allow_html=True)
        st.subheader("Counts Summary")

        # Calculate counts
        counts_data = {
            'POP': [
                weekly_new_counts * diagnosis_dist['POP'],
                monthly_new_counts * diagnosis_dist['POP'],
                yearly_new_counts * diagnosis_dist['POP'],
                weekly_est_counts * diagnosis_dist['POP'],
                monthly_est_counts * diagnosis_dist['POP'],
                yearly_est_counts * diagnosis_dist['POP']
            ],
            'SUI': [
                weekly_new_counts * diagnosis_dist['SUI'],
                monthly_new_counts * diagnosis_dist['SUI'],
                yearly_new_counts * diagnosis_dist['SUI'],
                weekly_est_counts * diagnosis_dist['SUI'],
                monthly_est_counts * diagnosis_dist['SUI'],
                yearly_est_counts * diagnosis_dist['SUI']
            ],
            'OAB': [
                weekly_new_counts * diagnosis_dist['OAB'],
                monthly_new_counts * diagnosis_dist['OAB'],
                yearly_new_counts * diagnosis_dist['OAB'],
                weekly_est_counts * diagnosis_dist['OAB'],
                monthly_est_counts * diagnosis_dist['OAB'],
                yearly_est_counts * diagnosis_dist['OAB']
            ],
            'Total': [
                weekly_new_counts,
                monthly_new_counts,
                yearly_new_counts,
                weekly_est_counts,
                monthly_est_counts,
                yearly_est_counts
            ]
        }

        counts_df = pd.DataFrame(counts_data,
                                 index=['New Week', 'New Month', 'New Year', 'Est. Week', 'Est. Month', 'Est. Year'])

        # Display DataFrame
        st.dataframe(counts_df)

        st.markdown('</div>', unsafe_allow_html=True)

    with col9:
        st.markdown('<div class="row-3-col-3">', unsafe_allow_html=True)
        st.subheader("Code Counts Summary")

        # Calculate counts for codes
        code_counts = {}
        for code in ['99212', '99213', '99214', '99215', '99203', '99204', '99205']:
            weekly_counts = sessions_per_week * (established_patients if '9921' in code else new_patients) * (
                est_code_dist[code] if '9921' in code else new_code_dist[code])
            monthly_counts = weekly_counts * 4
            yearly_counts = monthly_counts * 12
            code_counts[code] = [weekly_counts, monthly_counts, yearly_counts, yearly_counts]

        # Convert to DataFrame for better display
        code_counts_df = pd.DataFrame.from_dict(code_counts, orient='index', columns=['Week', 'Month', 'Year', 'Total'])

        # Display DataFrame
        st.dataframe(code_counts_df)

        st.markdown('</div>', unsafe_allow_html=True)
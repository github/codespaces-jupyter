import streamlit as st
import joblib
import pandas as pd
import matplotlib.pyplot as plt

# Load the model
model = joblib.load('CS/credit_score_model.pkl')

# Define the categorical features
categorical_features = ['Month', 'Occupation', 'Credit_Mix', 'Payment_of_Min_Amount', 'Payment_Behaviour']

# Define the numerical features
numerical_features = ['Age', 'Annual_Income', 'Monthly_Inhand_Salary', 'Num_Bank_Accounts',
       'Num_Credit_Card', 'Interest_Rate', 'Delay_from_due_date',
       'Num_of_Delayed_Payment', 'Changed_Credit_Limit',
       'Num_Credit_Inquiries', 'Outstanding_Debt', 'Credit_Utilization_Ratio',
       'Credit_History_Age', 'Total_EMI_per_month', 'Amount_invested_monthly',
       'Monthly_Balance', 'Count_Auto Loan', 'Count_Credit-Builder Loan',
       'Count_Personal Loan', 'Count_Home Equity Loan', 'Count_Not Specified',
       'Count_Mortgage Loan', 'Count_Student Loan',
       'Count_Debt Consolidation Loan', 'Count_Payday Loan']

# Create a title for the app
st.title('Credit Score Prediction App')

# Add some style to the app
st.markdown("""
<style>
body {
    color: #000;
    background-color: #f5f5dc;
}
</style>
    """, unsafe_allow_html=True)

# Create a sidebar for user input
st.sidebar.header('User Input Features')

# Create a dictionary to store the user input
user_input = {}

# Create input fields for the categorical features
for feature in categorical_features:
    if feature == 'Month':
        options = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
    elif feature == 'Occupation':
        options = ['Scientist', 'Teacher', 'Engineer', 'Entrepreneur', 'Lawyer']
    elif feature == 'Credit_Mix':
        options = ['Good', 'Bad', 'Average']
    elif feature == 'Payment_of_Min_Amount':
        options = ['Yes', 'No']
    elif feature == 'Payment_Behaviour':
        options = ['Low_spent_Small_value_payments', 'High_spent_Large_value_payments', 'High_spent_Medium_value_payments', 'Low_spent_Large_value_payments', 'High_spent_Small_value_payments']
    user_input[feature] = st.sidebar.selectbox(feature, options=options)

# Create input fields for the numerical features
for feature in numerical_features:
    user_input[feature] = st.sidebar.number_input(feature)

# When the 'Predict' button is clicked, make a prediction using the user input
if st.sidebar.button('Predict'):
    # Convert the user input to a DataFrame
    user_input_df = pd.DataFrame([user_input])

    # Make a prediction using the model
    prediction = model.predict(user_input_df)

    # Display the prediction
    st.write(f'Predicted Credit Score: {prediction[0]}')

    # Add a brief explanation for the prediction
    st.write("""
    This prediction is based on the input values you provided for the various features. 
    The model takes into account factors such as age, income, number of bank accounts, 
    credit card usage, and more to predict the credit score.
    """)

    # Plot all numerical features on one graph
    st.line_chart(user_input_df[numerical_features])
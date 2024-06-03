
import streamlit as st

st.title("Your first ML Data app using streamlit :) ")

st.markdown("""
## Task 10

Call your favourite model using mlflow from withing streamlit
        """)

content= st.text_input("Type your query", value='I lost my card')
if st.button("Predict"):
    st.text("Replace here with the predicted Output")

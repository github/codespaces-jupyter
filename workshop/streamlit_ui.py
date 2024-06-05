
import streamlit as st

st.title("Your first ML Data app using streamlit :) ")

st.markdown("""
## Task 10 (and last!)

Call your favourite model using mlflow from withing streamlit and visualise it in the streamlit web app.

Tip: to run and visualize streamlit run in the terminal:
```
streamlit run workshop/streamlit_ui.py
```
            
## Solution
        """)

content= st.text_input("Type your query", value='I lost my card')
if st.button("Predict"):
    st.text("Replace here with the predicted Output")

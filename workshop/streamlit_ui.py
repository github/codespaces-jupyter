
import streamlit as st

st.title("Your first ML Data app using streamlit :) ")

st.markdown("""
## Task 10

Call your favourite model using mlflow from withing streamlit
            

Tip: to run and visualize streamlit do:

``` streamlit run workshop/streamlit_ui.py````
        
        """)

content= st.text_input("Type your query", value='I lost my card')
if st.button("Predict"):
    st.text("Replace here with the predicted Output")

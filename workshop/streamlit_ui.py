
import streamlit as st
from workshop.pipeline import Pipeline

pipeline = Pipeline()
st.title("Workshop Streamlit App")

content= st.text_input("Type your query", value='I lost my card')
if st.button("Predict"):
    st.text(pipeline.predict_mlflow_model(content))

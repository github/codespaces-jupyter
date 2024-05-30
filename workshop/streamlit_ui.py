
import streamlit as st
import mlflow
from sentence_transformers import SentenceTransformer
sentences = ["This is an example sentence", "Each sentence is converted"]

embeddings_model = SentenceTransformer('sentence-transformers/all-mpnet-base-v2')
model = mlflow.sklearn.load_model("file:///workspaces/build-your-first-ml-pipeline-workshop/notebooks/mlruns/0/bcd3e16c12ac48b48a42b0ebc6e887b9/artifacts/mymodel")

st.title("Workshop")

content= st.text_input("Type your query", value='I lost my card')
if st.button("Predict"):
    st.text(model.predict(embeddings_model.encode(content).reshape(1, -1)))

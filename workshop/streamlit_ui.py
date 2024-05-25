
import streamlit as st
from datasets import load_dataset

st.text("Workshop")


dataset = load_dataset(
"yelp_review_full", split='test'
)

st.dataframe(dataset.to_pandas())
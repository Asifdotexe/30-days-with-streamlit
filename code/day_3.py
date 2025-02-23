"""
Day 3 out of 30
Implementing buttons

@author: Asif Sayyed
"""

import streamlit as st

st.header("Implementing st.button")

if st.button("I'm here!"):
    st.write("Yayyy, I am no longer lonely!")
else:
    st.write("I'm all alone :(")
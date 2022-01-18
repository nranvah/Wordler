import WordlerUtils as wut
import streamlit as st

st.title('Wordle with Friends')

word_length = st.slider('Word Length', min_value=3, max_value=10, value=5, step=1)
st.text(f'So, you want to play a wordle of word length = {word_length}')
max_tries = st.slider('Max tries', min_value=4, max_value=15, value=5, step=1)
st.text(f'So, you want to play a wordle with max tries = {max_tries}')

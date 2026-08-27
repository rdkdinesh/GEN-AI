import streamlit as st

def calculate_grade(score):
    if score >= 90 and score <= 100:
        return 'A'
    elif score >= 80 and score < 90:
        return 'B'
    elif score >= 70 and score < 80:
        return 'C'
    elif score >= 60 and score < 70:
        return 'D'
    else:
        return 'E'

# Streamlit app
st.title("Student Grade Calculator")

score = st.number_input("Enter your score (0-100):", min_value=1, max_value=100, step=1)
grade = calculate_grade(score)
st.write(f"Your grade is: {grade}")
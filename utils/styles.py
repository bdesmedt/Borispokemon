import streamlit as st


def inject_custom_css():
    st.markdown(
        """
        <style>
        .stButton > button {
            border-radius: 8px;
            font-weight: 600;
            transition: transform 0.1s ease;
        }
        .stButton > button:hover {
            transform: scale(1.03);
        }
        .stMetric {
            background-color: rgba(255, 255, 255, 0.05);
            border-radius: 8px;
            padding: 0.5rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

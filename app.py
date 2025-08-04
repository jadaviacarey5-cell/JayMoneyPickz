import streamlit as st

st.set_page_config(page_title="JayMoneyPickz", layout="centered")

st.title("📊 Welcome to JayMoneyPickz")
st.markdown("Use the sidebar to simulate a prop or generate today's top slips.")

st.sidebar.title("Menu")
choice = st.sidebar.radio("Choose a tool:", ["Simulate Prop", "Generate Slips"])

if choice == "Simulate Prop":
    st.subheader("Simulate a Player Prop")
    st.info("Coming soon: Type a prop like 'Alcantara 6.5 Ks vs HOU'")
elif choice == "Generate Slips":
    st.subheader("Top 5-6 Pick Slips")
    st.info("Coming soon: This will auto-load slips for all sports.")

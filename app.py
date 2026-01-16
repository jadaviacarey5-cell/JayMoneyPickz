import streamlit as st
from modules.decision_logic import make_pick
from modules.errors import DataUnavailableError, ModelAccuracyError, NoPickError
from modules.input_handler import normalize_sport, parse_user_input
from modules.model_selector import select_model
from modules.simulator import run_simulation
from modules.slip_generator import generate_top_slips

st.set_page_config(page_title="JayMoneyPickz", layout="centered")
st.title("📊 Welcome to JayMoneyPickz")

menu = st.sidebar.radio("Choose an option", ["Simulate Prop", "Generate Top 5-6 Slips"])

if menu == "Simulate Prop":
    sport_choice = st.selectbox(
        "Select the sport",
        ["mlb", "tennis", "wnba", "soccer", "pga", "cs2", "lol", "val"],
    )
    user_input = st.text_input("Enter a prop (e.g. Alcantara 6.5 Strikeouts vs HOU):")
    if st.button("Simulate"):
        try:
            parsed = parse_user_input(user_input)
            parsed["sport"] = normalize_sport(sport_choice)
            bundle = select_model(parsed)
            model_result = bundle.model.predict(bundle.features["vector"])
            results = run_simulation(model_result, parsed)
            pick = make_pick(results, parsed["line"])

            st.success(f"✅ Recommended Pick: **{pick.upper()}**")
            st.markdown(f"- **Player:** {parsed['player']}")
            st.markdown(f"- **Prop:** {parsed['line']} {parsed['prop_type']}")
            st.markdown(f"- **Mean projection:** {results.mean:.2f}")
            st.markdown(f"- **Simulations:** {results.simulations}")
            st.markdown(f"- **Model accuracy gate:** {results.accuracy*100:.1f}%")
            st.markdown(f"- **Over %:** {results.over_prob*100:.1f}%")
            st.markdown(f"- **Under %:** {results.under_prob*100:.1f}%")
        except (DataUnavailableError, ModelAccuracyError, NoPickError) as e:
            st.error(f"❌ {e}")

elif menu == "Generate Top 5-6 Slips":
    sport = st.selectbox("Pick a sport", ["mlb", "tennis", "wnba", "soccer", "pga", "cs2", "lol", "val"])
    if st.button("Generate Slip"):
        with st.spinner("Simulating best plays..."):
            picks = generate_top_slips(sport)
            if not picks:
                st.warning("No +EV props found right now.")
            for p in picks:
                st.markdown(f"**{p['pick']}** {p['player']} {p['line']} {p['prop_type']} — **Edge: {round(p['edge']*100)}%**")

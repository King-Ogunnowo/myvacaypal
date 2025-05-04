import streamlit as st
import random
import time
import os

from pipeline.converse import converse
from pipeline.orchestrator import orchestrator

def remove_chat_history():
    file_paths = [
        "/Users/oluwaseyi/Documents/repositories/myvacaypal/pipeline/converse/converse_output/chat_history.json",
        "/Users/oluwaseyi/Documents/repositories/myvacaypal/pipeline/entity_extraction/entity_extraction_output/entities.json",
        "/Users/oluwaseyi/Documents/repositories/myvacaypal/pipeline/flight_search/flight_search_output/flight.json",
        "/Users/oluwaseyi/Documents/repositories/myvacaypal/pipeline/hotel_search/hotel_search_output/hotels.json",
        "/Users/oluwaseyi/Documents/repositories/myvacaypal/pipeline/flight_search/flight_search_output/flattened_flight_confirmation_results.csv"
    ]
    for path in file_paths:
        if os.path.exists(path):
            os.remove(path)


import pandas as pd
import streamlit as st

def render_flight_thumbnails():
    """
    Render grouped flight offers as thumbnail cards in Streamlit.

    Parameters:
        df (pd.DataFrame): Flattened DataFrame with flight segments.
    """
    df = pd.read_csv("/Users/oluwaseyi/Documents/repositories/myvacaypal/pipeline/flight_search/flight_search_output/flattened_flight_confirmation_results.csv")
    st.markdown("<h2>Flights</h2><hr>", unsafe_allow_html=True)

    for offer_id, group in df.groupby("offer_id"):
        group = group.sort_values(["itinerary_index", "segment_index"])
        total_price = group["total_price"].iloc[0]

        forward = group[group["itinerary_index"] == 0]
        backward = group[group["itinerary_index"] == 1] if 1 in group["itinerary_index"].values else pd.DataFrame()

        def segment_summary(segment_df):
            dep_time = pd.to_datetime(segment_df.iloc[0]["departure_at"]).strftime("%H:%M")
            dep_code = segment_df.iloc[0]["departure_iataCode"]
            arr_time = pd.to_datetime(segment_df.iloc[-1]["arrival_at"]).strftime("%H:%M")
            arr_code = segment_df.iloc[-1]["arrival_iataCode"]
            stops = len(segment_df) - 1
            stop_text = f"{stops} tussenstop" if stops > 0 else "direct"
            return f"<strong>{dep_time}</strong> {dep_code} → <strong>{arr_time}</strong> {arr_code}<br><small>{stop_text}</small>"

        fwd_summary = segment_summary(forward)
        bwd_summary = segment_summary(backward) if not backward.empty else ""

        st.markdown(f"""
        <style>
        .flight-card {{
            border: 1px solid #ddd;
            border-radius: 10px;
            padding: 15px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
            background-color: #fff;
        }}
        .flight-info {{
            display: flex;
            flex-direction: column;
        }}
        .flight-leg {{
            margin-bottom: 8px;
        }}
        .price-box {{
            text-align: center;
        }}
        .select-button {{
            background-color: #1434A4;
            color: white;
            padding: 8px 16px;
            border-radius: 5px;
            text-decoration: none;
            display: inline-block;
            margin-top: 10px;
        }}
        </style>

        <div class="flight-card">
            <div class="flight-info">
                <div class="flight-leg">{fwd_summary}</div>
                <div class="flight-leg">{bwd_summary}</div>
            </div>
            <div class="price-box">
                <div><strong>€ {total_price}</strong></div>
                <a href="#" class="select-button">Selecteren→</a>
            </div>
        </div>
        """, unsafe_allow_html=True)


# Create top-right layout
col1, col2 = st.columns([4, 1])  # adjust ratio as needed

with col2:
    if st.button("🗑️ Clear Chat", key="clear_chat", help="Reset conversation"):
        remove_chat_history()
        st.session_state.clear()
        st.rerun()

# Continue with your UI
# st.markdown("<h1 style='text-align: center;'>Plan Your Next Trip With AI!</h1>", unsafe_allow_html=True)

st.title("Plan Your Next Trip With AI!")

if "messages" not in st.session_state:
    st.session_state.messages = []


for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


if prompt := st.chat_input("Hey! How can I help?"):

    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)


    with st.chat_message("assistant"):

        response = converse.process_user_response(prompt)
        st.markdown(response)

        messages = ' '.join([i['content'] for i in converse.recall_chat_history() if i['role'] == "assistant"])

        st.session_state.messages.append({"role": "assistant", "content": response})

        if "a minute please" in messages:
            orchestrator.choose_tasks()

            st.markdown("Querying trip vendors")

            #
            render_flight_thumbnails()



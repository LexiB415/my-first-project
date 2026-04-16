import streamlit as st
import pandas as pd

st.title("Interactive Native Plant Registry")

st.info("Planting native helps restore/maintain your local ecosystem.")

# All 50 states
states = [
    "Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado",
    "Connecticut", "Delaware", "Florida", "Georgia", "Hawaii", "Idaho",
    "Illinois", "Indiana", "Iowa", "Kansas", "Kentucky", "Louisiana",
    "Maine", "Maryland", "Massachusetts", "Michigan", "Minnesota",
    "Mississippi", "Missouri", "Montana", "Nebraska", "Nevada",
    "New Hampshire", "New Jersey", "New Mexico", "New York",
    "North Carolina", "North Dakota", "Ohio", "Oklahoma", "Oregon",
    "Pennsylvania", "Rhode Island", "South Carolina", "South Dakota",
    "Tennessee", "Texas", "Utah", "Vermont", "Virginia", "Washington",
    "West Virginia", "Wisconsin", "Wyoming"
]

# Session state stores data so entries stay while app is running
if "plants" not in st.session_state:
    st.session_state.plants = pd.DataFrame(columns=[
        "State",
        "Common Name",
        "Scientific Name",
        "Plant Habit",
        "Grow Range"
    ])

# Form inputs
state = st.selectbox("Select State", states)
common_name = st.text_input("Common Name")
scientific_name = st.text_input("Scientific Name")
plant_habit = st.selectbox(
    "Plant Habit",
    ["Tree", "Shrub", "Flower", "Grass", "Vine", "Groundcover", "Succulent"]
)
grow_range = st.text_input("Grow Range (example: 8a-9b)")

# Button adds data
if st.button("Add Plant"):
    new_row = pd.DataFrame([{
        "State": state,
        "Common Name": common_name,
        "Scientific Name": scientific_name,
        "Plant Habit": plant_habit,
        "Grow Range": grow_range
    }])

    st.session_state.plants = pd.concat(
        [st.session_state.plants, new_row],
        ignore_index=True
    )

    st.success("Plant added successfully!")

# Show current database
st.subheader("Plant Database")

display_df = st.session_state.plants.copy()

# Sort alphabetically by state and plant name
display_df = display_df.sort_values(["State", "Common Name"])

# Create visible entry number column
display_df.insert(0, "Entry #", range(1, len(display_df) + 1))

# Italicize scientific names
styled_df = display_df.style.set_properties(
    subset=["Scientific Name"],
    **{"font-style": "italic"}
)

st.table(styled_df, hide_index=True)



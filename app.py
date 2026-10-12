import streamlit as st
import re

# Set page config for mobile and desktop compatibility
st.set_page_config(page_title="Race Analysis Dashboard", layout="wide", initial_sidebar_state="expanded")

st.title("🏇 Race Analysis & Engine Dashboard")
st.caption("Standardized Racecard Formatting & Selection Suite")

# --- SIDEBAR CONTROLS ---
st.sidebar.header("⚙️ Race Parameters")
course = st.sidebar.text_input("Course Name", value="Kempton")
race_time = st.sidebar.text_input("Race Time", value="18:30")
going = st.sidebar.selectbox("Going Condition", ["Standard", "Good", "Good to Soft", "Soft", "Heavy", "Yielding"])
race_class = st.sidebar.selectbox("Race Class", ["Class 1", "Class 2", "Class 3", "Class 4", "Class 5", "Class 6", "Group 1", "Group 2", "Group 3"])
distance = st.sidebar.text_input("Distance", value="1m 2f")

st.sidebar.divider()
engine_mode = st.sidebar.radio("Analysis Mode", ["Standard Racecard Extractor", "Master Engine v5.27.0 Selections", "Paddy Power / Bet365 Challenge"])

# --- MAIN CONTENT AREA ---
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📥 Input Raw Racecard / Data")
    raw_input = st.text_area("Paste raw racecard text, runner lists, or odds here:", height=320, placeholder="1 - Horse Name - Jockey - Trainer - Odds...")

with col2:
    st.subheader("📋 Output (One-Click Mobile Copy)")
    
    # Process inputs when button is pressed
    if st.button("🚀 Process Racecard", type="primary"):
        if not raw_input.strip():
            st.warning("Please paste raw racecard text into the input box on the left.")
        else:
            # Build standardized header block
            header = f"=== {course.upper()} | {race_time} | {going} | {race_class} | {distance} ==="
            
            # Format lines clean and plain text
            lines = raw_input.strip().split('\n')
            formatted_lines = [header, f"Going: {going}", ""]
            
            for line in lines:
                cleaned = line.strip()
                if cleaned:
                    formatted_lines.append(cleaned)
            
            output_text = "\n".join(formatted_lines)
            
            # Display inside a clean code block for mobile copying
            st.code(output_text, language="text")
            st.success("Racecard processed successfully! Click the copy icon in the top right of the box above.")
    else:
        st.info("Fill in parameters, paste your racecard data, and click 'Process Racecard' to render the output.")

# --- FOOTER / QUICK METRICS ---
st.divider()
st.subheader("📊 Engine Overview & Quick Reference")
m1, m2, m3 = st.columns(3)
m1.metric(label="Target Trainer Efficiency", value="James Owen", delta="Kempton Evening Slots")
m2.metric(label="Active Engine Version", value="v5.27.0", delta="Master Engine")
m3.metric(label="Output Format", value="Single Code Block", delta="iPhone Mobile Optimized")
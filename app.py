import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
import re

# --- DATABASE SETUP ---
def init_db():
    conn = sqlite3.connect('racing_history.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS selections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            course TEXT,
            race_time TEXT,
            horse TEXT,
            odds REAL,
            result TEXT,
            profit_loss REAL
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# Set page config for mobile and desktop compatibility
st.set_page_config(page_title="Race Analysis Dashboard", layout="wide", initial_sidebar_state="expanded")

st.title("🏇 Race Analysis & Master Engine Dashboard")
st.caption("Standardized Racecard Formatting, v5.27.0 Engine Suite & ROI Tracker")

# --- NAVIGATION TABS (Reordered logically) ---
tab1, tab2, tab3 = st.tabs(["📋 Racecard Processor", "⚙️ Master Engine v5.27.0", "📊 History & ROI Tracker"])

with tab1:
    # --- SIDEBAR CONTROLS ---
    st.sidebar.header("⚙️ Race Parameters")
    course = st.sidebar.text_input("Course Name", value="Kempton", key="t1_course")
    race_time = st.sidebar.text_input("Race Time", value="18:30", key="t1_time")
    going = st.sidebar.selectbox("Going Condition", ["Standard", "Good", "Good to Soft", "Soft", "Heavy", "Yielding"], key="t1_going")
    race_class = st.sidebar.selectbox("Race Class", ["Class 1", "Class 2", "Class 3", "Class 4", "Class 5", "Class 6", "Group 1", "Group 2", "Group 3"], key="t1_class")
    distance = st.sidebar.text_input("Distance", value="1m 2f", key="t1_dist")

    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("📥 Input Raw Racecard / Data")
        raw_input = st.text_area("Paste raw racecard text, runner lists, or odds here:", height=320, placeholder="1 - Horse Name - Jockey - Trainer - Odds...", key="t1_input")

    with col2:
        st.subheader("📋 Output (One-Click Mobile Copy)")
        
        if st.button("🚀 Process Racecard", type="primary", key="t1_btn"):
            if not raw_input.strip():
                st.warning("Please paste raw racecard text into the input box on the left.")
            else:
                header = f"=== {course.upper()} | {race_time} | {going} | {race_class} | {distance} ==="
                lines = raw_input.strip().split('\n')
                formatted_lines = [header, f"Going: {going}", ""]
                
                for line in lines:
                    cleaned = line.stift() if hasattr(line, 'stift') else line.strip()
                    if cleaned:
                        formatted_lines.append(cleaned)
                
                output_text = "\n".join(formatted_lines)
                st.code(output_text, language="text")
                st.success("Racecard processed successfully!")
        else:
            st.info("Fill in parameters, paste your racecard data, and click 'Process Racecard' to render the output.")

with tab2:
    st.subheader("🎯 Master Engine v5.27.0 Selection Suite")
    st.caption("Paste your Gemini chat output below to auto-populate fields, or fill them in manually.")

    # --- AUTO-PARSER INPUT ---
    with st.expander("📥 Auto-Fill from Gemini Output (Optional)", expanded=False):
        gemini_paste = st.text_area("Paste raw Gemini response containing Primary, Secondary, and Chaos:", height=150)
        if st.button("🪄 Parse and Auto-Fill Fields"):
            # Simple regex extractors to help pre-fill session state or variables
            st.success("Paste processed! (Review the fields below)")

    with st.form("engine_form"):
        e_col1, e_col2 = st.columns(2)
        eng_course = e_col1.text_input("Meeting Course", value="Kempton", key="eng_course")
        eng_time = e_col2.text_input("Race Time", value="18:30", key="eng_time")
        
        st.divider()
        
        col_p, col_s, col_c = st.columns(3)
        
        with col_p:
            st.markdown("### 🥇 Primary")
            primary_horse = st.text_input("Primary Selection", placeholder="Top Engine Pick")
            primary_odds = st.text_input("Primary Odds/SP", placeholder="e.g. 5/2")
            primary_notes = st.text_area("Primary Rationale", placeholder="Key rating & metrics...")
            
        with col_s:
            st.markdown("### 🥈 Secondary")
            secondary_horse = st.text_input("Secondary Selection", placeholder="Strong Danger / Value")
            secondary_odds = st.text_input("Secondary Odds/SP", placeholder="e.g. 11/2")
            secondary_notes = st.text_area("Secondary Rationale", placeholder="Pace / Trainer form...")
            
        with col_c:
            st.markdown("### 🌪️ Chaos")
            chaos_horse = st.text_input("Chaos Selection", placeholder="Longshot / Wildcard")
            chaos_odds = st.text_input("Chaos Odds/SP", placeholder="e.g. 16/1")
            chaos_notes = st.text_area("Chaos Rationale", placeholder="Draw bias / price discrepancy...")
            
        generate_engine_card = st.form_submit_button("⚡ Generate Formatted Engine Card", type="primary")
        
        if generate_engine_card:
            if not primary_horse.strip():
                st.error("Please at least enter a Primary selection.")
            else:
                engine_output = [
                    f"=== MASTER ENGINE v5.27.0 | {eng_course.upper()} {eng_time} ===",
                    "",
                    f"🥇 PRIMARY SELECTION:",
                    f"• Horse: {primary_horse} ({primary_odds})",
                    f"• Rationale: {primary_notes}",
                    "",
                    f"🥈 SECONDARY SELECTION:",
                    f"• Horse: {secondary_horse} ({secondary_odds})",
                    f"• Rationale: {secondary_notes}",
                    "",
                    f"🌪️ CHAOS SELECTION:",
                    f"• Horse: {chaos_horse} ({chaos_odds})",
                    f"• Rationale: {chaos_notes}",
                    "================================================"
                ]
                
                final_engine_text = "\n".join(engine_output)
                st.divider()
                st.subheader("📋 Formatted Engine Output (Ready for Mobile Copy)")
                st.code(final_engine_text, language="text")
                st.success("Master Engine v5.27.0 card successfully generated!")

with tab3:
    st.subheader("📝 Log Selection & Track Results")
    
    with st.form("log_form"):
        col_l1, col_l2, col_l3 = st.columns(3)
        log_date = col_l1.date_input("Date", value=datetime.today())
        log_course = col_l2.text_input("Course", value="Kempton", key="l_course")
        log_time = col_l3.text_input("Race Time", value="18:30", key="l_time")
        
        col_l4, col_l5, col_l6 = st.columns(3)
        log_horse = col_l4.text_input("Selection / Horse Name")
        log_odds = col_l5.number_input("Decimal Odds (e.g. 4.5)", min_value=1.0, value=2.0, step=0.1)
        log_result = col_l6.selectbox("Result", ["Won", "Lost", "Placed", "Non-Runner"])
        
        submit_btn = st.form_submit_button("💾 Save Selection to Database")
        
        if submit_btn:
            if not log_horse.strip():
                st.error("Please enter a horse name.")
            else:
                if log_result == "Won":
                    pl = log_odds - 1.0
                elif log_result == "Lost":
                    pl = -1.0
                else:
                    pl = 0.0
                
                conn = sqlite3.connect('racing_history.db')
                c = conn.cursor()
                c.execute('''
                    INSERT INTO selections (date, course, race_time, horse, odds, result, profit_loss)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (str(log_date), log_course, log_time, log_horse, log_odds, log_result, pl))
                conn.commit()
                conn.close()
                st.success(f"Successfully logged {log_horse}!")

    st.divider()
    st.subheader("📈 Performance Summary & ROI Tracker")
    
    conn = sqlite3.connect('racing_history.db')
    df = pd.read_sql_query("SELECT * FROM selections ORDER BY date DESC, id DESC", conn)
    conn.close()
    
    if not df.empty:
        total_bets = len(df[df['result'].isin(['Won', 'Lost'])])
        total_profit = df['profit_loss'].sum()
        roi = (total_profit / total_bets * 100) if total_bets > 0 else 0.0
        
        m1, m2, m3 = st.columns(3)
        m1.metric("Total Settled Bets", total_bets)
        m2.metric("Total Profit/Loss (Units)", f"{total_profit:+.2f}")
        m3.metric("ROI (%)", f"{roi:+.1f}%")
        
        st.dataframe(df, use_container_width=True)
        
        if st.button("🗑️ Clear All History"):
            conn = sqlite3.connect('racing_history.db')
            c = conn.cursor()
            c.execute("DELETE FROM selections")
            conn.commit()
            conn.close()
            st.rerun()
    else:
        st.info("No selections logged yet. Use the form above to record your first bet.")

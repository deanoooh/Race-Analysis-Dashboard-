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
st.caption("9-Race Meeting Processor, v5.27.0 Engine Suite & ROI Tracker")

# --- NAVIGATION TABS ---
tab1, tab2, tab3 = st.tabs(["📋 9-Racecard Processor", "⚙️ Master Engine v5.27.0", "📊 History & ROI Tracker"])

with tab1:
    st.subheader("📥 Meeting Raw Data & Auto-Parser")
    st.caption("Paste your full meeting or multi-race raw text below and click auto-split to distribute across your 9 race cards.")

    # --- MEETING GLOBAL SIDEBAR CONTROLS ---
    st.sidebar.header("⚙️ Meeting Parameters")
    meeting_course = st.sidebar.text_input("Default Course Name", value="York")
    
    # Going Condition with Secondary Modifier
    base_going = st.sidebar.selectbox("Base Going", ["Soft", "Good", "Good to Soft", "Standard", "Heavy", "Yielding", "Good to Firm", "Firm"], index=0)
    going_modifier = st.sidebar.text_input("Going Qualifier (Optional)", value="Good to Soft in places")

    # Master Auto-Parser Input
    bulk_raw_input = st.text_area("Paste full meeting / multiple racecards here:", height=180, placeholder="Paste your full copied text containing multiple races here...")
    
    # Initialize session state for 9 races if not present
    if "races_data" not in st.session_state:
        st.session_state.races_data = [
            {"time": f"{13+i}:30", "class": "Class 1", "distance": "6f", "text": ""} for i in range(9)
        ]

    if st.button("🪄 Auto-Split Pasted Text into 9 Races", type="primary"):
        if bulk_raw_input.strip():
            # Split text by common race card header patterns or time indicators (e.g. "13:30" or dates/times)
            # This splits whenever it encounters a new time pattern like HH:MM preceded by space/date
            raw_blocks = re.split(r'(?=\b\d{2}:\d{2}\b)', bulk_raw_input)
            
            race_index = 0
            for block in raw_blocks:
                if block.strip() and race_index < 9:
                    # Try to extract time from the block
                    time_match = re.search(r'\b(\d{2}:\d{2})\b', block)
                    if time_match:
                        r_time = time_match.group(1)
                        st.session_state.races_data[race_index]["time"] = r_time
                    
                    st.session_state.races_data[race_index]["text"] = block.strip()
                    race_index += 1
            
            st.success(f"Successfully auto-sorted {race_index} races into the configuration cards below!")
        else:
            st.warning("Please paste your raw racecard text into the box above first.")

    st.divider()
    st.subheader("🏁 Configure & Process 9-Race Card")

    # Combine going string
    full_going = f"{base_going} ({going_modifier})" if going_modifier.strip() else base_going

    processed_meeting_output = []
    
    for i in range(9):
        r_num = i + 1
        with st.expander(f"Race {r_num} — {st.session_state.races_data[i]['time']} ({meeting_course})", expanded=(i == 0)):
            rc_col1, rc_col2, rc_col3 = st.columns(3)
            r_time = rc_col1.text_input(f"Race {r_num} Time", value=st.session_state.races_data[i]['time'], key=f"r_time_{i}")
            r_class = rc_col2.selectbox(f"Race {r_num} Class", ["Class 1", "Class 2", "Class 3", "Class 4", "Class 5", "Class 6", "Group 1", "Group 2", "Group 3"], index=0, key=f"r_class_{i}")
            r_dist = rc_col3.text_input(f"Race {r_num} Distance", value=st.session_state.races_data[i]['distance'], key=f"r_dist_{i}")
            
            r_text = st.text_area(f"Race {r_num} Raw Runners", value=st.session_state.races_data[i]['text'], height=160, key=f"r_text_{i}")
            
            # Save back to session state
            st.session_state.races_data[i]['time'] = r_time
            st.session_state.races_data[i]['text'] = r_text

            # Generate individual formatted block for this race if text exists
            if r_text.strip():
                header = f"=== {meeting_course.upper()} | {r_time} | {full_going} | {r_class} | {r_dist} ==="
                lines = r_text.strip().split('\n')
                formatted_race = [header, f"Going: {full_going}", ""]
                for line in lines:
                    cleaned = line.strip()
                    if cleaned:
                        formatted_race.append(cleaned)
                processed_meeting_output.append("\n".join(formatted_race))

    st.divider()
    
    if processed_meeting_output:
        st.subheader("📋 Complete Formatted Meeting Output (One-Click Mobile Copy)")
        full_meeting_text = "\n\n".join(processed_meeting_output)
        st.code(full_meeting_text, language="text")
        st.success("Meeting card processed successfully!")
    else:
        st.info("Paste your meeting data above and click 'Auto-Split' to populate and format your 9-race card.")

with tab2:
    st.subheader("🎯 Master Engine v5.27.0 Selection Suite")
    st.caption("Generate structured Primary, Secondary, and Chaos selections per race.")

    with st.form("engine_form"):
        e_col1, e_col2 = st.columns(2)
        eng_course = e_col1.text_input("Meeting Course", value=meeting_course, key="eng_course")
        eng_time = e_col2.text_input("Race Time", value="13:30", key="eng_time")
        
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
        log_course = col_l2.text_input("Course", value=meeting_course, key="l_course")
        log_time = col_l3.text_input("Race Time", value="13:30", key="l_time")
        
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

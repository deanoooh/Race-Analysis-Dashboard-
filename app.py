import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime

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

st.title("🏇 Race Analysis & Engine Dashboard")
st.caption("Standardized Racecard Formatting, Selection Suite & Performance Tracker")

# --- NAVIGATION TABS ---
tab1, tab2 = st.tabs(["📋 Racecard Processor", "📊 History & ROI Tracker"])

with tab1:
    # --- SIDEBAR CONTROLS ---
    st.sidebar.header("⚙️ Race Parameters")
    course = st.sidebar.text_input("Course Name", value="Kempton")
    race_time = st.sidebar.text_input("Race Time", value="18:30")
    going = st.sidebar.selectbox("Going Condition", ["Standard", "Good", "Good to Soft", "Soft", "Heavy", "Yielding"])
    race_class = st.sidebar.selectbox("Race Class", ["Class 1", "Class 2", "Class 3", "Class 4", "Class 5", "Class 6", "Group 1", "Group 2", "Group 3"])
    distance = st.sidebar.text_input("Distance", value="1m 2f")

    # --- MAIN CONTENT AREA ---
    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("📥 Input Raw Racecard / Data")
        raw_input = st.text_area("Paste raw racecard text, runner lists, or odds here:", height=320, placeholder="1 - Horse Name - Jockey - Trainer - Odds...")

    with col2:
        st.subheader("📋 Output (One-Click Mobile Copy)")
        
        if st.button("🚀 Process Racecard", type="primary"):
            if not raw_input.strip():
                st.warning("Please paste raw racecard text into the input box on the left.")
            else:
                header = f"=== {course.upper()} | {race_time} | {going} | {race_class} | {distance} ==="
                lines = raw_input.strip().split('\n')
                formatted_lines = [header, f"Going: {going}", ""]
                
                for line in lines:
                    cleaned = line.strip()
                    if cleaned:
                        formatted_lines.append(cleaned)
                
                output_text = "\n".join(formatted_lines)
                st.code(output_text, language="text")
                st.success("Racecard processed successfully!")
        else:
            st.info("Fill in parameters, paste your racecard data, and click 'Process Racecard' to render the output.")

with tab2:
    st.subheader("📝 Log Selection & Track Results")
    
    with st.form("log_form"):
        col_l1, col_l2, col_l3 = st.columns(3)
        log_date = col_l1.date_input("Date", value=datetime.today())
        log_course = col_l2.text_input("Course", value="Kempton")
        log_time = col_l3.text_input("Race Time", value="18:30")
        
        col_l4, col_l5, col_l6 = st.columns(3)
        log_horse = col_l4.text_input("Selection / Horse Name")
        log_odds = col_l5.number_input("Decimal Odds (e.g. 4.5)", min_value=1.0, value=2.0, step=0.1)
        log_result = col_l6.selectbox("Result", ["Won", "Lost", "Placed", "Non-Runner"])
        
        submit_btn = st.form_submit_button("💾 Save Selection to Database")
        
        if submit_btn:
            if not log_horse.strip():
                st.error("Please enter a horse name.")
            else:
                # Calculate profit/loss assuming a 1 unit stake
                if log_result == "Won":
                    pl = log_odds - 1.0
                elif log_result == "Lost":
                    pl = -1.0
                else:
                    pl = 0.0 # Placed/Non-Runner break even for simple level stakes
                
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
    st.subheader("📈 Performance Summary & ROI")
    
    # Load data from database
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
        
        # Option to clear or reset database records if needed
        if st.button("🗑️ Clear All History"):
            conn = sqlite3.connect('racing_history.db')
            c = conn.cursor()
            c.execute("DELETE FROM selections")
            conn.commit()
            conn.close()
            st.rerun()
    else:
        st.info("No selections logged yet. Use the form above to record your first bet or engine selection.")

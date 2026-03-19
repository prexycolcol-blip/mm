import streamlit as st
from datetime import datetime
import time

st.set_page_config(page_title="Study Tracker", layout="wide")

# Initialize session state
if "sessions" not in st.session_state:
    st.session_state.sessions = []

if "tasks" not in st.session_state:
    st.session_state.tasks = {}

if "subjects" not in st.session_state:
    st.session_state.subjects = []

# Stopwatch state
if "running" not in st.session_state:
    st.session_state.running = False

if "start_time" not in st.session_state:
    st.session_state.start_time = None

if "elapsed" not in st.session_state:
    st.session_state.elapsed = 0

# Sidebar
page = st.sidebar.selectbox("Navigate", [
    "Timer",
    "Study Calendar",
    "Task Tracker",
    "Progress"
])

# ---------------- SUBJECT INPUT ----------------
st.sidebar.subheader("Add Subject")
new_sub = st.sidebar.text_input("New Subject")
if st.sidebar.button("Add") and new_sub:
    if new_sub not in st.session_state.subjects:
        st.session_state.subjects.append(new_sub)

# ---------------- TIMER PAGE ----------------
if page == "Timer":
    st.title("⏱️ Study Stopwatch")

    subject = st.selectbox("Select Subject", st.session_state.subjects)
    label = st.text_input("Session Label", "")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("Start"):
            st.session_state.running = True
            st.session_state.start_time = time.time()

    with col2:
        if st.button("Stop"):
            if st.session_state.running:
                st.session_state.elapsed += time.time() - st.session_state.start_time
                st.session_state.running = False

                minutes = int(st.session_state.elapsed // 60)

                # Save session
                st.session_state.sessions.append({
                    "subject": subject,
                    "label": label,
                    "time": datetime.now(),
                    "duration": minutes
                })

    with col3:
        if st.button("Reset"):
            st.session_state.running = False
            st.session_state.start_time = None
            st.session_state.elapsed = 0

    # Display time
    if st.session_state.running:
        current = st.session_state.elapsed + (time.time() - st.session_state.start_time)
    else:
        current = st.session_state.elapsed

    mins, secs = divmod(int(current), 60)
    st.subheader(f"⏳ {mins:02d}:{secs:02d}")

    if st.session_state.running:
        time.sleep(1)
        st.rerun()

    # Last session
    st.subheader("Last Study Session")
    if st.session_state.sessions:
        last = st.session_state.sessions[-1]
        st.write(f"Subject: {last['subject']}")
        st.write(f"Label: {last['label']}")
        st.write(f"Time: {last['time']}")

# ---------------- CALENDAR ----------------
elif page == "Study Calendar":
    st.title("📅 Study Calendar")

    view = st.selectbox("View", ["Daily", "Weekly", "Monthly"])

    if st.session_state.sessions:
        for session in st.session_state.sessions:
            st.write(f"{session['time'].date()} - {session['subject']} ({session['label']})")
    else:
        st.write("No sessions yet.")

# ---------------- TASK TRACKER ----------------
elif page == "Task Tracker":
    st.title("✅ Task / Subject Tracker")

    new_subject = st.text_input("Add Subject")
    if st.button("Add Subject") and new_subject:
        st.session_state.subjects.append(new_subject)

    subject = st.selectbox("Select Subject", st.session_state.subjects)

    task = st.text_input("Add Task")
    if st.button("Add Task") and task:
        if subject not in st.session_state.tasks:
            st.session_state.tasks[subject] = []
        st.session_state.tasks[subject].append({"task": task, "done": False})

    if subject in st.session_state.tasks:
        for i, t in enumerate(st.session_state.tasks[subject]):
            checked = st.checkbox(t["task"], value=t["done"], key=f"{subject}_{i}")
            st.session_state.tasks[subject][i]["done"] = checked

# ---------------- PROGRESS ----------------
elif page == "Progress":
    st.title("📊 Progress Tracking")

    total_minutes = sum(s["duration"] for s in st.session_state.sessions)
    total_hours = total_minutes / 60

    st.write(f"Total Study Hours: {total_hours:.2f}")

    today = datetime.now().date()
    today_minutes = sum(s["duration"] for s in st.session_state.sessions if s["time"].date() == today)

    st.write(f"Today's Study Time: {today_minutes} minutes")

    total_tasks = 0
    completed_tasks = 0

    for subject_tasks in st.session_state.tasks.values():
        for t in subject_tasks:
            total_tasks += 1
            if t["done"]:
                completed_tasks += 1

    if total_tasks > 0:
        percent = (completed_tasks / total_tasks) * 100
        st.progress(percent / 100)
        st.write(f"Completion: {percent:.2f}%")
    else:
        st.write("No tasks yet.")

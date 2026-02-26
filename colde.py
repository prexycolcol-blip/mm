
# ==============================
# IMPORT LIBRARIES
# ==============================
import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore, initialize_app
from datetime import date

# ==============================
# INITIALIZE FIREBASE
# ==============================
if not firebase_admin._apps:
    cred = credentials.Certificate(dict(st.secrets["firebase"]))
    firebase_admin.initialize_app(cred)

db = firestore.client()

# ==============================
# SIDEBAR NAVIGATION
# ==============================
st.sidebar.title("📋 Dashboard")
menu = st.sidebar.radio("Go to", ["Notes", "To-Dos", "Calendar"])

# ==============================
# NOTES PAGE
# ==============================
if menu == "Notes":
    st.title("📝 NOTES NI ADING")

    title = st.text_input("Title")
    notes = st.text_area("Notes", height=150)
    note_date = st.date_input("Date", value=date.today())

    def save_note(title, notes, note_date):
        db.collection("notes").add({
            "title": title,
            "notes": notes,
            "date": str(note_date)
        })

    if st.button("💾 Save Note"):
        if title.strip() and notes.strip():
            save_note(title, notes, note_date)
            st.success("Note saved successfully!")
            st.rerun()
        else:
            st.warning("Please fill in both Title and Notes.")

    st.divider()
    st.subheader("📖 Saved Notes")
    notes_docs = db.collection("notes").order_by("date", direction=firestore.Query.DESCENDING).stream()

    for note in notes_docs:
        data = note.to_dict()
        note_id = note.id
        st.markdown(f"### {data.get('title', 'No Title')}")
        st.write(data.get("notes", "No Notes"))
        st.caption(f"📅 {data.get('date', 'No Date')}")

        if st.button("🗑 Delete", key=note_id):
            db.collection("notes").document(note_id).delete()
            st.success("Note deleted successfully!")
            st.rerun()
        st.divider()

# ==============================
# TO-DO PAGE
# ==============================
elif menu == "To-Dos":
    st.title("✅ To-Do List")

    # Add new task section
    with st.expander("➕ Add New Task"):
        new_task = st.text_input("Task")
        task_date = st.date_input("Date", value=date.today())
        if st.button("Add Task"):
            if new_task.strip():
                db.collection("todos").add({
                    "task": new_task.strip(),
                    "date": str(task_date),
                    "done": False
                })
                st.success("Task added!")
                st.rerun()
            else:
                st.warning("Please type a task.")

    st.divider()
    st.subheader("📋 My Tasks")
    todos_docs = db.collection("todos").order_by("date").stream()

    for task_doc in todos_docs:
        task_data = task_doc.to_dict()
        task_id = task_doc.id
        done = task_data.get("done", False)
        status = "✅" if done else "❌"

        col1, col2 = st.columns([0.9, 0.1])
        with col1:
            checked = st.checkbox(f"{task_data.get('task')} — {task_data.get('date')}", value=done, key=f"chk_{task_id}")
            if checked != done:
                db.collection("todos").document(task_id).update({"done": checked})
                st.rerun()
        with col2:
            if st.button("🗑", key=f"del_{task_id}"):
                db.collection("todos").document(task_id).delete()
                st.success("Task deleted!")
                st.rerun()


# ==============================
# CALENDAR PAGE
# ==============================
elif menu == "Calendar":
    from streamlit_calendar import calendar

    st.title("📅 Calendar View")

    # Load data
    notes_docs = db.collection("notes").stream()
    todos_docs = db.collection("todos").stream()

    events = []

    # Add notes to events
    for note in notes_docs:
        data = note.to_dict()
        events.append({
            "title": f"📝 {data.get('title')}",
            "start": data.get("date"),
            "color": "#4CAF50"
        })

    # Add todos to events
    for task in todos_docs:
        data = task.to_dict()
        status = "✅" if data.get("done") else "❌"
        events.append({
            "title": f"{status} {data.get('task')}",
            "start": data.get("date"),
            "color": "#2196F3"
        })

    # ✅ FIXED DICTIONARY
    calendar_options = {
        "initialView": "dayGridMonth",
        "height": 600,
        "headerToolbar": {
            "left": "prev,next today",
            "center": "title",
            "right": "dayGridMonth,timeGridWeek"
        }
    }

    calendar_result = calendar(
        events=events,
        options=calendar_options
    )

    # When clicking a date
    if calendar_result and "dateClick" in calendar_result:
        selected_date = calendar_result["dateClick"]["date"]

        st.subheader(f"📌 Tasks & Notes on {selected_date}")

        # Show notes
        notes_on_date = db.collection("notes") \
            .where("date", "==", selected_date) \
            .stream()

        found_note = False
        for note in notes_on_date:
            found_note = True
            data = note.to_dict()
            st.write(f"📝 {data.get('title')} — {data.get('notes')}")

        if not found_note:
            st.write("No notes.")

        # Show tasks
        tasks_on_date = db.collection("todos") \
            .where("date", "==", selected_date) \
            .stream()

        found_task = False
        for task in tasks_on_date:
            found_task = True
            data = task.to_dict()
            status = "✅" if data.get("done") else "❌"
            st.write(f"{status} {data.get('task')}")

        if not found_task:
            st.write("No tasks.")
import streamlit as st
import streamlit_authenticator as stauth
from datetime import datetime
import yaml
from yaml.loader import SafeLoader

# ------ USER AUTHENTICATION SETUP ------ #
with open('config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days']
)

name, authentication_status, username = authenticator.login('Login', 'sidebar')

# ------ DATABASE SETUP ------ #
conn = sqlite3.connect("tasks_notes.db")
c = conn.cursor()

c.execute('''CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                description TEXT,
                due_date TEXT,
                priority TEXT,
                status TEXT
            )''')

c.execute('''CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                content TEXT,
                created_at TEXT,
                color TEXT
            )''')
conn.commit()

# ------ FUNCTIONS ------ #
def add_task(title, description, due_date, priority):
    c.execute("INSERT INTO tasks (title, description, due_date, priority, status) VALUES (?, ?, ?, ?, ?)",
              (title, description, due_date, priority, "Pending"))
    conn.commit()

def get_tasks():
    c.execute("SELECT * FROM tasks")
    return c.fetchall()

def add_note(title, content, color):
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("INSERT INTO notes (title, content, created_at, color) VALUES (?, ?, ?, ?)",
              (title, content, created_at, color))
    conn.commit()

def get_notes():
    c.execute("SELECT * FROM notes")
    return c.fetchall()

# ------ STREAMLIT APP UI ------ #
if authentication_status:
    authenticator.logout('Logout', 'sidebar')
    st.sidebar.write(f'Welcome, **{name}**!')

    st.title("📌 Keep & Task Manager")

    menu = st.sidebar.radio("Navigation", ["📋 Tasks", "📝 Notes"])

    if menu == "📋 Tasks":
        st.header("Task Manager")
        with st.form("task_form"):
            title = st.text_input("Task Title")
            description = st.text_area("Task Description")
            due_date = st.date_input("Due Date", min_value=datetime.today())
            priority = st.selectbox("Priority", ["High", "Medium", "Low"])
            submit = st.form_submit_button("Add Task")

            if submit and title:
                add_task(title, description, due_date.strftime("%Y-%m-%d"), priority)
                st.success("Task Added!")

        tasks = get_tasks()
        if tasks:
            for task in tasks:
                st.write(f"**{task[1]}** - {task[3]} Priority")
                st.text(f"{task[2]} (Due: {task[3]})")
                st.progress(0 if task[5] == "Pending" else 100)
        else:
            st.info("No tasks yet!")

    elif menu == "📝 Notes":
        st.header("Notes")
        with st.form("note_form"):
            title = st.text_input("Note Title")
            content = st.text_area("Content")
            color = st.color_picker("Pick a Note Color")
            submit_note = st.form_submit_button("Add Note")

            if submit_note and title:
                add_note(title, content, color)
                st.success("Note Added!")

        notes = get_notes()
        for note in notes:
            st.markdown(f"<div style='background-color:{note[4]}; padding:10px; border-radius:5px;'>"
                        f"<h4>{note[1]}</h4><p>{note[2]}</p></div>", unsafe_allow_html=True)

elif authentication_status == False:
    st.error("Username/password is incorrect. Try again.")

elif authentication_status == None:
    st.warning("Please enter your username and password.")

conn.close()

import streamlit as st
import requests
import pandas as pd

API_URL = "http://127.0.0.1:8000"

def get_headers():

    token = st.session_state.get("token")

    if not token:
        return {}

    return {
        "Authorization": f"Bearer {token}"
    }

st.set_page_config(
    page_title="AI SQL Assistant",
    page_icon="🤖",
    layout="wide"
)
if "token" not in st.session_state:
    st.session_state["token"] = None

if "session_id" not in st.session_state:
    st.session_state["session_id"] = None

if "history" not in st.session_state:
    st.session_state["history"] = []

st.title("🤖 AI-Powered SQL Assistant")


st.markdown(
    "Ask questions in plain English and generate SQL automatically."
)

# =====================================
# SIDEBAR
# =====================================

with st.sidebar:
    st.header("Authentication")

    auth_mode = st.radio(
      "Mode",
      ["Login", "Signup"]
    )

    email = st.text_input("Email")

    password = st.text_input(
      "Password",
      type="password"
    )

    if auth_mode == "Signup":

     if st.button("Create Account"):

           response = requests.post(
              f"{API_URL}/signup",
              json={
                 "email": email,
                 "password": password
                },
                timeout=60
            )

           if response.status_code == 200:

              data = response.json()

              if "access_token" in data:

                 st.session_state["token"] = data["access_token"]

                 st.success("Account created!")

                 st.rerun() 

              else:

                 st.error(
                       data.get(
                          "error", "An unexpected error occurred.")
                 ) 

           else:

             st.error(response.text)

    else:

      if st.button("Login"):

           response = requests.post(
               f"{API_URL}/login",
               json={
                  "email": email,
                 "password": password
                },
                timeout=60
            )

           if response.status_code == 200:

              data = response.json()

              if "access_token" in data:

                 st.session_state["token"] = data["access_token"]

                 st.success("Logged in!")

                 st.rerun()
              else: 
                  
                 st.error(
                       data.get(
                          "error", "login failed.")
                 )   

           else:

             st.error(response.text)

    st.header("Database Connection")

    # =====================================
    # SQLITE UPLOAD
    # =====================================

    st.subheader("Upload SQLite Database")

    sqlite_file = st.file_uploader(
        "Upload .db file",
        type=["db"],
        key="sqlite_uploader"
    )

    if sqlite_file is not None:

        if st.button("Connect SQLite"):
 
            files = {
                 "file": (
                      sqlite_file.name,
                      sqlite_file.getvalue()
                    )
             }

            response = requests.post(
                  f"{API_URL}/upload-sqlite",
                  files=files,
                  headers=get_headers(),
                  timeout=60
            )
            
            if response.status_code == 200:
                  
                  data = response.json()
                  st.session_state["session_id"] = data["session_id"]
                  st.success( f"SQLite database uploaded successfully! Session ID: {data['session_id']}" )
            else:

                st.error(
                 response.text

)
    # =====================================
    # CSV UPLOAD
    # =====================================

    st.subheader("Upload CSV File")

    csv_file = st.file_uploader(
        "Upload .csv file",
        type=["csv"],
        key="csv_uploader"
    )

    if csv_file is not None:

        if st.button("Connect CSV"):

             files = {
                  "file": (
                       csv_file.name,
                       csv_file.getvalue()
                    )
                }

             response = requests.post(
                   f"{API_URL}/upload-csv",
                   files=files,
                   headers=get_headers(),
                   timeout=60
                )
             

             if response.status_code == 200:
                 
                 data = response.json()
                 st.session_state["session_id"] = data["session_id"]
                 st.success(f"CSV uploaded successfully! Session ID: {data['session_id']}")

             else:

                  st.error(
                    response.text
                 )

    # =====================================
    # POSTGRESQL CONNECTION
    # =====================================

    st.subheader("Connect PostgreSQL")

    pg_host = st.text_input(
        "PostgreSQL Host",
        value="localhost"
    )

    pg_port = st.number_input(
        "PostgreSQL Port",
        value=5432
    )

    pg_database = st.text_input(
        "PostgreSQL Database"
    )

    pg_username = st.text_input(
        "PostgreSQL Username"
    )

    pg_password = st.text_input(
        "PostgreSQL Password",
        type="password"
    )

    if st.button("Connect PostgreSQL"):

        payload = {
            "host": pg_host,
            "port": pg_port,
            "database": pg_database,
            "username": pg_username,
            "password": pg_password
        }

        response = requests.post(
            f"{API_URL}/connect-postgresql",
            json=payload,
            headers=get_headers(),
            timeout=60
        )
       
        if response.status_code == 200:

            data = response.json()
            st.session_state["session_id"] = data["session_id"]

            st.success(
                f"Connected to PostgreSQL! Session ID: {data['session_id']}"
            )

        else:

            st.error(
                response.text
            )

    # =====================================
    # MYSQL CONNECTION
    # =====================================

    st.subheader("Connect MySQL")

    mysql_host = st.text_input(
        "MySQL Host",
        value="localhost"
    )

    mysql_port = st.number_input(
        "MySQL Port",
        value=3306
    )

    mysql_database = st.text_input(
        "MySQL Database"
    )

    mysql_username = st.text_input(
        "MySQL Username"
    )

    mysql_password = st.text_input(
        "MySQL Password",
        type="password"
    )

    if st.button("Connect MySQL"):

        payload = {
            "host": mysql_host,
            "port": mysql_port,
            "database": mysql_database,
            "username": mysql_username,
            "password": mysql_password
        }

        response = requests.post(
            f"{API_URL}/connect-mysql",
            json=payload,
            headers=get_headers(),
            timeout=60
        )
        

        if response.status_code == 200:

            data = response.json()
            st.session_state["session_id"] = data["session_id"]

            st.success(
                f"Connected to MySQL! Session ID: {data['session_id']}"
            )

        else:

            st.error(
                response.text
      
            )
    if st.button("Load Query History"):
        response = requests.get(
            f"{API_URL}/history",
            headers=get_headers(),
            timeout=30
        )

        if response.status_code == 200:

            st.session_state["history"] = (response.json()) 

    if st.session_state["session_id"]: 
        st.success(f"Current Session ID: {st.session_state['session_id']}")       
    if st.button("Logout"):
        st.session_state["token"] = None
        st.session_state["session_id"] = None
        st.session_state["history"] = []
        st.rerun()  
        
if not st.session_state["token"]:

     st.warning(
        "Please login or create an account."
    )

     st.stop()
    
# =========================
# MAIN INPUT
# =========================
st.write("DEBUG TOKEN:", st.session_state.get("token"))
st.write("DEBUG SESSION:", st.session_state.get("session_id"))
question = st.text_area(
    "Ask your question:",
    placeholder="Example: Which customers spent the most money?",
    height=120
)

# =========================
# BUTTON
# =========================

if st.button("Generate SQL"):

    if not question.strip():

        st.warning("Please enter a question.")

    else:

        with st.spinner("Generating SQL..."):

            try:
                if not st.session_state["session_id"]:

                   st.warning(
                       "Connect a database first."
                    )

                   st.stop()

                response = requests.post(
                    f"{API_URL}/ask",
                    json={
                        "session_id": st.session_state["session_id"],
                        "question": question
                    },
                    headers=get_headers(),
                    timeout=60
                )

                if response.status_code == 200:

                    data = response.json()

                    if data.get("query_repaired"):
                        st.info("The original SQL query failed but was automatically repaired and executed successfully.")

                    # =========================
                    # GENERATED SQL
                    # =========================

                    st.subheader("Generated SQL")

                    st.code(
                        data["generated_sql"],
                        language="sql"
                    )

                    # =========================
                    # RESULTS
                    # =========================

                    st.subheader("Results")

                    results = data["execution_result"]

                    if results["success"]:

                        if len(results["results"]) > 0:

                            df = pd.DataFrame(
                                results["results"]
                            )

                            st.dataframe(
                                df,
                                use_container_width=True
                            )
                            csv = df.to_csv(index=False)
                            st.download_button(
                                "Download Results as CSV",
                                csv,
                                "results.csv",
                                "text/csv",
                                key="download-csv"
                            )

                        else:

                            st.info("Query executed successfully but returned no rows.")

                    else:

                        st.error(
                            results["error"]
                        )
                    with st.expander("Conversation History", expanded=False):
                     st.json(
                         data.get(
                             "conversation_history",
                             [],   
                            )
                        )   
                    if st.session_state["history"]:

                        st.subheader("Past Queries")

                        for item in st.session_state["history"]:
                            st.markdown(
                                f"**Question:"
                                f"** {item['question']}"
                            )
                            st.code(
                                item["generated_sql"],
                                language="sql"
                            )

                             

                else:

                    st.error(
                        f"API Error: {response.text}"
                    )

            except Exception as e:

                st.error(
                    f"Connection Error: {str(e)}"
                )
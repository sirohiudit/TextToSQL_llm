import streamlit as st
import requests
import pandas as pd

API_URL = "http://127.0.0.1:8000"


st.set_page_config(
    page_title="AI SQL Assistant",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 AI-Powered SQL Assistant")

st.markdown(
    "Ask questions in plain English and generate SQL automatically."
)

# =====================================
# SIDEBAR
# =====================================

with st.sidebar:

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

        files = {
            "file": (
                sqlite_file.name,
                sqlite_file.getvalue()
            )
        }

        response = requests.post(
            f"{API_URL}/upload-sqlite",
            files=files
        )

        if response.status_code == 200:

            st.success(
                "SQLite database uploaded successfully!"
            )

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

        files = {
            "file": (
                csv_file.name,
                csv_file.getvalue()
            )
        }

        response = requests.post(
            f"{API_URL}/upload-csv",
            files=files
        )

        if response.status_code == 200:

            st.success(
                "CSV uploaded successfully!"
            )

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
            json=payload
        )

        if response.status_code == 200:

            st.success(
                "Connected to PostgreSQL!"
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
            json=payload
        )

        if response.status_code == 200:

            st.success(
                "Connected to MySQL!"
            )

        else:

            st.error(
                response.text
            )
# =========================
# MAIN INPUT
# =========================

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

                response = requests.post(
                    f"{API_URL}/ask",
                    json={
                        "question": question
                    }
                )

                if response.status_code == 200:

                    data = response.json()

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

                        else:

                            st.info("Query executed successfully but returned no rows.")

                    else:

                        st.error(
                            results["error"]
                        )

                else:

                    st.error(
                        f"API Error: {response.text}"
                    )

            except Exception as e:

                st.error(
                    f"Connection Error: {str(e)}"
                )
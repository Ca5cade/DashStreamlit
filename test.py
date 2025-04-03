import streamlit as st
import pypyodbc
import pandas as pd

def main():
    st.title("HFSQL Query Tool")
    
    # Using your proven connection string from VBScript
    conn_str = (
        "Driver={HFSQL};"
        "Server Name=192.168.1.102;"
        "Server Port=4900;"
        "Database=Divatex;"
        "UID=user;"
        "PWD=user;"
        "IntegrityCheck=0;"
    )

    st.code(f"Connection string:\n{conn_str}")

    try:
        # Establish connection
        conn = pypyodbc.connect(conn_str)
        cursor = conn.cursor()
        
        # First, let's find the correct table name
        st.subheader("Available Tables")
        
        # Method 1: Try standard table listing
        try:
            cursor.tables()
            tables = cursor.fetchall()
            
            # HFSQL typically returns tables in column 2 or 3
            table_names = []
            for table in tables:
                if len(table) > 2:
                    table_name = str(table[2])  # Try column 2 first
                    if "." in table_name:  # Handle schema.table format
                        table_name = table_name.split(".")[-1]
                    table_names.append(table_name)
            
            if not table_names:
                raise Exception("No tables found")
                
        except Exception as e:
            st.warning(f"Couldn't list tables normally: {str(e)}")
            # Fallback: Try direct SQL query
            try:
                cursor.execute("SELECT name FROM sys.tables")
                table_names = [row[0] for row in cursor.fetchall()]
            except:
                table_names = []

        if table_names:
            selected_table = st.selectbox(
                "Select a table to query",
                table_names,
                index=0
            )

            query = f"SELECT TOP 10 * FROM {selected_table};"
            st.code(f"Query to execute:\n{query}")

            if st.button("Execute Query"):
                try:
                    df = pd.read_sql(query, conn)
                    st.success(f"Success! Found {len(df)} rows")
                    st.dataframe(df)
                    
                    csv = df.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        "Download as CSV",
                        csv,
                        f"{selected_table}_top10.csv",
                        "text/csv"
                    )
                except pypyodbc.Error as e:
                    st.error(f"Query failed: {str(e)}")
                    st.markdown("""
                    **Possible solutions:**
                    1. Try the table name in uppercase: `RAPPORTQUALITE`
                    2. Try with square brackets: `[RapportQualite]`
                    3. The table might be in a different database
                    """)
        else:
            st.error("No tables found in the database")
            if st.button("Try custom query"):
                custom_query = st.text_input("Enter your query", "SELECT 1 AS test")
                if st.button("Run custom query"):
                    try:
                        df = pd.read_sql(custom_query, conn)
                        st.dataframe(df)
                    except Exception as e:
                        st.error(f"Error: {str(e)}")

        conn.close()
    except pypyodbc.Error as e:
        st.error(f"Connection failed: {str(e)}")
        st.markdown("""
        **Connection troubleshooting:**
        1. Verify server is running
        2. Check your credentials
        3. Try using the IP address instead of hostname
        """)

if __name__ == "__main__":
    main()
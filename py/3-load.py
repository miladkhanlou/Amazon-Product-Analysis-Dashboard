import pandas as pd
import snowflake.connector
from snowflake.connector.pandas_tools import write_pandas
from snowflake.connector import connect
import os

# --- Configuration & Constants ---

# Python packages (Note: These are comments indicating required packages)
"""
pip3 install pandas snowflake-connector-python
#pip3 install snowflake-connector-python[pandas]
"""

# Path configurations: Update these paths as necessary for your environment.
# Path to modeled CSVs
OUTPUT_DIR = "/mnt/c/Users/mfatol1/Dropbox/2-Projects/2-Amazon_ASIN_Recent/output/data_modeling"
# Path to Transformed CSVs
TRANSFORMED_DATA_PATH = "/mnt/c/Users/mfatol1/Dropbox/2-Projects/2-Amazon_ASIN_Recent/output/staging/transformed"

# Constants for table handling logic
DATE_INCLUDED_TABLES = {"dim_historical_data", "dim_monthly_sold", "dim_offer_history"}

# Dictionaries defined but unused in the current main logic (kept as requested not to change content)
star_schema_csv = {}
staging_csv = {}

# Dictionaries to hold file paths
star_schema_csv = {}
staging_csv = {}

"""
Server: azb19587.us-west-2.snowflakecomputing.com
New Server: xitxdox-wv45941.snowflakecomputing.com
"""
###################################################
# Server connection function
###################################################
def connect_to_snowflake():
    """Establishes and returns a connection to the Snowflake database."""
    conn = connect(
        user = "mfatol1",
        password = "Homesweethome25",
        account = "XITXDOX-WV45941", # From Welcome email
        warehouse = "amazon_data",
        database = "amazon_data_db",
        schema = "bronze",
        # schema = "staging",
    )
    return conn

###################################################
# Load CSV to Snowflake function
###################################################
def load_csv_to_snowflake(csv_path, table_name, conn, if_create):
    
    # Read CSV into DataFrame
    df = pd.read_csv(csv_path)
    
    # Write Dataframe to snowflake 
    success, nchunks, nrows, _ = write_pandas( 
        conn=conn,
        df=df,
        table_name=table_name.upper(),
        auto_create_table=if_create,
        overwrite=True
    )
    if success:
        print(f"  → ✅ Loaded'{table_name}' with {nrows} rows ({nchunks} chunks)")
    else:
        print(f"  → ❌ Failed to load {csv_path} into Snowflake.")
        
###################################################
# --- Data Loading Functions ---
###################################################
def remove_duplicates(file, file_path):
    df = pd.read_csv(file_path)
    initial_count = len(df)
    df.drop_duplicates(inplace=True)
    final_count = len(df)
    df.to_csv(file_path, index=False)
    print(f"  → Removed {initial_count - final_count} duplicate rows from {file}.")
    
def load_files_from_directory(directory_path, conn):
    """
    1) Remove Duplicate rows from each CSV file in the specified directory.
    2) Load each CSV file into Snowflake, creating tables as needed.
    3) Skips auto-creation for tables that include date fields.
    """
    
    for file in os.listdir(directory_path):
        if file.endswith(".csv"):
            print(f"\nPROCESSING FILE -- {file}")
            # Remove duplicate rows before loading
            remove_duplicates(file, file_path=os.path.join(directory_path, file))
            table_name = file.split('.')[0]
            file_path = os.path.join(directory_path, file)
            # Check if the table name requires specific handling (False if date included)
            should_auto_create = table_name not in DATE_INCLUDED_TABLES
            load_csv_to_snowflake(file_path, table_name, conn, if_create=should_auto_create)

###################################################
# --- Main Orchestration Function ---
###################################################
def load_to_warehouse():
    """
    Main orchestration function to connect to Snowflake and initiate data loading
    for both modeled and transformed data directories.
    Handles connection and cursor management.
    """
    # Connect to snowflake at once
    conn = connect_to_snowflake()
    cursor = conn.cursor() # A cursor is created but not explicitly used for DDL/DML in the main flow, write_pandas handles that internally.
    
    #### Load all staging CSVs using dictionaries (old way - retained but inactive):
    # for table_name, file_path in staging_csv.items():
    #     load_csv_to_snowflake(file_path, table_name, conn, if_create=True) # Assuming staging tables can be auto-created
    # for table_name, file_path in star_schema_csv.items():
    #     load_csv_to_snowflake(file_path, table_name, conn, if_create=True) # Assuming star schema tables can be auto-created

    # Load data from defined paths
    # load_files_from_directory(OUTPUT_DIR, conn) # Loads modeled (star schema) data
    load_files_from_directory(TRANSFORMED_DATA_PATH, conn) # Loads transformed (staging) data

    # Close connection resources
    cursor.close() 
    conn.close() 
    print("\n--- Snowflake connection closed. Data loading complete. ---")
    
###################################################
# --- Script Entry Point ---
###################################################
if __name__ == "__main__":
    load_to_warehouse()

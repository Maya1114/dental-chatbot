import os  #operating system --> reading or writing to the file system
from azure.cosmos import CosmosClient #to connect to cosmosDB
from dotenv import load_dotenv #loads the secrets (from .env) into the environment
from rich.table import Table
from rich.console import Console
from config import COSMOS_URL, COSMOS_KEY, COSMOS_DB

# env_path = find_dotenv()

# print("working directory: ", os.getcwd())
# print("dotenv location: ", env_path)


client = CosmosClient(COSMOS_URL, COSMOS_KEY)
db = client.get_database_client(COSMOS_DB) 

console = Console()

def test_connection():
    print("containers:")
    for container in db.list_containers():
        print(" -", container['id'])


#for debugging
def display_db(container_name, limit=20):
    table_client = db.get_container_client(container_name)
    query = f"SELECT TOP {limit} * FROM c"
    results = list(table_client.query_items(query=query, enable_cross_partition_query=True))
    
    if not results:
        console.print(f"[red]No data found in {container_name}[/red]")
        return

    # Create the table
    table = Table(title=f"{container_name} (Top {limit})")
    sys_fields = ['_attachments', '_etag', '_rid', '_self', '_ts'] #extra fields from cosmos


    # Add columns based on keys
    keys = [k for k in results[0].keys() if k not in sys_fields]
    for key in keys:
        table.add_column(key, style="cyan", no_wrap=False, overflow="fold")

    # Add rows
    for row in results:
        table.add_row(*(str(row.get(k, "")) for k in keys))

    console.print(table)

# also for debugging to see what is in the containers w/o printing out the table
def check_container(container: str, schema: dict):
    #bruh why it is schemaless :(
    table = db.get_container_client(container)
    query  = "SELECT TOP 50 * FROM c"
    #cross partition because the query requires we read across multiple partitions in the DB
    results = list(table.query_items(query=query, enable_cross_partition_query=True))

    sys_fields = ['_attachments', '_etag', '_rid', '_self', '_ts'] #extra fields from cosmos

    columns = set()
    for row in results:
        for key in row.keys():
            if key not in sys_fields:
                columns.add(key)

    #value hints so the query builder knows what types of values are in the DB
    if container == "appointments":
        value_hints = {
            "PatientStatus": ["confirmed", "pending", "cancelled"],
            "Provider": ["DEN1", "DEN2", "DEN3", "DEN4"],
            "Column": ["OP1", "OP2", "OP4"],
            "practiceId": ["id1", "id2", "id3"],
            "Time": ["YYYY-MM-DDTHH:MM:SS"]
        }

    elif container == "patients":
        value_hints = {
            "practiceId": ["id1"],
            "Name": ["Chad Wright", "Jeremy Morris", "Kenneth Collins"],
            "PhoneNumber": ["+1-886-386-4081", "+1-555-258-1285", "+1-278-206-9937"]
        }

    schema[container] = {
        "columns" : columns,
        "value_hints" : value_hints
    }
    return schema

#to tell the ai what is in the db
def load_schema():
    schema = {}
    #hardcoded container names for these function calls (cuz there's only 2) but I could have extracted the container[ids] instead
    schema = check_container("appointments", schema)
    schema = check_container("patients", schema)
    return schema

#query the db
def run_query(container: str, query: str):
    table = db.get_container_client(container)
    results = list(table.query_items(query=query, enable_cross_partition_query=True))
    return results

if __name__ == "__main__":
    test_connection()
    display_db("appointments")
    display_db("patients")

    #print(run_query("patients", "select top 5 * from c"))
    #print(run_query("appointments", "SELECT TOP 10 c.PatientName FROM c WHERE c.PatientStatus <> 'confirmed'"))



    #DB columns: 
    #  appointments: PatientId, PatientName, PatientStatus, Provider, Time, practiceId, id
    #  patients: Name, PhoneNumber, practiceId, id
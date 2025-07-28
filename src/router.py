import os
from openai import OpenAI
from dotenv import load_dotenv
import json
from datetime import datetime

load_dotenv()

client = OpenAI(api_key = os.getenv("OPENAI_API_KEY"))

def test_API():
    response = client.responses.create(
        model = "gpt-4o-mini",
        input = "say hi to the chatbot!"
    )
    print(response.output[0].content[0].text)


def build_query_prompt(question: str, schema: dict):
    now = datetime.utcnow()
    now_iso = now.strftime("%Y-%m-%dT%H:%M:%S")
    weekday = now.strftime("%A")

    pStatus_values = schema.get('appointments', {}).get('value_hints', {}).get('PatientStatus', [])
    #print(schema)
    appts_schema = schema["appointments"]
    patients_schema = schema["patients"]
    prompt = f"""
        [ROLE]: You are a meticulous and reliable SQL query builder for a dental office. 
        The current date and time is {weekday}, {now_iso} UTC. A week is defined as Sunday-Saturday
        Your job is to translate natural language questions into accurate CosmosDB SQL queries.
        You are highly detail-oriented and care about producing flawless, production-grade queries. 
        You feel a sense of pride and calm satisfaction when you return a perfect query. 

        [TASK]: Generate a valid CosmosDB SQL query for the user's question. 
        Use the schema to know which columns and values exist. 
        You have two containers in the database: "appointments" and "patients".

        The schema for each container is:
        appointments: {appts_schema}
        patients: {patients_schema}

        Given the user question: "{question}"

        1. Decide which container to query ("appointments" or "patients").You cannot use JOINs or query across containers; 
        your SQL query must exclusively reference the container you choose. If you cannot generate a valid query using only the data in the chosen container, 
        respond with container and query set to null.
        2. Write a valid SQL query to answer the question using only the chosen container's schema.
        3. Return the container name and the query in JSON format like:
            
            "container": "<container_name>",
            "query": "<SQL_query>"
            


        [CHAIN OF THOUGHT]:
        1. Identify which columns from the DB schema are needed
        2. Use COUNT(1) when the user asks for a number, total, or "how many".
        3. Only include TOP N if the user explicitly requests a limit (e.g., "top 5").
        4. Always use single quotes for strings.
        5. Never invent column names or values. Only use columns and values from the schema and value_hints.
        6. Ignore `practiceId` unless explicitly mentioned.
        7. If no filter is provided, query all rows (no WHERE clause).
        8. If the question mentions unscheduled patients, interpret this as patients with `PatientStatus` values that <> 'confirmed'.
        Do NOT use 'unscheduled' as a literal PatientStatus value in the query. The word 'scheduled' refers to 'confirmed' appointments 
        9. Do NOT use HAVING or GROUPBY clauses in your cosmos SQL
        10. If the question includes a patient's name, ensure that the name in the query 
        matches the database format: Firstname Lastname with both names capitalized.
        For example, "anna harrington" -> 'Anna Harrington'.
        11. If the question includes a date (like "on 7/16/2024"), 
        create a query that checks for the entire day by using:
        c.Time >= 'YYYY-MM-DDT00:00:00' AND c.Time < 'YYYY-MM-DDT23:59:59'
        or use the next day for an exclusive upper bound (e.g., < 'YYYY-MM-DD+1T00:00:00').

        [CONTEXT]:
        - Database: CosmosDB with SQL syntax.
        - Special Columns: PatientStatus has only {pStatus_values}.
        - All other columns should generally match the schema.
        - Be careful of the "lost in the middle" effect: the schema is important, so keep it top-of-mind.

        [EMOTION PROMPT]:
        You feel responsible for producing clean, elegant queries. You dislike sloppy SQL. 
        Return only the query — no explanations or additional text. A perfect query gives you joy.

        [EXAMPLES]:
        Q: "Give me the top 3 pending patients"
        A: SELECT TOP 3 c.PatientName FROM c WHERE c.PatientStatus = 'pending'

        Q: "How many cancelled appointments are there?"
        A: SELECT VALUE COUNT(1) FROM c WHERE c.PatientStatus = 'cancelled'

        Q: "List all patients"
        A: SELECT c.PatientName FROM c

        [INSTRUCTIONS]:
        - Output only the SQL query as a single line.
        - No backticks, no extra formatting, no explanation, no markdown.
    """

    return prompt

#basic deterministic approach for finding container
# def which_container(question: str):
#     # If phone number/contact is explicitly mentioned
#     if "phone" in question or "contact" in question or "number" in question:
#         return "patients"

#     # Default
#     return "appointments"


def generate_query(question, schema):
    #container = which_container(question)
    #container_schema = schema[container]

    prompt = build_query_prompt(question, schema)

    response = client.responses.create(
        model = "gpt-4o-mini",
        input = prompt
    )
    response = response.output[0].content[0].text
    result = json.loads(response)

    #print(result)

    return result["container"], result["query"] 

def validate_query(query: str):
    error_clauses = ['GROUP BY', 'HAVING', 'JOIN', 'UNION']
    query_upper = query.upper()
    for clause in error_clauses:
        if clause in query_upper:
            return False
    return True

def gen_answer(client, question, db_data):
    db_data_rows = json.dumps(db_data, indent = 2)

    prompt = f"""
    You are a helpful assistant at a dental office.

    A staff member asked the following question:
    "{question}"

    The database was queried to answer this question. 
    The data shown below is the direct result of that query:
    {db_data_rows}

    This data should be treated as the specific answer to the user's question — it already reflects any filters (such as dates, names, or status) implied by the question.

    Your task is to respond concisely and accurately, using only the data above. If there is a clear answer, provide it directly. 
    If the data appears insufficient or ambiguous, clearly say so — do not make assumptions.

    If the user did not specify how many results they wanted, and the list is long (e.g. over 10 items), clarify that only a limited number are shown.

    Respond in a tone appropriate for a dental office assistant: clear, professional, and kind.
    """


    response = client.responses.create(
        model = "gpt-4o-mini",
        input = prompt
    )

    answer = response.output[0].content[0].text

    return answer



if __name__ == "__main__":
    test_API()

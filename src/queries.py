#hardcode conditions for query generation (later to replace with ai querying)
def build_query(question: str, schema: dict):
    #question = question.lower()

    if "unscheduled" in question:
        query, container = "SELECT c.PatientName FROM c WHERE c.PatientStatus <> 'confirmed'", "appointments"

        return query, container

    elif "last week" in question:
        query = "SELECT * FROM c WHERE c.Time >= '2025-07-18' AND c.Time < '2025-07-25'", "appointments"

        return query, container
    else:
        return None, None
    


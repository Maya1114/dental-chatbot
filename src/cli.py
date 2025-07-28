import typer
from cosmos_client import test_connection, load_schema, run_query
from router import test_API, client, gen_answer, validate_query
from router import generate_query


app = typer.Typer()

#load the schema into local mem
DBschema = load_schema()

@app.command()
def ping():
    typer.echo("Testing cosmos and openai...\n")
    test_connection()
    print()

    test_API()
    print()

    typer.echo("Schema loaded:")
    print(DBschema)

@app.command()
def ask(question: str):
    container, query = generate_query(question.lower(), DBschema)
    if not query:
        typer.echo("Is there something I can help you with?")
        return
    
    valid = validate_query(query)
    if not valid:
        typer.echo("Sorry, this question cannot be answered due to database limitations.")
        return
    
    results = run_query(container, query)
    #print(results)

    answer = gen_answer(client, question, results)

    typer.echo(answer)



if __name__ == "__main__":
    app()

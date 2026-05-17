import typer

app = typer.Typer()

@app.command()
def run():
    main()

def main() -> None: ...

if __name__ == "__main__":
    app()

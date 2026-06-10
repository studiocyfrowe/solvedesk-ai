import typer
from pathlib import Path

from solvedesk_cmd.application.dependencies import get_env_builder
from solvedesk_cmd.infrastructure.dependencies import get_collection_manager
from solvedesk_cmd.infrastructure.installers.model_downloader import ModelDownloader

app = typer.Typer(help="Vector database commands")

@app.command(
    "checkout",
    help="Checkout vector database"
)
def checkout_db(
    database_dir: str = typer.Argument(
        ...,
        help="Vector database directory name"
    )
):
    manager = get_collection_manager()
    env_builder = get_env_builder()
    databases_path = Path("./utils/databases")
    if not databases_path.exists():
        typer.echo("Directory ./databases does not exist")
        raise typer.Exit(code=1)

    selected_database = databases_path / database_dir

    if not selected_database.exists():
        typer.echo(
            f"Database directory does not exist: {selected_database}"
        )

        typer.echo("\nAvailable databases:\n")

        for item in databases_path.iterdir():
            if item.is_dir():
                typer.echo(f"- {item.name}")

        raise typer.Exit(code=1)

    env_builder.update_env_variable(
        "CHROMA_DIR",
        f"./utils/databases/{database_dir}"
    )
    
    manager.refresh()

    typer.echo(f"Checked out database: {database_dir}")
    typer.echo(f"CHROMA_DIR={selected_database}")

@app.command(
    "init",
    help="Initialize vector database [ChromaDB] & embedding model [silver-retriever]"
)
def init_vector_db(
    collection_name: str = typer.Option(
        "random-text",
        help="Collection name"
    ),

    model_repo: str = typer.Option(
        "https://huggingface.co/ipipan/silver-retriever-base-v1",
        help="HuggingFace model repository"
    ),

    models_dir: str = typer.Option(
        "./utils/models",
        help="Directory for downloaded models"
    ),

    chroma_dir: str = typer.Option(
        "default-db",
        help="Vector database directory name"
    )
):
    manager = get_collection_manager()
    env_builder = get_env_builder()
    databases_path = Path("./utils/databases")

    databases_path.mkdir(
        parents=True,
        exist_ok=True
    )

    final_database_path = databases_path / chroma_dir

    env_builder.update_env_variable(
        "CHROMA_DIR",
        f"./utils/databases/{chroma_dir}"
    )

    final_database_path.mkdir(
        parents=True,
        exist_ok=True
    )

    model_local_path = None

    if typer.confirm(
        "\n[CONFIRM] Download embedding model (ipipan/silver-retriever-v1)?"
    ):
        model_downloader = ModelDownloader(
            model_repo=model_repo,
            models_dir=models_dir
        )

        _, model_local_path = model_downloader.combine_url()

        model_downloader.execute()
    else:
        _, model_local_path = ModelDownloader(
            model_repo=model_repo,
            models_dir=models_dir
        ).combine_url()

    env_config = env_builder.get_env_config(
        model_local_path=str(model_local_path),
        chroma_dir=str(final_database_path),
        collection_name=collection_name
    )

    env_builder.execute()
    manager.refresh()

    typer.echo("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    typer.echo(f"[STATUS] Created databases directory: {databases_path}")
    typer.echo(f"[STATUS] Created vector database: {final_database_path}")
    typer.echo("[STATUS] Vector Database is ready!")
    typer.echo("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    typer.echo("[NEXT STEP] Create new collection: solvedesk db new <collection-name>")


@app.command("list", help="Show list of ChromaDB collections")
def list_collections():
    manager = get_collection_manager()
    collections = manager.list_all()

    if not collections:
        typer.echo("Brak kolekcji.")
        raise typer.Exit()

    for collection in collections:
        typer.echo(
            f"{collection['name']} | "
            f"id={collection['id']} | "
            f"documents={collection['documents_count']} | "
            f"metadata={collection['metadata']}"
        )


@app.command(
    "details",
    help="Show collection details"
)
def collection_details(
    collection_name: str,
    full: bool = typer.Option(
        False,
        "--full",
        help="Show full document content"
    )
):
    manager = get_collection_manager()

    try:
        details = manager.retrieve_details(
            collection_name
        )
    except Exception:
        typer.echo(
            f"[ERROR] Collection not found: {collection_name}"
        )
        raise typer.Exit(code=1)

    typer.echo("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    typer.echo("COLLECTION DETAILS")
    typer.echo("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")

    typer.echo(f"Name: {details['name']}")
    typer.echo(f"ID: {details['id']}")
    typer.echo(
        f"[STATUS] Documents (count): {details['documents_count']}"
    )
    typer.echo(
        f"[STATUS] Metadata: {details['metadata']}"
    )

    documents = details.get("documents", [])
    metadatas = details.get("metadatas", [])
    ids = details.get("ids", [])

    if not documents:
        typer.echo("\n[STATUS] No documents.")
        return

    typer.echo("\nDOCUMENTS\n")

    for index, document in enumerate(documents):

        typer.echo("=" * 80)

        if ids and index < len(ids):
            typer.echo(f"ID: {ids[index]}")

        if metadatas and index < len(metadatas):
            typer.echo(f"Metadata: {metadatas[index]}")

        typer.echo("\n[STATUS] Content:\n")

        content = str(document)

        if not full and len(content) > 500:
            content = content[:500] + "\n...[TRUNCATED]..."

        typer.echo(content)

        typer.echo("")

    typer.echo("=" * 80)


@app.command("new", help="Create new ChromaDB collection")
def create_collection(
    collection_name: str = typer.Option(
        None,
        help="Collection name. If empty, random sd-collection-* will be created."
    )
):
    manager = get_collection_manager()
    created_name = manager.create(collection_name)

    typer.echo(f"[STATUS] Created new collection: {created_name}")
    typer.echo("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    typer.echo("[NEXT STEP] Show details: solvedesk db details <collection-name>")
    typer.echo("[NEXT STEP] Show list: solvedesk db list")


@app.command("delete", help="Delete ChromaDB collection")
def delete_collection(collection_name: str):
    manager = get_collection_manager()
    deleted = manager.delete(collection_name)

    if deleted:
        typer.echo(f"[STATUS] Collection deleted: {collection_name}")
    else:
        typer.echo(f"[STATUS] Collection not found: {collection_name}")
        raise typer.Exit(code=1)
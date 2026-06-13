import typer, time
from dotenv import load_dotenv
from solvedesk_cmd.application.dependencies import get_data_reporter, get_chart_builder, get_chunker
from solvedesk_cmd.infrastructure.dependencies import get_collection, get_model, get_collection_manager

load_dotenv()

app = typer.Typer(name="data")

@app.command(
    "chunk",
    help="Chunk documents and save them to a new collection"
)
def chunking(
    collection_name: str = typer.Argument(
        ...,
        help="Source collection name"
    ),
    target_collection_name: str = typer.Option(
        None,
        "--target",
        "-t",
        help="Target collection name"
    ),
    chunk_size: int = typer.Option(
        512,
        "--chunk-size",
        help="Chunk size in tokens"
    )
):
    try:
        if collection_name.endswith("_chunks"):
            raise ValueError(
                "Collection appears to already contain chunks. "
                "Use the source collection instead."
            )

        if chunk_size <= 0:
            raise ValueError(
                "Chunk size must be greater than 0."
            )

        if target_collection_name is None:
            target_collection_name = (
                f"{collection_name}_chunks"
            )

        if collection_name == target_collection_name:
            raise ValueError(
                "Source and target collections cannot be the same."
            )

        col_mg = get_collection_manager()

        source_ids, source_documents, source_metadatas, _ = (
            col_mg.get_collection(
                collection_name=collection_name
            )
        )

        if not source_documents:
            typer.echo(
                "\n[WARNING] No documents found."
            )
            return

        typer.echo(
            f"\n[INFO] Source collection: {collection_name}"
        )
        typer.echo(
            f"[INFO] Target collection: {target_collection_name}"
        )
        typer.echo(
            f"[INFO] Chunk size: {chunk_size} tokens\n"
        )

        col_mg.create(
            collection_name=target_collection_name
        )

        _, _, _, target_collection = (
            col_mg.get_collection(
                collection_name=target_collection_name
            )
        )

        model = get_model()

        chunker = get_chunker(
            ids=source_ids,
            documents=source_documents,
            metadatas=source_metadatas,
            model=model,
            target_collection=target_collection,
            chunk_size=chunk_size
        )

        start_time = time.perf_counter()

        total_chunks = chunker.execute()

        duration = time.perf_counter() - start_time

        typer.echo(
            "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        )
        typer.echo(
            "[SUCCESS] Chunking completed"
        )
        typer.echo(
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        )
        typer.echo(
            f"Documents processed : {len(source_documents)}"
        )
        typer.echo(
            f"Chunks created      : {total_chunks}"
        )
        typer.echo(
            f"Duration            : {duration:.2f}s"
        )
        typer.echo(
            f"Saved to            : {target_collection_name}"
        )

    except Exception as e:
        typer.echo(
            "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        )
        typer.echo(
            f"[ERROR] {str(e)}"
        )
        typer.echo(
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        )
        raise typer.Exit(code=1)

@app.command(
    "revision",
    help="Check embedding quality using cosine similarity and clustering"
)
def revision(
    collection_name: str = typer.Argument(
        ...,
        help="Collection name"
    ),
    clusters: int = typer.Option(
        3,
        help="Number of clusters"
    )
):
    try:
        model = get_model()
        col_mg = get_collection_manager()

        ids, documents, metadatas, collection = col_mg.get_collection(
            collection_name=collection_name
        )

        if documents is None or len(documents) == 0:
            typer.echo("No documents found in collection.")
            return

        result = collection.get(
            include=["documents", "embeddings", "metadatas"]
        )

        documents = result.get("documents", [])
        embeddings = result.get("embeddings", [])
        ids = result.get("ids", [])

        if embeddings is None:
            typer.echo("No embeddings found in collection.")
            return

        reporter = get_data_reporter(
            model=model,
            documents=documents,
            embeddings=embeddings,
            clusters=clusters
        )

        report = reporter.execute()

        typer.echo("\nEmbedding quality report\n")
        typer.echo(f"Documents count: {report['documents_count']}")
        typer.echo(f"Embedding size: {report['embedding_size']}")
        typer.echo(f"Mean similarity: {report['mean_similarity']:.4f}")

        typer.echo("\nClusters:")
        for cluster in report["clusters"]:
            typer.echo(
                f"Cluster {cluster['cluster_id']}: "
                f"{cluster['count']} documents"
            )

        typer.echo("\nToken statistics:")
        for item in report["token_statistics"]:
            typer.echo(
                f"Document {item['doc_id']} | "
                f"Tokens: {item['token_count']}/{item['max_tokens']} "
                f"({item['usage_percent']}%) | "
                f"Truncated: {item['truncated']} | "
                f"Embedding size: {item['embedding_size']}"
            )

        charts = get_chart_builder()

        cluster_chart = charts.clusters(
            embeddings=embeddings,
            labels=report["labels"]
        )

        token_chart = charts.token_limit_bar(
            token_statistics=report["token_statistics"]
        )

        similarity_chart = charts.cosine_similarity_progress([
            {
                "doc_id": "mean",
                "cosine_similarity": float(report["mean_similarity"])
            }
        ])

        typer.echo("\nCharts created:")
        typer.echo(f"Clusters: {cluster_chart}")
        typer.echo(f"Token limit: {token_chart}")
        typer.echo(f"Cosine similarity: {similarity_chart}")

    except Exception as e:
        typer.echo(f"\nERROR: {str(e)}\n")
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
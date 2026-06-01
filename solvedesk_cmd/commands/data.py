import typer, math

from dotenv import load_dotenv
import numpy as np

from application.dependencies import get_data_reporter, get_chart_builder
from infrastructure.dependencies import get_collection, get_model, get_collection_manager

load_dotenv()

app = typer.Typer(name="data")

@app.command(
    "chunk",
    help="Chunk documents and save them only to a new collection"
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
        model = get_model()
        col_mg = get_collection_manager()

        source_collection = col_mg.get_collection(
            collection_name=collection_name
        )

        if target_collection_name is None:
            target_collection_name = f"{collection_name}_chunks"

        col_mg.create(
            collection_name=target_collection_name
        )

        target_collection = col_mg.get_collection(
            collection_name=target_collection_name
        )

        data = source_collection.get(
            include=["documents", "metadatas"]
        )
        
        ids = data.get("ids", [])
        documents = data.get("documents", [])
        metadatas = data.get("metadatas", [])

        if not documents:
            typer.echo("Brak dokumentów do podziału.")
            return

        if collection_name.endswith("_chunks"):
            raise ValueError(
                "Ta kolekcja wygląda już na podzieloną na chunki. "
                "Podaj kolekcję źródłową, np. faq zamiast faq_chunks."
            )

        if target_collection_name is None:
            target_collection_name = f"{collection_name}_chunks"

        if collection_name == target_collection_name:
            raise ValueError(
                "Kolekcja źródłowa i docelowa nie mogą być takie same."
            )

        total_chunks = 0

        for index, document in enumerate(documents):
            source_id = ids[index]
            metadata = metadatas[index] if metadatas else {}

            if "_chunk_" in str(source_id):
                typer.echo(
                    f"Pominięto {source_id}, bo wygląda jak istniejący chunk."
                )
                continue

            tokens = model.tokenize([str(document)])
            input_ids = tokens["input_ids"][0]

            token_count = len(input_ids)
            chunks_count = math.ceil(token_count / chunk_size)

            typer.echo(
                f"Document {source_id}: "
                f"{token_count} tokens -> {chunks_count} chunks"
            )

            chunk_parts = np.array_split(
                input_ids,
                chunks_count
            )

            for chunk_index, chunk_token_ids in enumerate(chunk_parts):
                chunk_token_ids = chunk_token_ids.tolist()

                chunk_text = model.tokenizer.decode(
                    chunk_token_ids,
                    skip_special_tokens=True
                )

                if not chunk_text.strip():
                    continue

                chunk_id = f"{source_id}_chunk_{chunk_index + 1}"

                typer.echo(
                    f"  {chunk_id}: {len(chunk_token_ids)} tokens"
                )

                chunk_metadata = {
                    **metadata,
                    "source_id": source_id,
                    "chunk_index": chunk_index + 1,
                    "chunk_total": chunks_count,
                    "chunk_tokens": len(chunk_token_ids),
                    "max_chunk_size": chunk_size,
                    "source_token_count": token_count
                }

                embedding = model.encode(chunk_text).tolist()

                target_collection.add(
                    ids=[chunk_id],
                    documents=[chunk_text],
                    embeddings=[embedding],
                    metadatas=[chunk_metadata]
                )

                total_chunks += 1

        typer.echo("\nChunking completed")
        typer.echo(f"Source collection: {collection_name}")
        typer.echo(f"Target collection: {target_collection_name}")
        typer.echo(f"Created chunks: {total_chunks}")

    except Exception as e:
        typer.echo(f"\nERROR: {str(e)}\n")
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
        collection = get_collection()

        data = collection.get(
            include=["documents", "embeddings"]
        )

        documents = data.get("documents", [])
        embeddings = data.get("embeddings", [])

        if documents is None or len(documents) == 0:
            typer.echo("No documents found in collection.")
            return

        if embeddings is None or len(embeddings) == 0:
            typer.echo("No embeddings found in collection.")
            return

        reporter = get_data_reporter(
            model=get_model(),
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
                "cosine_similarity": report["mean_similarity"]
            }
        ])

        typer.echo("\nCharts created:")
        typer.echo(f"Clusters: {cluster_chart}")
        typer.echo(f"Token limit: {token_chart.resolve()}")
        typer.echo(f"Cosine similarity: {similarity_chart}")

    except Exception as e:
        typer.echo(f"\nERROR: {str(e)}\n")
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
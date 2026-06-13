import math
import typer
import numpy as np
from rich.progress import (
    Progress,
    SpinnerColumn,
    BarColumn,
    TextColumn,
    TimeElapsedColumn,
    TimeRemainingColumn
)
from rich.console import Console

console = Console()

class Chunkers:
    def __init__(
        self,
        ids,
        documents,
        metadatas,
        model,
        target_collection,
        chunk_size: int = 10
    ):
        self.ids = ids
        self.documents = documents
        self.metadatas = metadatas
        self.model = model
        self.target_collection = target_collection
        self.chunk_size = chunk_size
        
    def chunk_document(
        self,
        document: str,
        chunk_size: int
    ) -> list[str]:
        tokens = self.model.tokenize([str(document)])
        input_ids = tokens["input_ids"][0]

        chunks = []

        for start in range(0, len(input_ids), chunk_size):
            end = start + chunk_size
            chunk_tokens = input_ids[start:end]

            chunk_text = self.model.tokenizer.decode(
                chunk_tokens,
                skip_special_tokens=True
            )

            chunks.append(chunk_text)

        return chunks

    def execute(self) -> int:
        total_chunks = 0

        with Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]Chunking documents"),
            BarColumn(),
            TextColumn("{task.completed}/{task.total}"),
            TimeElapsedColumn(),
            TimeRemainingColumn(),
            console=console
        ) as progress:

            task = progress.add_task(
                "chunking",
                total=len(self.documents)
            )

            for index, document in enumerate(self.documents):
                source_id = self.ids[index]
                metadata = self.metadatas[index] if self.metadatas else {}

                chunks = self.chunk_document(
                    document=document,
                    chunk_size=self.chunk_size
                )

                for chunk_index, chunk in enumerate(chunks, start=1):
                    chunk_id = f"{source_id}_chunk_{chunk_index}"

                    embedding = self.model.encode(chunk).tolist()

                    self.target_collection.add(
                        ids=[chunk_id],
                        documents=[chunk],
                        embeddings=[embedding],
                        metadatas=[{
                            **metadata,
                            "source_id": source_id,
                            "chunk_index": chunk_index,
                            "chunk_size": self.chunk_size
                        }]
                    )

                    total_chunks += 1

                progress.update(task, advance=1)

        return total_chunks

    def _is_chunk(self, source_id) -> bool:
        return "_chunk_" in str(source_id)

    def _print_skipped(self, source_id):
        typer.echo(
            f"Pominięto {source_id}, bo wygląda jak istniejący chunk."
        )

    def _get_metadata(self, index: int) -> dict:
        if not self.metadatas:
            return {}

        return self.metadatas[index] or {}

    def _tokenize(self, document):
        tokens = self.model.tokenize([str(document)])
        return tokens["input_ids"][0]

    def _calculate_chunks_count(self, token_count: int) -> int:
        return math.ceil(token_count / self.chunk_size)

    def _split_tokens(self, input_ids, chunks_count: int):
        return np.array_split(input_ids, chunks_count)

    def _decode_tokens(self, token_ids) -> str:
        return self.model.tokenizer.decode(
            token_ids,
            skip_special_tokens=True
        )

    def _create_chunk_id(
        self,
        source_id,
        chunk_index: int
    ) -> str:
        return f"{source_id}_chunk_{chunk_index + 1}"

    def _create_chunk_metadata(
        self,
        metadata: dict,
        source_id,
        chunk_index: int,
        chunks_count: int,
        chunk_tokens_count: int,
        token_count: int
    ) -> dict:
        return {
            **metadata,
            "source_id": source_id,
            "chunk_index": chunk_index + 1,
            "chunk_total": chunks_count,
            "chunk_tokens": chunk_tokens_count,
            "max_chunk_size": self.chunk_size,
            "source_token_count": token_count
        }

    def _create_embedding(self, chunk_text: str):
        return self.model.encode(chunk_text).tolist()

    def _add_chunk(
        self,
        chunk_id: str,
        chunk_text: str,
        embedding,
        chunk_metadata: dict
    ):
        self.target_collection.add(
            ids=[chunk_id],
            documents=[chunk_text],
            embeddings=[embedding],
            metadatas=[chunk_metadata]
        )

    def _save_chunks(
        self,
        source_id,
        chunks,
        metadata: dict,
        chunks_count: int,
        token_count: int
    ) -> int:
        created_chunks = 0

        for chunk_index, chunk_token_ids in enumerate(chunks):
            chunk_token_ids = chunk_token_ids.tolist()
            chunk_text = self._decode_tokens(chunk_token_ids)

            if not chunk_text.strip():
                continue

            chunk_id = self._create_chunk_id(
                source_id=source_id,
                chunk_index=chunk_index
            )

            self._print_chunk_info(
                chunk_id=chunk_id,
                chunk_tokens_count=len(chunk_token_ids)
            )

            chunk_metadata = self._create_chunk_metadata(
                metadata=metadata,
                source_id=source_id,
                chunk_index=chunk_index,
                chunks_count=chunks_count,
                chunk_tokens_count=len(chunk_token_ids),
                token_count=token_count
            )

            embedding = self._create_embedding(chunk_text)

            self._add_chunk(
                chunk_id=chunk_id,
                chunk_text=chunk_text,
                embedding=embedding,
                chunk_metadata=chunk_metadata
            )

            created_chunks += 1

        return created_chunks

    def _print_document_info(
        self,
        source_id,
        token_count: int,
        chunks_count: int
    ):
        typer.echo(
            f"Document {source_id}: "
            f"{token_count} tokens -> {chunks_count} chunks"
        )

    def _print_chunk_info(
        self,
        chunk_id: str,
        chunk_tokens_count: int
    ):
        typer.echo(
            f"  {chunk_id}: {chunk_tokens_count} tokens"
        )
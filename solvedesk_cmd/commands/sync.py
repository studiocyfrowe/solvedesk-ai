import os
import json
import typer
import pandas as pd

from pathlib import Path
from dotenv import load_dotenv

from solvedesk_cmd.domain.enums.allowed_types import AllowedTypes
from solvedesk_cmd.domain.enums.allowed_extensions import AllowedExtensions

from solvedesk_cmd.application.dependencies import get_data_preprocessor, get_env_builder
from solvedesk_cmd.infrastructure.dependencies import get_cli_data_sync_service

load_dotenv()

app = typer.Typer(name="sync")


def load_records_from_file(path: Path, ext: str) -> list[dict]:
    if ext == ".json":
        raw_data = json.loads(
            path.read_text(encoding="utf-8")
        )

        return raw_data if isinstance(raw_data, list) else [raw_data]

    if ext == ".csv":
        df = pd.read_csv(path)
        return df.to_dict(orient="records")

    if ext == ".xlsx":
        df = pd.read_excel(path)
        return df.to_dict(orient="records")

    return []


def get_preprocessing_config(type: str) -> tuple[list[str], list[str]]:
    if type == "know-base":
        return (
            ["id", "name", "question", "answer"],
            ["name", "question", "answer"]
        )

    if type == "faq":
        return (
            ["id", "question", "answer"],
            ["question", "answer"]
        )

    if type == "helpdesk":
        return (
            ["id", "title", "problem", "solution"],
            ["title", "problem", "solution"]
        )

    raise typer.BadParameter(
        "Unsupported data type. Use: know_base, faq or helpdesk"
    )


@app.command(
    "api",
    help="Download data from external API and save to selected vector database collection"
)
def sync_api(
    api_url: str = typer.Argument(
        ...,
        help="External API URL"
    ),
    collection_name: str = typer.Option(
        ...,
        "--collection-name",
        "-c",
        help="Choose existing collection in your database"
    ),
    token: str = typer.Option(
        None,
        "--token",
        "-t",
        help="Bearer token for external API"
    ),
    data_type: str = typer.Option(
        "know-base",
        "--type",
        help="Data type: know-base, faq or helpdesk"
    )
):
    try:
        typer.echo("\n[STATUS] Starting API synchronization...\n")

        service = get_cli_data_sync_service(
            api_url=api_url,
            token=token,
            collection_name=collection_name
        )

        count = service.sync(
            type=data_type
        )

        typer.echo(f"[STATUS] Imported documents: {count}")

        typer.echo("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        typer.echo("[SUCCESS] API Synchronization completed successfully!")
        typer.echo("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    except Exception as e:
        typer.echo(f"\n[ERROR] {str(e)}\n")
        raise typer.Exit(code=1)


@app.command(
    "file",
    help="Load data from local file and save to selected vector database collection"
)
def import_data(
    file_path: str,
    collection_name : str = typer.Argument(
        help="Choose existing collection in your database"
    ),
    type: str = typer.Option(
        "know-base",
        "--type",
        "-t",
        help="Data type: know_base, faq or helpdesk"
    )
):
    try:
        path = Path(file_path)
        if not path.exists():
            raise typer.BadParameter(
                f"File does not exist: {file_path}"
            )

        ext = path.suffix.lower()

        allowed_extensions = AllowedExtensions.to_list()
        if ext not in allowed_extensions:
            raise typer.BadParameter(
                f"Unsupported file format: {ext}"
            )

        allowed_types = AllowedTypes.to_list()
        if type not in allowed_types:
            raise typer.BadParameter(
                "Unsupported data type. Use: know_base, faq or helpdesk"
            )

        records = load_records_from_file(
            path=path,
            ext=ext
        )

        required_fields, text_fields = get_preprocessing_config(type)

        data_processor = get_data_preprocessor(
            records=records,
            required_fields=required_fields,
            text_fields=text_fields
        )

        clean_records = data_processor.execute()

        typer.echo("\nPREPROCESSING SUMMARY\n")
        typer.echo(f"[STATUS] Raw records: {len(records)}")
        typer.echo(f"[STATUS] Valid records: {len(clean_records)}")
        typer.echo(f"[STATUS] Rejected records: {len(records) - len(clean_records)}")

        typer.echo("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        typer.echo("CLEAN FILE PREVIEW\n")

        preview = clean_records[:3]

        typer.echo(
            json.dumps(
                preview,
                indent=2,
                ensure_ascii=False
            )
        )

        typer.echo("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")
        typer.echo(f"[STATUS] Selected data type: {type}")

        confirmed = typer.confirm(
            "[CONFIRM] Do you want to import this cleaned data?"
        )

        if not confirmed:
            typer.echo("[STATUS] Import canceled")
            raise typer.Exit()

        content = json.dumps(
            clean_records,
            ensure_ascii=False
        ).encode("utf-8")

        service = get_cli_data_sync_service(
            api_url="",
            collection_name=collection_name
        )

        count = service.sync(
            type=type,
            content=content,
            extension=".json"
        )

        typer.echo(f"[STATUS] Imported documents: {count}")
        
        typer.echo("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        typer.echo(f"[SUCCESS] Documents has been imported!")
        typer.echo("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    except Exception as e:
        typer.echo(f"[ERROR] {str(e)}")
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
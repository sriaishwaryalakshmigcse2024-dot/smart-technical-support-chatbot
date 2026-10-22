
from pathlib import Path

import pymupdf
from docx import Document


SUPPORTED_EXTENSIONS = {".pdf", ".txt", ".docx"}


def extract_pdf(file_path: Path) -> list[dict]:
    """Extract readable text from each PDF page."""
    records = []

    with pymupdf.open(file_path) as pdf:
        if pdf.needs_pass:
            raise ValueError("PDF is password-protected.")

        for page_number, page in enumerate(pdf, start=1):
            text = page.get_text("text").strip()

            if text:
                records.append({
                    "source": file_path.name,
                    "location": f"Page {page_number}",
                    "text": text,
                })

    return records


def extract_txt(file_path: Path) -> list[dict]:
    """Extract text from a TXT file."""
    try:
        text = file_path.read_text(
            encoding="utf-8-sig"
        ).strip()
    except UnicodeDecodeError:
        text = file_path.read_text(
            encoding="cp1252"
        ).strip()

    if not text:
        return []

    return [{
        "source": file_path.name,
        "location": "Full document",
        "text": text,
    }]


def extract_docx(file_path: Path) -> list[dict]:
    """Extract paragraphs and tables from a Word document."""
    document = Document(file_path)
    parts = []

    # Extract paragraphs, including headings.
    for paragraph in document.paragraphs:
        text = paragraph.text.strip()

        if text:
            parts.append(text)

    # Extract tables.
    for table in document.tables:
        for row in table.rows:
            cells = [
                cell.text.strip().replace("\n", " ")
                for cell in row.cells
            ]

            if any(cells):
                parts.append(" | ".join(cells))

    text = "\n".join(parts).strip()

    if not text:
        return []

    return [{
        "source": file_path.name,
        "location": "Full document",
        "text": text,
    }]


def load_document(file_path: Path) -> list[dict]:
    """Select the appropriate extraction method."""
    extension = file_path.suffix.lower()

    if extension == ".pdf":
        return extract_pdf(file_path)

    if extension == ".txt":
        return extract_txt(file_path)

    if extension == ".docx":
        return extract_docx(file_path)

    raise ValueError(
        f"Unsupported file type: {extension or 'no extension'}"
    )


def load_knowledge_base(
    folder_path: str | Path
) -> tuple[list[dict], list[dict]]:
    """Load supported files and collect errors."""
    folder = Path(folder_path)

    if not folder.exists():
        raise FileNotFoundError(
            f"Knowledge-base folder does not exist: "
            f"{folder.resolve()}"
        )

    if not folder.is_dir():
        raise NotADirectoryError(
            f"Expected a folder, got a file: {folder.resolve()}"
        )

    records = []
    errors = []

    # Search subfolders too, so nested knowledge-base files are found.
    for file_path in sorted(folder.rglob("*")):
        if not file_path.is_file():
            continue

        if file_path.name.startswith("~$"):
            continue

        if file_path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            continue

        try:
            extracted = load_document(file_path)

            if not extracted:
                errors.append({
                    "source": str(file_path.relative_to(folder)),
                    "error": "No readable text found",
                })
                continue

            # Keep the relative path to distinguish duplicate filenames.
            for record in extracted:
                record["source"] = str(
                    file_path.relative_to(folder)
                )

            records.extend(extracted)

        except Exception as exc:
            errors.append({
                "source": str(file_path.relative_to(folder)),
                "error": f"{type(exc).__name__}: {exc}",
            })

    return records, errors


if __name__ == "__main__":
    # Run this script from your project root directory.
    project_folder = Path(__file__).resolve().parent
    knowledge_folder = project_folder / "data" / "knowledge_base"

    try:
        documents, errors = load_knowledge_base(
            knowledge_folder
        )

        print(f"Knowledge-base folder: {knowledge_folder}")
        print(f"Extracted records: {len(documents)}")
        print(f"Files with issues: {len(errors)}")

        for record in documents:
            print(f"\nSource: {record['source']}")
            print(f"Location: {record['location']}")
            print(f"Text preview: {record['text'][:300]}")

        for error in errors:
            print(
                f"\nIssue: {error['source']} - "
                f"{error['error']}"
            )

        if not documents:
            print(
                "\nNo text was extracted. Check that your "
                "knowledge-base folder contains PDF, TXT, "
                "or DOCX files with readable text."
            )

    except (FileNotFoundError, NotADirectoryError) as exc:
        print(f"Folder error: {exc}")

        {
    "source": "wifi_troubleshooting.txt",
    "location": "Full document",
    "text": "Check that Wi-Fi is enabled..."
}

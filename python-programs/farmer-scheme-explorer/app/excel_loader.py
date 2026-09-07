from pathlib import Path

import pandas as pd
from langchain_core.documents import Document


REQUIRED_COLUMNS = [
    "S.No",
    "Department",
    "Scheme",
    "Scheme Description",
    "Eligibility Criteria",
    "Document's Required",
    "GO & Guidelines",
]


def load_excel(file_path: str) -> list[Document]:
    """
    Load farmer schemes from Excel and convert
    each scheme into a LangChain Document.
    """

    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(
            f"Excel file not found: {file_path}"
        )

    df = pd.read_excel(path)

    missing_columns = [
        column
        for column in REQUIRED_COLUMNS
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing Excel columns: {missing_columns}"
        )

    documents = []

    for _, row in df.iterrows():

        scheme = str(row["Scheme"]).strip()

        if not scheme or scheme.lower() == "nan":
            continue

        department = clean_value(
            row["Department"]
        )

        description = clean_value(
            row["Scheme Description"]
        )

        eligibility = clean_value(
            row["Eligibility Criteria"]
        )

        documents_required = clean_value(
            row["Document's Required"]
        )

        guidelines = clean_value(
            row["GO & Guidelines"]
        )

        content = f"""
Scheme Name:
{scheme}

Department:
{department}

Scheme Description:
{description}

Eligibility Criteria:
{eligibility}

Documents Required:
{documents_required}

GO & Guidelines:
{guidelines}
""".strip()

        metadata = {
            "sno": clean_value(row["S.No"]),
            "department": department,
            "scheme": scheme,
        }

        documents.append(
            Document(
                page_content=content,
                metadata=metadata,
            )
        )

    return documents


def clean_value(value) -> str:
    """
    Convert Excel cell values into clean strings.
    """

    if pd.isna(value):
        return ""

    return str(value).strip()
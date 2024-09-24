from fastapi import APIRouter, UploadFile, status, Response, Depends
from pydantic import BaseModel
import pandas as pd
import io
import csv

global_data = {"gross_revenue": 0, "expense": 0, "net_revenue": 0}


def get_report_dependencies():
    return global_data


api_router = APIRouter()


class FileUploadSuccessMessage(BaseModel):
    message: str


class ErrorMessage(BaseModel):
    error: str


class GetReportResponse(BaseModel):
    gross_revenue: float
    expense: float
    net_revenue: float


@api_router.get("/ping")
def ping():
    return "pong"


@api_router.get("/report/", response_model=GetReportResponse)
async def get_report(dependency: dict[str, float] = Depends(get_report_dependencies)):
    """
    This endpoint is used to get a report of the financial data.
    """
    return GetReportResponse(
        gross_revenue=dependency["gross_revenue"],
        expense=dependency["expense"],
        net_revenue=dependency["net_revenue"],
    )


@api_router.post(
    "/transactions/",
    responses={
        200: {
            "model": FileUploadSuccessMessage,
            "description": "CSV received and processed",
        },
        400: {"model": ErrorMessage, "description": "Bad file uploaded"},
    },
)
async def post_transactions(
    file: UploadFile,
    response: Response,
    dependency: str = Depends(get_report_dependencies),
):
    """
    This endpoint is used to upload a CSV file to the server.
    This file should be formatted as a CSV file with the following columns:
    `Date, Type, Amount($), Memo`
    """
    if file.content_type != "text/csv":
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {
            "error": "The file must be a CSV file",
        }

    contents = await file.read()
    await process_csv_file(contents, dependency)

    return FileUploadSuccessMessage(message="CSV received and processed")


async def process_csv_file(contents: bytes, dependency: dict[str, float]):
    """
    Process the CSV file contents asynchrounously and
    saves the data to global variables.
    """
    df = preprocess_csv(contents)
    dependency["gross_revenue"] = df[df["Type"] == "income"]["Amount($)"].sum()
    dependency["expense"] = df[df["Type"] == "expense"]["Amount($)"].sum()
    dependency["net_revenue"] = dependency["gross_revenue"] - dependency["expense"]


def preprocess_csv(contents: bytes):
    """
    Read and validate the CSV contents.
    Returns a pandas DataFrame with valid rows.
    """
    valid_rows = []

    with io.BytesIO(contents) as csvfile:
        csv_reader = csv.reader(csvfile.read().decode("utf-8").splitlines())
        for row in csv_reader:
            if validate_row(row):
                row[2] = float(row[2])
                valid_rows.append(row[:4])

    df = pd.DataFrame(valid_rows, columns=["Date", "Type", "Amount($)", "Memo"])
    df["Type"] = df["Type"].str.strip().str.lower()

    return df


def validate_row(row):
    """
    Validate a row of the CSV based on specified data types.
    Returns True if valid, otherwise False.
    """
    if len(row) < 4:
        return False

    _, txn_type, amount_str, _ = row[:4]

    if txn_type not in [" Income", " Expense"]:
        return False

    try:
        amount = float(amount_str)
        if amount < 0:
            return False
    except ValueError:
        return False

    return True

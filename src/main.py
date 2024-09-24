from fastapi import FastAPI, UploadFile, status, Response
from pydantic import BaseModel

app = FastAPI()


class FileUploadSuccessMessage(BaseModel):
    message: str


class ErrorMessage(BaseModel):
    error: str


class GetReportResponse(BaseModel):
    gross_revenue: float
    expense: float
    net_revenue: float


@app.get("/ping")
def read_root():
    return "pong"


@app.get("/report/", response_model=GetReportResponse)
async def get_report():
    return {
        "gross_revenue": 1000.0,
        "expense": 500.0,
        "net_revenue": 500.0,
    }


@app.post(
    "/transactions/",
    responses={
        200: {
            "model": FileUploadSuccessMessage,
            "description": "CSV received and processed",
        },
        400: {"model": ErrorMessage, "description": "Bad file uploaded"},
    },
)
async def create_upload_file(file: UploadFile, response: Response):
    """
    This endpoint is used to upload a CSV file to the server.
    This file should be formatted as a CSV file with the following columns:
    `Date, Type, Amount($), Memo`
    """
    # Read the file and validate that it is a CSV file
    if file.content_type != "text/csv":
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {
            "error": "The file must be a CSV file",
        }

    # Read the file and print first 10 lines
    contents = await file.read()
    lines = contents.decode().split("\n")
    print(lines)

    return FileUploadSuccessMessage(message="CSV received and processed")

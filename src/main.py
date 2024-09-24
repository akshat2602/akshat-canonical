from fastapi import FastAPI, UploadFile, status, Response, BackgroundTasks
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
async def post_transactions(
    file: UploadFile, response: Response, background_tasks: BackgroundTasks
):
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

    # Read the file
    contents = await file.read()
    # Pass the contents to a different function to process the CSV file asynchrounously
    background_tasks.add_task(process_csv_file, contents)

    return FileUploadSuccessMessage(message="CSV received and processed")


def process_csv_file(contents: bytes):
    # This function would be used to process the CSV file asynchronously
    print("Processing CSV file")

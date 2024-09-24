import random
import csv
import io
from fastapi.testclient import TestClient
from datetime import datetime
from src.main import app

client = TestClient(app)


def generate_random_csv(
    num_rows: int,
    valid_column_no: bool = True,
    valid_data_types: bool = True,
    valid_row_prob: float = 0.8,  # Probability of generating a valid row
) -> io.StringIO:
    """
    Generate a random CSV with the columns: Date, Type, Amount($), Memo.
    The number of valid columns and data types can be controlled by flags
    and probabilities.

    :param num_rows: Number of rows to generate.
    :param valid_column_no: If True, include rows with valid column counts; otherwise,
        include rows with fewer columns.
    :param valid_data_types: If True, include rows with valid data types; otherwise,
        include rows with incorrect data types.
    :param valid_row_prob: Probability of generating a valid row (0.0 to 1.0).
    :return: The CSV content as a BytesIO object.
    """
    valid_rows = []
    invalid_rows = []

    for _ in range(num_rows):
        date = datetime.now().strftime("%Y-%m-%d")
        txn_type = random.choice(["income", "expense"])
        amount = round(random.uniform(10, 1000), 2)
        memo = random.choice(["Groceries", "Salary", "Rent", "Miscellaneous"])
        if valid_column_no:
            if not valid_data_types and random.random() >= valid_row_prob:
                invalid_rows.append([date, txn_type, "invalid_amount", memo])
            else:
                valid_rows.append([date, txn_type, amount, memo])
        else:
            if not valid_data_types and random.random() >= valid_row_prob:
                invalid_rows.append([date, txn_type, "invalid_amount"])
            else:
                invalid_rows.append([date, txn_type, amount])

    all_rows = valid_rows + invalid_rows
    random.shuffle(all_rows)

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerows(all_rows)

    csv_bytes = output.getvalue().encode("utf-8")

    bytes_io_output = io.BytesIO(csv_bytes)

    return bytes_io_output


def test_get_report():
    """
    Test the /report/ endpoint to ensure it returns valid financial data.
    """
    response = client.get("/report/")
    assert response.status_code == 200
    data = response.json()
    assert "gross_revenue" in data
    assert "expense" in data
    assert "net_revenue" in data
    assert isinstance(data["gross_revenue"], float)
    assert isinstance(data["expense"], float)
    assert isinstance(data["net_revenue"], float)


def test_post_transactions_with_correct_csv():
    """
    Test the /transactions/ endpoint to ensure a
    valid CSV can be uploaded and processed.
    """

    csv_content = generate_random_csv(1000)

    files = {"file": ("transactions.csv", csv_content, "text/csv")}

    response = client.post("/transactions/", files=files)
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "CSV received and processed"


def test_post_transactions_with_invalid_column_numbers():
    """
    Test the /transactions/ endpoint to ensure that CSV
    is still processed even if some rows have invalid number
    of columns.
    """
    csv_content = generate_random_csv(1000, valid_column_no=False, valid_row_prob=0.5)

    files = {"file": ("transactions.csv", csv_content, "text/csv")}

    response = client.post("/transactions/", files=files)
    assert response.status_code == 200
    data = response.json()
    data = response.json()
    assert data["message"] == "CSV received and processed"


def test_post_transactions_with_invalid_data_types():
    """
    Test the /transactions/ endpoint to ensure that CSV
    is still processed even if some rows have invalid data types
    of columns.
    """
    csv_content = generate_random_csv(1000, valid_data_types=False, valid_row_prob=0.5)

    files = {"file": ("transactions.csv", csv_content, "text/csv")}

    response = client.post("/transactions/", files=files)
    assert response.status_code == 200
    data = response.json()
    data = response.json()
    assert data["message"] == "CSV received and processed"


def test_post_transactions_with_invalid_column_numbers_data_types():
    """
    Test the /transactions/ endpoint to ensure that CSV
    is still processed even if some rows have invalid data types
    of columns.
    """
    csv_content = generate_random_csv(
        1000, valid_column_no=False, valid_data_types=False, valid_row_prob=0.5
    )

    files = {"file": ("transactions.csv", csv_content, "text/csv")}

    response = client.post("/transactions/", files=files)
    assert response.status_code == 200
    data = response.json()
    data = response.json()
    assert data["message"] == "CSV received and processed"


def test_post_transactions_invalid_file():
    """
    Test the /transactions/ endpoint to ensure an error is
    returned when uploading a non-CSV file.
    """
    files = {"file": ("transactions.txt", "This is not a CSV", "text/plain")}

    response = client.post("/transactions/", files=files)
    assert response.status_code == 400
    data = response.json()
    assert "error" in data
    assert data["error"] == "The file must be a CSV file"

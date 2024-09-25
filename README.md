# Canonical Assessment Summer Break

## Environment Setup

This project uses poetry for dependency management. You can install poetry by following this link - https://python-poetry.org/docs/#installation.
If not, you can also used the built-in Dockerfile to run this app inside a docker container, I know this is a overkill but I didn't wanna use pip and venvs for this project as that takes time and poetry is super simple and fast for iteration.

If you want to use docker instead, make sure docker is installed on your machine - https://docs.docker.com/engine/install/

## Dependency installation

If you are using poetry, you can run the following command in the project root directory:

```bash
poetry install
```

If you want to use docker, you need to build the docker image:

```bash
docker build -t canonical .
```

## Running the API server

The API server is built using fastAPI. Use the following command to run the API server:

```bash
poetry run fastapi dev src/main.py --host 0.0.0.0 --port 5000
```

This starts up an API server on port 5000 and you can visit [http://localhost:5000](http://localhost:5000/docs) to look at the APIs that the API server supports(according to INSTRUCTIONS.md).

If you're using docker, run the following command to spin up the API server.

```bash
docker run -it -p 5000:5000 canonical poetry run fastapi dev src/main.py --host 0.0.0.0 --port 5000
```

### Running tests

I wrote some basic tests(with the help of ChatGPT for generating a random CSV with false data). To run those tests, you can run the following command in the project root directory:

```bash
poetry run pytest
```

If you are using docker, run this command:

```bash
docker run -it canonical poetry run pytest
```

## Solution context

The API server takes in a CSV file of the format, `Date, Type, Amount($), Memo` and then calculates the fields, `gross revenue, expenses, and net revenue`.

It handles the following edge cases that I could come up with for which I have written tests as well-

-   Uploading a non-csv file
-   Uploading a csv file but with wrong data types(it ignores the rows that have the wrong data type)
-   Uploading a csv file but with arbitrary number of columns(it ignores the rows that have wrong column number, 4 in this case)
-   Uploading a csv with both wrong data types and arbitrary number of columns

## Shortcomings

Some shortcomings I can think of -

-   If the CSV is huge, it might cause performance issues because right now my solution goes row by row to validate the CSV.
-   I use pandas to calculate the aggregate after doing the validation. This is fine for small CSVs but iterating over the CSV twice is avoidable.
-   Again, processing of the huge CSV can be delegated to a separate process instead of doing the processing in the same API server process.

## Additional Time

If I had additional time, I would probably work on the shortcomings mentioned and also try and come up with more edge cases then I currently have.

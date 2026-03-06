import pandas as pd
from sqlalchemy import create_engine, text
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware

class DataBaseConnector:
    def __init__(self, username, password, host, port, db_name):
        self.url = f"mysql+pymysql://{username}:{password}@{host}:{port}/{db_name}"

    def get_engine(self):
        return create_engine(self.url, pool_pre_ping=True)

class DataLoader:
    def __init__(self, engine):
        self.engine = engine

    def load_csv_to_db(self, df, table_name):

        try:
            with self.engine.begin() as conn:
                df.to_sql(
                    table_name,
                    con=conn,
                    if_exists="append",
                    index=False,
                    chunksize=1000,
                    method="multi"
                )

            return {
                "status": "success",
                "rows_loaded": len(df),
                "table": table_name
            }

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

class DataFetcher:
    def __init__(self, engine):
        self.engine = engine

    def fetch_all(self, table_name):

        try:
            query = text(f"SELECT * FROM {table_name}")

            with self.engine.connect() as conn:
                result = conn.execute(query)
                columns = result.keys()
                rows = result.fetchall()

            data = [dict(zip(columns, row)) for row in rows]

            if not data:
                raise HTTPException(status_code=404, detail="No data found")

            return data

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))


app = FastAPI(title="Trade Data API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

db_engine = DataBaseConnector(
    username="root",
    password="root",
    host="localhost",
    port=3306,
    db_name="tc_trades_db"
).get_engine()


loader = DataLoader(db_engine)
fetcher = DataFetcher(db_engine)

@app.post("/upload-csv")
async def upload_csv(
    table_name: str,
    file: UploadFile = File(...)
):
    """
    Upload CSV file and load data into MySQL
    """

    try:

        if not file.filename.endswith(".csv"):
            raise HTTPException(status_code=400, detail="Only CSV files allowed")

        df = pd.read_csv(file.file)

        result = loader.load_csv_to_db(df, table_name)

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/fetch-data")
def fetch_data(table_name: str, from_date: str = None, to_date: str = None):

    try:

        if from_date and to_date:
            query = text(
                f"""
                SELECT * FROM {table_name}
                WHERE DATE(trade_date) BETWEEN :from_date AND :to_date
                """
            )
            params = {"from_date": from_date, "to_date": to_date}

        elif to_date:
            query = text(
                f"""
                SELECT * FROM {table_name}
                WHERE DATE(trade_date) = :to_date
                """
            )
            params = {"to_date": to_date}

        else:
            query = text(f"SELECT * FROM {table_name}")
            params = {}

        with db_engine.connect() as conn:
            result = conn.execute(query, params)
            columns = result.keys()
            rows = result.fetchall()

        data = [dict(zip(columns, row)) for row in rows]

        return data

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
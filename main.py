import pandas as pd
from sqlalchemy import create_engine, text
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

class DataBaseConnector:
    def __init__(self, username, password, host, port, db_name):
        self.url = (
            f"mysql+pymysql://{username}:{password}@{host}:{port}/{db_name}"
        )

    def get_engine(self):
        return create_engine(self.url, pool_pre_ping=True)


class DataLoader:
    def __init__(self, engine, file_path, table_name):
        self.engine = engine
        self.file_path = file_path
        self.table_name = table_name

    def load_csv_to_db(self, file_path, table_name):
        df = pd.read_csv(file_path)

        with self.engine.begin() as conn:
            df.to_sql(
                table_name,
                con=conn,
                if_exists="replace",
                index=False
            )


class DataFetcher:
    def __init__(self, engine):
        self.engine = engine

    def fetch_all(self, table_name):
        sql = text(f"SELECT * FROM {table_name}")

        with self.engine.connect() as conn:
            result = conn.execute(sql)
            columns = result.keys()
            rows = result.fetchall()

        return [dict(zip(columns, row)) for row in rows]


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

file_name = "C:\\Users\\AbhishekSiddagalla\\EC\\TC_Dashboard\\dataset\\ods_trades_20251117.csv"
table = "tc_trades"

loader = DataLoader(
    engine=db_engine,
    file_path=file_name,
    table_name=table
)
fetcher = DataFetcher(db_engine)

@app.post("/load-data")
def load_data():
    loader.load_csv_to_db(file_name, table)
    return {"status": "success"}


@app.get("/fetch-data")
def fetch_data(table_name: str):
    data = fetcher.fetch_all(table_name)

    if not data:
        raise HTTPException(status_code=404, detail="No data found")

    return data

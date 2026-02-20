export async function fetchTradeDataset() {
  const res = await fetch(
    "http://127.0.0.1:8000/fetch-data?table_name=tc_trades",
  );

  if (!res.ok) {
    throw new Error(`API failed: ${res.status}`);
  }
  return await res.json();
}

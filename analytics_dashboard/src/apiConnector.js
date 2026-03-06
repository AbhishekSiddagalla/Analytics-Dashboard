export async function fetchTradeDataset(fromDate, toDate) {
  let url = `http://127.0.0.1:8000/fetch-data?table_name=trades`;

  if (fromDate && toDate) {
    url += `&from_date=${fromDate}&to_date=${toDate}`;
  } else if (toDate) {
    url += `&to_date=${toDate}`;
  }

  const res = await fetch(url);

  if (!res.ok) {
    throw new Error(`API failed: ${res.status}`);
  }

  return await res.json();
}

from fastapi import FastAPI
import uvicorn
import os
import json

from google.oauth2 import service_account
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import RunReportRequest, DateRange, Dimension, Metric

app = FastAPI()

# ID della proprietà GA4 (sostituisci con il tuo)
PROPERTY_ID = "355446183"

# Credenziali lette dalla variabile di ambiente (che hai caricato su Railway)
service_account_info = json.loads(os.getenv("GOOGLE_APPLICATION_CREDENTIALS_JSON"))
credentials = service_account.Credentials.from_service_account_info(service_account_info)
client = BetaAnalyticsDataClient(credentials=credentials)


@app.get("/")
def root():
    return {
        "status": "Online",
        "message": "API attiva dal tuo GPT con Railway 🚀"
    }

@app.get("/kpi")
def get_kpi():
    request = RunReportRequest(
        property=f"properties/{PROPERTY_ID}",
        dimensions=[Dimension(name="date")],
        metrics=[
            Metric(name="sessions"),
            Metric(name="totalUsers")
        ],
        date_ranges=[DateRange(start_date="30daysAgo", end_date="today")]
    )

    response = client.run_report(request)
    
    # Parsing dei dati ricevuti
    analytics_data = []
    for row in response.rows:
        analytics_data.append({
            "date": row.dimension_values[0].value,
            "sessions": int(row.metric_values[0].value),
            "users": int(row.metric_values[1].value)
        })
    
    return analytics_data

# Avvia il server (Railway usa host 0.0.0.0)
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000)

from fastapi import FastAPI, HTTPException
from pymongo import MongoClient
from fastapi.responses import JSONResponse
import os
from datetime import datetime

app = FastAPI()

# Get MongoDB cluster URL from environment variable
mongodb_url = os.getenv("MONGODB_URL", "mongodb+srv://devteam:Zagateam2023*@applicationcluster.tvbngn1.mongodb.net/test")

# Establish MongoDB connection
metric_client = MongoClient(mongodb_url)
metric_db = metric_client["OtelMetric"]
metric_collection = metric_db["MetricDTO"]

@app.get("/get_all_metric_data")
async def get_all_metric_data():
    try:
        all_metric_data = metric_collection.find()

        metric_data_list = []
        for metric_doc in all_metric_data:
            try:
                date_value = metric_doc["date"]
            except KeyError as e:
                raise HTTPException(status_code=500, detail={"error": f"Missing or invalid 'date' field: {e}"})
                
            formatted_metric_data = {
                "cpuUsage": metric_doc["cpuUsage"],
                "memoryUsage": metric_doc["memoryUsage"],
                "serviceName": metric_doc["serviceName"],
                "date": date_value.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
            }
            metric_data_list.append(formatted_metric_data)

        # Return data as JSONResponse
        return JSONResponse(content=metric_data_list)
    except Exception as e:
        raise HTTPException(status_code=500, detail={"error": str(e)})

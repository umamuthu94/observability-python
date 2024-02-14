

from fastapi import FastAPI, HTTPException
from pymongo import MongoClient
from bson import json_util
from typing import List
from fastapi.encoders import jsonable_encoder
from fastapi import Depends
from fastapi.responses import JSONResponse
from fastapi import HTTPException

# from fastapi import Depends
from datetime import datetime
# from fastapi.encoders import jsonable_encoder

app = FastAPI()

metric_client = MongoClient("mongodb://localhost:27017")
metric_db = metric_client["OtelMetric"]
metric_collection = metric_db["MetricDTO"]

# Classes definition for Metrics
class MetricData:
    def __init__(self, cpu_usage, memory_usage, service_name, date=None):
        self.cpu_usage = cpu_usage
        self.memory_usage = memory_usage
        self.service_name = service_name
        self.date = date.isoformat() if date else datetime.utcnow()


# FastAPI route to store metric data
@app.post("/store_metric_data")
async def store_metric_data(data: dict):
    try:
        metric_data = MetricData(
            cpu_usage=data['cpuUsage'],
            memory_usage=data['memoryUsage'],
            service_name=data['serviceName']
        )

        # Format date in the required structure
        formatted_date = metric_data.date.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"

        # Create the final structure for MongoDB
        final_metric_data = {
            "cpuUsage": metric_data.cpu_usage,
            "memoryUsage": metric_data.memory_usage,
            "serviceName": metric_data.service_name,
            "date": {"$date": formatted_date}
        }

        # Insert the metric data into MongoDB
        result = metric_collection.insert_one(final_metric_data)

        # Use jsonable_encoder to convert the response to JSON-compatible format
        response_data = jsonable_encoder(final_metric_data, exclude={"_id"})

        return response_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



from fastapi import HTTPException

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
                "date": date_value
            }
            metric_data_list.append(formatted_metric_data)

        return metric_data_list
    except Exception as e:
        raise HTTPException(status_code=500, detail={"error": str(e)})


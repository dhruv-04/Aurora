import uuid
import random
import time
import json
from datetime import datetime, timezone
from google.cloud import pubsub_v1 
from dotenv import load_dotenv
import os

load_dotenv()

PROJECT_ID = os.getenv("GCP_PROJECT_ID")
TOPIC_ID = os.getenv("PUBSUB_TOPIC_ID")         
CRITICAL_ANOMALY_PROBABILITY = 0.04 

# Normal and Anomaly Ranges
HR_NORMAL_SLEEP = (55, 75)
HR_NORMAL_ACTIVE = (80, 110)
O2_NORMAL_RANGE = (96.0, 99.5) 
O2_CRITICAL_RANGE = (88.0, 92.0)
HR_ANOMALY = (115, 140)

publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path(PROJECT_ID, TOPIC_ID)

def generate_user_id() -> list:
    uuids = [str(uuid.uuid4()) for _ in range(10)]
    return uuids
UUIDS = generate_user_id()

def get_current_activity():
    hour = datetime.now(timezone.utc).hour
    if 23 <= hour or hour < 7:
        return "Sleeping"
    else:
        return random.choice(["Active", "Resting", "Active"])

def generate_vitals():
    """Generates a single, realistic vital signs payload for a random patient."""
    user_id = random.choice(UUIDS)
    timestamp = datetime.now(timezone.utc).isoformat() 
    activity_state = get_current_activity()
    is_anomaly_flag = False
    
    # Generate Vitals based on State
    if activity_state == "Sleeping":
        heart_rate = random.randint(*HR_NORMAL_SLEEP)
        if random.random() < CRITICAL_ANOMALY_PROBABILITY:
            is_anomaly_flag = True
            heart_rate = random.randint(*HR_ANOMALY)
            blood_oxygen = round(random.uniform(*O2_CRITICAL_RANGE), 1)
        else:
            blood_oxygen = round(random.uniform(*O2_NORMAL_RANGE), 1)

    else: # Active or Resting
        heart_rate = random.randint(*HR_NORMAL_ACTIVE)
        blood_oxygen = round(random.uniform(*O2_NORMAL_RANGE), 1)

    # Final Payload
    data_payload = {
        "userid": user_id,
        "timestamp": timestamp, 
        "heart_rate": heart_rate,
        "blood_oxygen": blood_oxygen,
        "activity_state": activity_state,
        "is_anomaly_flag": is_anomaly_flag
    }
    return data_payload

def simulate_and_push():
    vitals = generate_vitals()
    
    json_data = json.dumps(vitals)
    data_bytes = json_data.encode("utf-8")
    
    try:
        future = publisher.publish(topic_path, data_bytes)
        message_id = future.result()
        
        if vitals["is_anomaly_flag"]:
            print(f"🚨 PUSHED ANOMALY (ID: {message_id}) for {vitals['userid'][:8]}... HR: {vitals['heart_rate']}")
        else:
            print(f"Pushed Normal ({vitals['activity_state']}) for {vitals['userid'][:8]}... HR: {vitals['heart_rate']}")
            
    except Exception as e:
        print(f"--- FAILED TO PUBLISH MESSAGE --- Error: {e}")


if __name__ == "__main__":
    
    print(f"--- Aurora Vital Sign Publisher Starting (Project: {PROJECT_ID}) ---")
    print("Pushing data every ~1 second. Ctrl+C to stop.")
    print("-" * 60)
    
    try:
        while True:
            simulate_and_push()
            time.sleep(random.uniform(0.9, 1.1)) 
            
    except KeyboardInterrupt:
        print("\nSimulator gracefully stopped.")
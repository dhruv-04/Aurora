from datetime import datetime, timezone
import uuid
import random
import time
import json

# COnfiguration to be used by simulation
# Normal and Anomaly Ranges
HR_NORMAL_SLEEP = (55, 75)
HR_NORMAL_ACTIVE = (80, 110)
O2_NORMAL_RANGE = (96.0, 99.5) 
O2_CRITICAL_RANGE = (88.0, 92.0)
HR_ANOMALY = (115, 140)
CRITICAL_ANOMALY_PROBABILITY = 0.04 # 4% chance of a high-severity spike

# --- Helper Functions ---

def generate_user_id() -> list:
    """Generates a list of 10 unique UUIDs to simulate different patients."""
    uuids = []
    for _ in range(10):
        uuids.append(str(uuid.uuid4()))
    return uuids

# Generate the list of IDs once
UUIDS = generate_user_id()

def get_current_activity():
    """
    Simulates the wearable determining if the user is sleeping or active/resting based on time.
    """
    hour = datetime.now(timezone.utc).hour
    # Assume sleeping between 11 PM (23) and 7 AM (7)
    if 23 <= hour or hour < 7:
        return "Sleeping"
    else:
        # Simulate active/resting state during the day
        return random.choice(["Active", "Resting", "Active"])

# --- Main Simulation Logic ---

def generate_simulation():
    """
    Generates a single, realistic vital signs payload for a random patient.
    Anomaly logic is applied based on activity state.
    """
    
    # 1. Select a random patient
    user_id = random.choice(UUIDS)
    timestamp = datetime.now(timezone.utc).isoformat()
    activity_state = get_current_activity()
    
    is_anomaly_flag = False
    
    # Initialize values
    heart_rate = random.randint(70, 90)
    blood_oxygen = round(random.uniform(*O2_NORMAL_RANGE), 1)

    # 2. Apply rules based on activity state
    if activity_state == "Sleeping":
        # Sleeping HR is lower
        heart_rate = random.randint(*HR_NORMAL_SLEEP)
        
        # Anomaly Check: High HR during sleep
        if random.random() < CRITICAL_ANOMALY_PROBABILITY:
            is_anomaly_flag = True
            heart_rate = random.randint(*HR_ANOMALY)
            blood_oxygen = round(random.uniform(*O2_CRITICAL_RANGE), 1) # Drop SpO2 during crisis

    elif activity_state == "Active":
        # Active HR is higher
        heart_rate = random.randint(*HR_NORMAL_ACTIVE)

    # 3. Create the final payload (must match your planned format)
    data_payload = {
        "user_id": user_id,
        "timestamp": timestamp,
        "heart_rate": heart_rate,
        "blood_oxygen": blood_oxygen,
        "activity_state": activity_state,
        "is_anomaly_flag": is_anomaly_flag
    }
    
    return data_payload

# --- Run the Simulation ---

if __name__ == "__main__":
    
    print("--- Starting Aurora Vital Sign Simulator (Ctrl+C to stop) ---")
    
    try:
        while True:
            vitals = generate_simulation()
            
            # Print the resulting JSON payload
            json_output = json.dumps(vitals, indent=None)
            
            # Highlight critical events for easy visualization
            if vitals["is_anomaly_flag"]:
                print(f"🚨 CRITICAL ANOMALY: {json_output}")
            else:
                print(f"Normal ({vitals['activity_state']}): {json_output}")
            
            # Generate data roughly every second
            time.sleep(random.uniform(0.9, 1.1)) 
            
    except KeyboardInterrupt:
        print("\nSimulator gracefully stopped.")
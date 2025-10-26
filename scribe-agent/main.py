from pydantic import BaseModel, validate_call, ValidationError
from datetime import datetime
from flask import Flask, request, jsonify
from enum import Enum
import uuid
import os
from google.cloud import firestore

class ActivityStatus(Enum):
    SLEEPING='Sleeping'
    RESTING='Resting'
    ACTIVE='Active'

class VitalPayload(BaseModel):
    userid: uuid.UUID
    timestamp: datetime
    heart_rate: int
    blood_oxygen: float
    activity_state: ActivityStatus
    is_anomaly_flag: bool


db = firestore.Client()

@validate_call
def pushAsPublisher(payload: VitalPayload):
    try:
        #mock the push into the firestore
        data = payload.model_dump(mode="json")
        userIdString = str(payload.userid)

        docRef = db.collection('vital_history').document(userIdString).collection("readings").document()
        docRef.set(data)

        print(f"[SCRIBE] Data successfully logged for user {userIdString}.")
        return True
    except Exception as e:
        # ... (Handle internal Firestore errors)
        raise Exception(f"Firestore write failed: {e}")

#create a flask app
app = Flask(__name__)

@app.route('/health', methods=['GET'])
def health_check():
    return "Health good", 200


@app.route('/api/scribe', methods=["POST"])
def scribe():
    try:
        payload = request.get_json()
        if payload is None:
            return jsonify({"message": "[SCRIBE] The request is malformed."}), 400
        pushAsPublisher(payload)
        return jsonify({ "message": "Payload successful!" }), 201
    except ValidationError as e:
        print(f"[SCRIBE] The validation failed. Schema was malformed.")
        return jsonify({ "message": "Validation Error occured." }), 400
    except Exception as e:
        print(f"Error occured.")
        return jsonify({ "message": f"Error occured : {e}" }), 400

# app.run(debug=True)
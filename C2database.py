import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

cred = credentials.Certificate("dir_firebase/databasestore.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': "https://studentdata-e92be-default-rtdb.firebaseio.com/"
})

ref = db.reference('students')

data = {
    "CPC205020":
        {
            "fist_name": "Pon", 
            "last_name": "Sokphal",
            "major": "Information Technology",
            "fuculity": "Dien Tu",  
            "address": "Thai Nguyen",          
            "email": "cpc205020@tnut.edu.vn",
            "last_time_scan": "2024-01-01 00:00:00",
            "acadimac_year": "2025",
            "total_attendance": "0"            
        },
    "CPC205019":
        {
            "fist_name": "Mong Da", 
            "last_name": "Pich",
            "major": " Eletraction",
            "fuculity": "Dien",  
            "address": "Siem Reap",          
            "email": "cpc205019@tnut.edu.vn",
            "last_time_scan": "2024-01-01 00:00:00",
            "acadimac_year": "2025",
            "total_attendance": "0"            
        },
    "CPC205013":
        {
            "fist_name": "Veng Ann", 
            "last_name": "Kun",
            "major": "Information Technology",
            "fuculity": "Dien Tu",  
            "address": "Thai Nguyen",          
            "email": "cpc205013@tnut.edu.vn",
            "last_time_scan": "2024-01-01 00:00:00",
            "acadimac_year": "2025",
            "total_attendance": "0"            
        }
}


for key, value in data.items():
    ref.child(key).set(value)
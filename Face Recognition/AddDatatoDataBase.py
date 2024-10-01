import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': "https://face-recognition-1bf72-default-rtdb.firebaseio.com/"
})

ref = db.reference('Students')

data = {
    "321654":
        {
            "name": "Test Test",
            "major": "Computer Science",
            "binusian_year": 2027,
            "total_attendance":6,
            "standing": "G",
            "semester": 3,
            "last_attendance_time": "2022-12-11 00:54:34"
            #key : value
        },

    "852741":
        {
            "name": "Emily Blunt",
            "major": "Design Interior",
            "binusian_year": 2028,
            "total_attendance":6,
            "standing": "G",
            "semester": 4,
            "last_attendance_time": "2022-12-11 00:54:34"
            #key : value
        },

    "963852":
        {
            "name": "Elon Musk",
            "major": "Digital Business Innovation",
            "binusian_year": 2027,
            "total_attendance":6,
            "standing": "G",
            "semester": 5,
            "last_attendance_time": "2022-12-11 00:54:34"
            #key : value
        },

    "2702352250":
        {
            "name": "Theona Arlinton",
            "major": "Computer Science",
            "binusian_year": 2027,
            "total_attendance":4,
            "standing": "G",
            "semester": 3,
            "last_attendance_time": "2022-12-11 00:54:34"
            #key : value
        },

    "2702343523":
        {
            "name": "Pazella Mutia Reflin",
            "major": "Computer Science",
            "binusian_year": 2027,
            "total_attendance":5,
            "standing": "G",
            "semester": 3,
            "last_attendance_time": "2022-12-11 00:54:34"
            #key : value
        },

    "2702228892":
        {
            "name": "Nelson Ferdinand Wangsaputra",
            "major": "Computer Science",
            "binusian_year": 2027,
            "total_attendance":5,
            "standing": "G",
            "semester": 3,
            "last_attendance_time": "2022-12-11 00:54:34"
            #key : value
        }
}

for key,value in data.items():
    ref.child(key).set(value)
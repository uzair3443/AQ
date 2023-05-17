import firebase_admin
from firebase_admin import credentials, messaging
from firebase_admin import db
from django.shortcuts import render
from twilio.rest import Client
from django.conf import settings
from django.db import connection

# Initialize the Firebase app and database
cred = credentials.Certificate('C:/Users/DELL/Desktop/key/aq.json')
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://my-project-191388-default-rtdb.firebaseio.com'
})
ref = db.reference('/Users')

def index(request):
    users_snapshot = ref.get()

    users_data = []
    for user_id, user_data in users_snapshot.items():
        address = user_data.get('Address')
        email = user_data.get('Email')
        name = user_data.get('Name')
        phone_number = user_data.get('PhoneNumber')

        data = user_data.get('data')
        latest_entry = None
        if data:
            # Get the latest entry from the data
            latest_entry_id = max(data.keys())
            latest_entry = data.get(latest_entry_id)

        user_entry = {
            'id': user_id,
            'address': address,
            'email': email,
            'name': name,
            'phone_number': phone_number,
            'latest_entry': latest_entry
        }
        users_data.append(user_entry)

    context = {
        'users': users_data
    }
    return render(request, "dashboard.html", context)

def chart(request):
    users_snapshot = ref.get()

    users_data = []
    for user_id, user_data in users_snapshot.items():
        address = user_data.get('Address')
        email = user_data.get('Email')
        name = user_data.get('Name')
        phone_number = user_data.get('PhoneNumber')

        # Retrieve user data
 
        # ...

        # Retrieve temperature, humidity, CO2, CO, NO2, SO2 values
        temperature = 0.0
        humidity = 0.0
        co2 = 0
        co = 0
        no2 = 0
        so2 = 0

        if user_data['data']:
            latest_entry = max(user_data['data'].values(), key=lambda entry: entry['timestamp'])
            temperature = latest_entry.get('temperature', 0.0)
            humidity = latest_entry.get('humidity', 0.0)
            co2 = latest_entry.get('CO2', 0)
            co = latest_entry.get('CO', 0)
            no2 = latest_entry.get('NO2', 0)
            so2 = latest_entry.get('SO2', 0)

        user_entry = {
            'id': user_id,
            'address': address,
            'email': email,
            'name': name,
            'phone_number': phone_number,
            'temperature': temperature,
            'humidity': humidity,
            'co2': co2,
            'co': co,
            'no2': no2,
            'so2': so2
        }
        users_data.append(user_entry)

    context = {
        'users': users_data
    }
    return render(request, "chart.html", context)

def send_sms(request):
    if request.method == 'POST':
        user_name = request.POST.get('user_name')
        message = request.POST.get('message')
        
        # Retrieve user's phone number from Firebase based on the user name
         # Initialize the Firebase app
        
         # Assuming '/users' is the reference to the user data in Firebase Realtime Database
        user_data = ref.order_by_child('Name').equal_to(user_name).get()  # Retrieve the user data from the database
        
        if user_data:
            for user_id, user_info in user_data.items():
                user_phone_number = user_info['PhoneNumber']
                
                try:
                    # Ensure the phone number is in a valid format
                    formatted_phone_number = "+92" + user_phone_number  # Assuming the phone numbers are from Pakistan (+92)
                    
                    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
                    
                    message = client.messages.create(
                        body=message,
                        from_=settings.TWILIO_PHONE_NUMBER,
                        to=formatted_phone_number
                    )
                    
                    success_message = f"SMS sent to user '{user_name}' successfully."
                    return render(request, 'send_sms.html', {'success_message': success_message})
                except Exception as e:
                    error_message = f"Error occurred while sending SMS: {str(e)}"
                    return render(request, 'send_sms.html', {'error_message': error_message})
        else:
            error_message = f"No user found with name '{user_name}'"
            return render(request, 'send_sms.html', {'error_message': error_message})
    else:
        return render(request, 'send_sms.html')
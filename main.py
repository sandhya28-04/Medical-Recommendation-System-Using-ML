from flask import Flask, render_template, request, redirect, url_for, flash, session
import re

import numpy as np
import pandas as pd
import pickle
from flask import Flask, request, render_template, jsonify
from flask_mysqldb import MySQL
from collections import defaultdict
from textblob import TextBlob
from datetime import datetime
from textblob import TextBlob
from flask_mail import Mail, Message

# flask app
app = Flask(__name__)
app.secret_key = 'secret'
import os
from pathlib import Path
print("Template folder used:", os.path.abspath(app.template_folder))

BASE_DIR = Path(__file__).resolve().parent
DATASET_DIR = BASE_DIR / "dataset"



app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = 'sandhyachaudhary525@gmail.com'
app.config['MAIL_PASSWORD'] = 'otbq xhaa xxvm nqbx'  # Use App Password if using Gmail
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
mail = Mail(app)

   







# MySQL configuration (add here)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'medicine'

# Initialize MySQL extension
mysql = MySQL(app)


# load databasedataset===================================
sym_des = pd.read_csv("dataset/symtoms_df.csv")
precautions = pd.read_csv("dataset/precautions_df.csv")
workout = pd.read_csv("dataset/workout_df.csv")
description = pd.read_csv("dataset/description.csv")
medications = pd.read_csv('dataset/medications.csv')
diets = pd.read_csv("dataset/diets.csv")
hospitals_path = DATASET_DIR / "hospitals.csv"
hospitals = pd.read_csv(hospitals_path)
# Build a mapping from disease to its set of symptoms
disease_symptoms = {}
for _, row in sym_des.iterrows():
    disease = row['Disease'].strip()
    for col in ['Symptom_1', 'Symptom_2', 'Symptom_3', 'Symptom_4']:
        symptom = row[col]
        if pd.notna(symptom):
            disease_symptoms.setdefault(disease, set()).add(symptom.strip().lower().replace(' ', '_'))
svc = pickle.load(open('model/svc.pkl','rb'))



# custome and helping functions
#==========================helper funtions================
def extract_map_url(location_field):
    import re
    match = re.search(r'\((https?://[^\)]+)\)', location_field)
    return match.group(1) if match else "#"
def helper(dis):
    desc = description[description['Disease'] == dis]['Description']
    desc = " ".join([w for w in desc])

    pre = precautions[precautions['Disease'] == dis][['Precaution_1', 'Precaution_2', 'Precaution_3', 'Precaution_4']]
    pre = [col for col in pre.values]

    med = medications[medications['Disease'] == dis]['Medication']
    med = [med for med in med.values]

    die = diets[diets['Disease'] == dis]['Diet']
    die = [die for die in die.values]

    wrkout = workout[workout['disease'] == dis]['workout']

    return desc,pre,med,die,wrkout

def get_hospitals_for_disease(disease, user_location):
    matches = hospitals[
        
        (hospitals['Disease'].str.strip().str.lower() == disease.strip().lower()) &
        (hospitals['Location'].str.strip().str.lower().str.contains(user_location.strip().lower()))
    ]
    if matches.empty:
        matches = hospitals[hospitals['Disease'].str.strip().str.lower() == disease.strip().lower()]
        location_note = True
    else:
        location_note = False
    return matches.to_dict('records'), location_note
    if matches.empty:
        matches = hospitals[hospitals['Disease'].str.strip().str.lower() == disease.strip().lower()]
    return matches.to_dict('records')
symptoms_dict = {'itching': 0, 'skin_rash': 1, 'nodal_skin_eruptions': 2, 'continuous_sneezing': 3, 'shivering': 4, 'chills': 5, 'joint_pain': 6, 'stomach_pain': 7, 'acidity': 8, 'ulcers_on_tongue': 9, 'muscle_wasting': 10, 'vomiting': 11, 'burning_micturition': 12, 'spotting_urination': 13, 'fatigue': 14, 'weight_gain': 15, 'anxiety': 16, 'cold_hands_and_feets': 17, 'mood_swings': 18, 'weight_loss': 19, 'restlessness': 20, 'lethargy': 21, 'patches_in_throat': 22, 'irregular_sugar_level': 23, 'cough': 24, 'high_fever': 25, 'sunken_eyes': 26, 'breathlessness': 27, 'sweating': 28, 'dehydration': 29, 'indigestion': 30, 'headache': 31, 'yellowish_skin': 32, 'dark_urine': 33, 'nausea': 34, 'loss_of_appetite': 35, 'pain_behind_the_eyes': 36, 'back_pain': 37, 'constipation': 38, 'abdominal_pain': 39, 'diarrhoea': 40, 'mild_fever': 41, 'yellow_urine': 42, 'yellowing_of_eyes': 43, 'acute_liver_failure': 44, 'fluid_overload': 45, 'swelling_of_stomach': 46, 'swelled_lymph_nodes': 47, 'malaise': 48, 'blurred_and_distorted_vision': 49, 'phlegm': 50, 'throat_irritation': 51, 'redness_of_eyes': 52, 'sinus_pressure': 53, 'runny_nose': 54, 'congestion': 55, 'chest_pain': 56, 'weakness_in_limbs': 57, 'fast_heart_rate': 58, 'pain_during_bowel_movements': 59, 'pain_in_anal_region': 60, 'bloody_stool': 61, 'irritation_in_anus': 62, 'neck_pain': 63, 'dizziness': 64, 'cramps': 65, 'bruising': 66, 'obesity': 67, 'swollen_legs': 68, 'swollen_blood_vessels': 69, 'puffy_face_and_eyes': 70, 'enlarged_thyroid': 71, 'brittle_nails': 72, 'swollen_extremeties': 73, 'excessive_hunger': 74, 'extra_marital_contacts': 75, 'drying_and_tingling_lips': 76, 'slurred_speech': 77, 'knee_pain': 78, 'hip_joint_pain': 79, 'muscle_weakness': 80, 'stiff_neck': 81, 'swelling_joints': 82, 'movement_stiffness': 83, 'spinning_movements': 84, 'loss_of_balance': 85, 'unsteadiness': 86, 'weakness_of_one_body_side': 87, 'loss_of_smell': 88, 'bladder_discomfort': 89, 'foul_smell_of urine': 90, 'continuous_feel_of_urine': 91, 'passage_of_gases': 92, 'internal_itching': 93, 'toxic_look_(typhos)': 94, 'depression': 95, 'irritability': 96, 'muscle_pain': 97, 'altered_sensorium': 98, 'red_spots_over_body': 99, 'belly_pain': 100, 'abnormal_menstruation': 101, 'dischromic _patches': 102, 'watering_from_eyes': 103, 'increased_appetite': 104, 'polyuria': 105, 'family_history': 106, 'mucoid_sputum': 107, 'rusty_sputum': 108, 'lack_of_concentration': 109, 'visual_disturbances': 110, 'receiving_blood_transfusion': 111, 'receiving_unsterile_injections': 112, 'coma': 113, 'stomach_bleeding': 114, 'distention_of_abdomen': 115, 'history_of_alcohol_consumption': 116, 'fluid_overload.1': 117, 'blood_in_sputum': 118, 'prominent_veins_on_calf': 119, 'palpitations': 120, 'painful_walking': 121, 'pus_filled_pimples': 122, 'blackheads': 123, 'scurring': 124, 'skin_peeling': 125, 'silver_like_dusting': 126, 'small_dents_in_nails': 127, 'inflammatory_nails': 128, 'blister': 129, 'red_sore_around_nose': 130, 'yellow_crust_ooze': 131}
diseases_list = {15: 'Fungal infection', 4: 'Allergy', 16: 'GERD', 9: 'Chronic cholestasis', 14: 'Drug Reaction', 33: 'Peptic ulcer diseae', 1: 'AIDS', 12: 'Diabetes ', 17: 'Gastroenteritis', 6: 'Bronchial Asthma', 23: 'Hypertension ', 30: 'Migraine', 7: 'Cervical spondylosis', 32: 'Paralysis (brain hemorrhage)', 28: 'Jaundice', 29: 'Malaria', 8: 'Chicken pox', 11: 'Dengue', 37: 'Typhoid', 40: 'hepatitis A', 19: 'Hepatitis B', 20: 'Hepatitis C', 21: 'Hepatitis D', 22: 'Hepatitis E', 3: 'Alcoholic hepatitis', 36: 'Tuberculosis', 10: 'Common Cold', 34: 'Pneumonia', 13: 'Dimorphic hemmorhoids(piles)', 18: 'Heart attack', 39: 'Varicose veins', 26: 'Hypothyroidism', 24: 'Hyperthyroidism', 25: 'Hypoglycemia', 31: 'Osteoarthristis', 5: 'Arthritis', 0: '(vertigo) Paroymsal  Positional Vertigo', 2: 'Acne', 38: 'Urinary tract infection', 35: 'Psoriasis', 27: 'Impetigo'}

# # Initialize the TextBlob object for spelling correction
def correct_spelling(symptom):
    # Correct the spelling of a single symptom
    blob = TextBlob(symptom)
    return str(blob.correct())

symptom_mapping = defaultdict(lambda: "unknown", {
    "itching": ["itching"],
    "skin_rash": ["skin rash", "rash", "dermatitis"],
    "nodal_skin_eruptions": ["nodal skin eruptions", "skin eruptions", "bumps"],
    "continuous_sneezing": ["continuous sneezing", "sneezing"],
    "shivering": ["shivering", "trembling"],
    "chills": ["chills", "cold sensation", "cold"],
    "joint_pain": ["joint pain", "arthralgia", "aching joints"],
    "stomach_pain": ["stomach pain", "abdominal pain", "belly ache"],
    "acidity": ["acidity", "heartburn", "acid reflux"],
    "ulcers_on_tongue": ["ulcers on tongue", "tongue ulcers", "mouth sores"],
    "muscle_wasting": ["muscle wasting", "muscle loss"],
    "vomiting": ["vomiting", "emesis", "throwing up"],
    "burning_micturition": ["burning micturition", "burning urination", "painful urination"],
    "spotting_urination": ["spotting urination", "blood in urine", "hematuria"],
    "fatigue": ["fatigue", "tiredness", "exhaustion"],
    "weight_gain": ["weight gain", "increased weight"],
    "anxiety": ["anxiety", "nervousness", "worry"],
    "cold_hands_and_feets": ["cold hands and feet", "cold extremities"],
    "mood_swings": ["mood swings", "emotional changes"],
    "weight_loss": ["weight loss", "decreased weight"],
    "restlessness": ["restlessness", "agitation"],
    "lethargy": ["lethargy", "sluggishness"],
    "patches_in_throat": ["patches in throat", "throat patches", "throat lesions"],
    "irregular_sugar_level": ["irregular sugar level", "unstable glucose", "blood sugar fluctuations"],
    "cough": ["cough", "coughing"],
    "high_fever": ["high fever", "elevated temperature"],
    "sunken_eyes": ["sunken eyes", "hollow eyes"],
    "breathlessness": ["breathlessness", "shortness of breath", "dyspnea"],
    "sweating": ["sweating", "perspiration"],
    "dehydration": ["dehydration", "fluid loss"],
    "indigestion": ["indigestion", "upset stomach"],
    "headache": ["headache", "head pain", "migraine"],
    "yellowish_skin": ["yellowish skin", "jaundice"],
    "dark_urine": ["dark urine"],
    "nausea": ["nausea", "queasiness"],
    "loss_of_appetite": ["loss of appetite", "no appetite", "anorexia"],
    "pain_behind_the_eyes": ["pain behind the eyes", "eye pain"],
    "back_pain": ["back pain", "lower back pain"],
    "constipation": ["constipation", "difficulty passing stool"],
    "abdominal_pain": ["abdominal pain", "belly pain", "stomach ache"],
    "diarrhoea": ["diarrhoea", "loose stools"],
    "mild_fever": ["mild fever", "fever" "low-grade fever"],
    "yellow_urine": ["yellow urine"],
    "yellowing_of_eyes": ["yellowing of eyes", "scleral icterus"],
    "acute_liver_failure": ["acute liver failure", "hepatic failure"],
    "fluid_overload": ["fluid overload", "edema"],
    "swelling_of_stomach": ["swelling of stomach", "abdominal bloating"],
    "swelled_lymph_nodes": ["swelled lymph nodes", "enlarged lymph nodes"],
    "malaise": ["malaise", "general discomfort"],
    "blurred_and_distorted_vision": ["blurred and distorted vision", "blurry vision"],
    "phlegm": ["phlegm", "mucus"],
    "throat_irritation": ["throat irritation", "sore throat"],
    "redness_of_eyes": ["redness of eyes", "bloodshot eyes"],
    "sinus_pressure": ["sinus pressure", "sinus congestion"],
    "runny_nose": ["runny nose", "rhinorrhea"],
    "congestion": ["congestion", "nasal blockage"],
    "chest_pain": ["chest pain", "angina"],
    "weakness_in_limbs": ["weakness in limbs", "limb weakness"],
    "fast_heart_rate": ["fast heart rate", "tachycardia"],
    "pain_during_bowel_movements": ["pain during bowel movements", "painful defecation"],
    "pain_in_anal_region": ["pain in anal region", "anal pain"],
    "bloody_stool": ["bloody stool", "rectal bleeding"],
    "irritation_in_anus": ["irritation in anus", "anal itching"],
    "neck_pain": ["neck pain", "cervical pain"],
    "dizziness": ["dizziness", "lightheadedness"],
    "cramps": ["cramps", "muscle cramps", "spasms"],
    "bruising": ["bruising", "hematoma"],
    "obesity": ["obesity", "overweight"],
    "swollen_legs": ["swollen legs", "leg edema"],
    "swollen_blood_vessels": ["swollen blood vessels", "varicose veins"],
    "puffy_face_and_eyes": ["puffy face and eyes", "facial swelling"],
    "enlarged_thyroid": ["enlarged thyroid", "goiter"],
    "brittle_nails": ["brittle nails", "weak nails"],
    "swollen_extremeties": ["swollen extremities", "swollen arms and legs"],
    "excessive_hunger": ["excessive hunger", "polyphagia"],
    "extra_marital_contacts": ["extra marital contacts", "multiple sexual partners"],
    "drying_and_tingling_lips": ["drying and tingling lips", "lip dryness"],
    "slurred_speech": ["slurred speech", "dysarthria"],
    "knee_pain": ["knee pain", "pain in the knees"],
    "hip_joint_pain": ["hip joint pain", "hip pain"],
    "muscle_weakness": ["muscle weakness", "muscle fatigue"],
    "stiff_neck": ["stiff neck", "neck stiffness"],
    "swelling_joints": ["swelling joints", "joint swelling"],
    "movement_stiffness": ["movement stiffness", "rigidity"],
    "spinning_movements": ["spinning movements", "vertigo"],
    "loss_of_balance": ["loss of balance", "balance problems"],
    "unsteadiness": ["unsteadiness", "lack of balance"],
    "weakness_of_one_body_side": ["weakness of one body side", "hemiparesis"],
    "loss_of_smell": ["loss of smell", "anosmia"],
    "bladder_discomfort": ["bladder discomfort", "bladder pain"],
    "foul_smell_of_urine": ["foul smell of urine", "smelly urine"],
    "continuous_feel_of_urine": ["continuous feel of urine", "urgency to urinate"],
    "passage_of_gases": ["passage of gases", "flatulence"],
    "internal_itching": ["internal itching"],
    "toxic_look_(typhos)": ["toxic look (typhos)", "septic appearance"],
    "depression": ["depression", "low mood"],
    "irritability": ["irritability", "easily annoyed"],
    "muscle_pain": ["muscle pain", "myalgia"],
    "altered_sensorium": ["altered sensorium", "confusion"],
    "red_spots_over_body": ["red spots over body", "rash with red spots"],
    "belly_pain": ["belly pain", "abdominal pain"],
    "abnormal_menstruation": ["abnormal menstruation", "irregular periods"],
    "dischromic_patches": ["dischromic patches", "skin discoloration"],
    "watering_from_eyes": ["watering from eyes", "teary eyes"],
    "increased_appetite": ["increased appetite", "hyperphagia"],
    "polyuria": ["polyuria", "excessive urination"],
    "family_history": ["family history", "genetic predisposition"],
    "mucoid_sputum": ["mucoid sputum", "mucus in sputum"],
    "rusty_sputum": ["rusty sputum", "blood-tinged sputum"],
    "lack_of_concentration": ["lack of concentration", "difficulty focusing"],
    "visual_disturbances": ["visual disturbances", "vision problems"],
    "receiving_blood_transfusion": ["receiving blood transfusion"],
    "receiving_unsterile_injections": ["receiving unsterile injections"],
    # Add more symptoms and their synonyms here
})
import pandas as pd
df = pd.read_csv(hospitals_path)
def make_map_link(row):
    # Use hospital name and location for better accuracy
    query = f"{row['Hospital']} {row['Location'].split('(')[0].strip()}"
    url = f"https://www.google.com/maps/search/?api=1&query={query.replace(' ', '+')}"
    return f"{row['Location'].split('(')[0].strip()} ({url})"
def extract_map_url(location_field):
    match = re.search(r'\((https?://[^\)]+)\)', location_field)
    return match.group(1) if match else "#"

def helper(dis):
    desc = description[description['Disease'] == dis]['Description']
    desc = " ".join([w for w in desc])
    pre = precautions[precautions['Disease'] == dis][['Precaution_1', 'Precaution_2', 'Precaution_3', 'Precaution_4']]
    pre = [col for col in pre.values]
    med = medications[medications['Disease'] == dis]['Medication']
    med = [med for med in med.values]
    die = diets[diets['Disease'] == dis]['Diet']
    die = [die for die in die.values]
    wrkout = workout[workout['disease'] == dis]['workout']
    return desc, pre, med, die, wrkout
def make_direction_link(hospital_row, user_location):
    # Combine hospital name and location for accuracy
    hospital_address = f"{hospital_row['Hospital']} {hospital_row['Location'].split('(')[0].strip()}"
    origin = user_location.replace(' ', '+')
    destination = hospital_address.replace(' ', '+')
    url = f"https://www.google.com/maps/dir/?api=1&origin={origin}&destination={destination}"
    return url


df['Location'] = df.apply(make_map_link, axis=1)
df.to_csv(hospitals_path, index=False)
df = pd.read_csv(hospitals_path)
def get_predicted_value(user_symptoms):
    max_matches = 0
    best_disease = None
    for disease, symptoms in disease_symptoms.items():
        matches = len(set(user_symptoms) & symptoms)
        if matches > max_matches:
            max_matches = matches
            best_disease = disease
    return best_disease if best_disease else "Unknown Disease"

# creating routes========================================
# Helper functions for email verification

# Registration
import random
from flask import session
@app.route("/verify-code", methods=["GET", "POST"])
def verify_code():
    if request.method == "POST":
        code = request.form['code']
        if code == session.get('verification_code'):
            session['code_verified'] = True
            flash("Code verified! Please reset your password.", "success")
            return redirect(url_for('reset_password'))
        else:
            flash("Invalid verification code.", "danger")
    return render_template("verify_code.html")

@app.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        email = request.form['email']
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cur.fetchone()
        cur.close()
        if user:
            verification_code = str(random.randint(100000, 999999))
            session['verification_code'] = verification_code
            session['reset_email'] = email

            msg = Message(
                subject="Code",
                sender=app.config['MAIL_USERNAME'],
                recipients=[email]
            )
            msg.body = f"Subject: Password Reset Verification for Your Medical Recommendation System Account\nEmail Body:\n\nDear User,\n\nThank you for using our Medical Recommendation System. We have received your request to reset your password. Please use the verification code below to proceed with resetting your password:\n\n {verification_code}\n\nYour privacy and security are our top priorities. If you did not request this change, please contact our support team immediately.\n\nWe appreciate your trust in our system and are committed to supporting your health journey with personalized and reliable recommendations.\n\nThank you for being a valued user.\n\nBest regards,\nThe Medical Recommendation System Team"
            try:
                mail.send(msg)
                print("Verification code sent to:", email)  # Debug print
                flash("Verification code sent to your email.", "info")
                return redirect(url_for('verify_code'))
            except Exception as e:
                print("Email send error:", e)  # Debug print
                flash("Failed to send verification code. Please try again.", "danger")
        else:
            print("No user found for email:", email)  # Debug print
            flash("Email not found.", "danger")
    return render_template("forgot_password.html")
@app.route("/reset-password", methods=["GET", "POST"])
def reset_password():
    if not session.get('code_verified'):
        return redirect(url_for('forgot_password'))
    if request.method == "POST":
        new_password = request.form['new_password']
        email = session.get('reset_email')
        cur = mysql.connection.cursor()
        cur.execute("UPDATE users SET password = %s WHERE email = %s", (new_password, email))
        mysql.connection.commit()
        cur.close()
        session.pop('verification_code', None)
        session.pop('reset_email', None)
        session.pop('code_verified', None)
        flash("Password reset successful. Please log in.", "success")
        return redirect(url_for('login'))
    return render_template("reset_password.html")

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        code = request.form.get('code')

        # Username validation
        if not re.match(r'^[A-Za-z][A-Za-z0-9_]*$', username):
            flash('Username must start with a letter and can contain numbers/underscores.')
            return render_template('register.html')

        # Email validation
        if not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            flash('Invalid email address.')
            return render_template('register.html')

        
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE email = %s", (email,))
        account = cur.fetchone()
        if account:
            flash('Email already registered.')
            cur.close()
            return render_template('register.html')

        cur.execute("INSERT INTO users (username, email, password) VALUES (%s, %s, %s)", (username, email, password))
        mysql.connection.commit()
        cur.close()
        flash('Registered successfully! Please log in.')
        return redirect(url_for('login'))

    return render_template('register.html')



# Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE email = %s AND password = %s", (email, password))
        user = cur.fetchone()
        cur.close()
        if user:
    
            session['user'] = user[1]  # username
            print("Login successful, redirecting to interface")
            return redirect(url_for('interface'))
        else:
            flash('Invalid credentials.')
    return render_template('login.html')





# Inside interface (main system page)
@app.route('/interface')
def interface():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('interface.html')
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))
@app.route('/hospitals/<disease>/<user_location>')
def hospitals_for_disease(disease, user_location):
    hospital_recommendations, location_note = get_hospitals_for_disease(disease, user_location)
    for h in hospital_recommendations:
        h['DirectionLink'] = make_direction_link(h, user_location)  # <-- Use this!
    print("Disease:", disease)
    print("User location:", user_location)
    print("Hospital recommendations:", hospital_recommendations)
    return render_template(
        'hospitals.html',
        disease=disease,
        hospital_recommendations=hospital_recommendations,
        location_note=location_note,
        user_location=user_location
    )

# Define a route for the home page
@app.route('/predict', methods=['GET', 'POST'])
def predict():
    if request.method == 'POST':
        import re
        from datetime import datetime
        name = request.form.get('name', '').strip()
        gender = request.form.get('gender')
        location = request.form.get('location')
        symptoms = request.form.get('symptoms')
        birthdate_str = request.form.get('birthdate')
        if not birthdate_str:
            message = "Please enter your birthdate."
            return render_template('index.html', symptom_message=message, name=name, gender=gender, location=location, symptoms=symptoms)
        try:
            birthdate = datetime.strptime(birthdate_str, "%Y-%m-%d")
            if birthdate.year < 1950 or birthdate > datetime.today():
                message = "Date of birth must be between 1950 and today."
                return render_template('index.html', symptom_message=message, name=name, gender=gender, location=location, symptoms=symptoms)
        except Exception:
            message = "Invalid birthdate format."
            return render_template('index.html', symptom_message=message, name=name, gender=gender, location=location, symptoms=symptoms)
        if not name or not re.fullmatch(r'[A-Za-z]+(?: [A-Za-z]+)*', name):
            message = "Name must contain only letters and single spaces (no numbers or special characters)."
            return render_template('index.html', birthdate_message=birthdate_message, name=name, gender=gender, location=location, symptoms=symptoms)
        if not birthdate_str:
            message = "Please enter your birthdate."
            return render_template('index.html', symptom_message=message, name=name, gender=gender, location=location, symptoms=symptoms)

        try:
            birthdate = datetime.strptime(birthdate_str, "%Y-%m-%d")
            today = datetime.today()
            years = today.year - birthdate.year
            months = today.month - birthdate.month
            days = today.day - birthdate.day

            if days < 0:
                months -= 1
                days += (birthdate.replace(month=birthdate.month + 1, day=1) - birthdate.replace(month=birthdate.month, day=1)).days
            if months < 0:
                years -= 1
                months += 12

            age_str = f"{years} years, {months} months, {days} days"
        except Exception as e:
            message = "Invalid birthdate format."
            return render_template('index.html', symptom_message=message, name=name, gender=gender, location=location, symptoms=symptoms)

        print(symptoms)
        if symptoms == "Symptoms":
            message = "Please either write symptoms or you have written misspelled symptoms"
            return render_template('index.html', message=message, name=name, gender=gender, location=location, symptoms=symptoms)
        
        if not symptoms:
            message = "Please enter symptoms."
            return render_template('index.html', message=message, name=name, gender=gender, location=location, symptoms=symptoms) 
        
    
        # Get all unique symptoms from your dataset
        all_symptoms = set()
        for col in ['Symptom_1', 'Symptom_2', 'Symptom_3', 'Symptom_4']:
            all_symptoms.update(sym_des[col].dropna().str.strip().str.lower().str.replace(' ', '_'))
    
        user_symptoms = [s.strip().lower().replace(' ', '_') for s in symptoms.split(',')]
        valid_user_symptoms = [s for s in user_symptoms if s in all_symptoms]
        # Require at least 3 valid symptoms
        if len(valid_user_symptoms) < 3:
            message = "Please enter at least 3 valid symptoms, separated by commas."
            return render_template(
                'index.html',
                symptom_message=message,
                name=name,
                age=age_str,
                gender=gender,
                location=location,
                symptoms=symptoms
            )

        predicted_disease = get_predicted_value(valid_user_symptoms)
        
        # Save to MySQL database
        print("Attempting to save to database...")
        try:
            username = session.get('user')  
            cur = mysql.connection.cursor()
            cur.execute(
                "INSERT INTO user_queries (name, age, gender, location, symptoms, predicted_disease, username) VALUES (%s, %s,%s, %s, %s, %s, %s)",
                (name, age_str, gender, location, symptoms, predicted_disease, username)
            )
            mysql.connection.commit()
            cur.close()
        except Exception as e:
            print("Database error:", e)
        
        dis_des, precautions, medications, rec_diet, workout = helper(predicted_disease)
    
        my_precautions = []
        for i in precautions:
            my_precautions.append(i)
    
        return render_template(
            'index.html',
            name=name,
            age=age_str,
            location=location,
            symptoms=symptoms,
            predicted_disease=predicted_disease,
            dis_des=dis_des,
            my_precautions=my_precautions[0] if my_precautions else "",
            medications=medications,
            my_diet=rec_diet,
            workout=workout
        )
    else:
        return render_template('index.html')
# Removed invalid return statement outside of function
# (No code needed here)


# about view funtion and path


from flask import request, jsonify


# Define qa_pairs globally so it's not re-created on every request
qa_pairs = {
    "what is a normal body temperature": "A normal body temperature is around 98.6°F (37°C), but it can range between 97°F and 99°F and still be considered normal.",
    "what should i do if i have a sore throat": "Rest, stay hydrated, and try warm salt water gargles. If the pain persists or is severe, consult a doctor.",
    "can i take paracetamol for a headache": "Yes, paracetamol is generally safe for treating headaches. Always follow the dosage instructions on the label.",
    "how do i know if i’m dehydrated": "Signs of dehydration include dry mouth, dizziness, dark yellow urine, and fatigue. Drink water regularly to stay hydrated.",
    "which hospital is good": "Some of the best hospitals in your area include Norvic International, Grande International Hospital, and others. Please specify your health problem for a more accurate recommendation.",
    "which hospital is good for heart problems": "For cardiac care, hospitals like Norvic International or Grande International Hospital in Kathmandu are highly recommended.",
    "what is your name": "I am your Health Assistant chatbot.",
    "thank you": "You're welcome! Let me know if you have more questions.",
    "thanks": "You're welcome! Let me know if you have more questions.",
    "what is fungal infection": "Fungal infection is a common skin condition caused by fungi.",
    "what is allergy": "Allergy is an immune system reaction to a substance in the environment.",
    "what is gerd": "GERD (Gastroesophageal Reflux Disease) is a digestive disorder that affects the lower esophageal sphincter.",
    "what is chronic cholestasis": "Chronic cholestasis is a condition where bile flow from the liver is reduced for a prolonged period.",
    "what is drug reaction": "Drug Reaction occurs when the body reacts adversely to a medication.",
    "what is peptic ulcer disease": "Peptic ulcer disease involves sores that develop on the inner lining of the stomach and small intestine.",
    "what is aids": "AIDS (Acquired Immunodeficiency Syndrome) is a disease caused by HIV that weakens the immune system.",
    "what is diabetes": "Diabetes is a chronic condition that affects how the body processes blood sugar.",
    "what is gastroenteritis": "Gastroenteritis is an inflammation of the stomach and intestines, typically caused by a virus or bacteria.",
    "what is bronchial asthma": "Bronchial Asthma is a respiratory condition characterized by inflammation of the airways.",
    "what is hypertension": "Hypertension, or high blood pressure, is a common cardiovascular condition.",
    "what is migraine": "Migraine is a type of headache that often involves severe pain and sensitivity to light and sound.",
    "what is cervical spondylosis": "Cervical spondylosis is a degenerative condition of the cervical spine.",
    "what is paralysis (brain hemorrhage)": "Paralysis (brain hemorrhage) refers to the loss of muscle function due to bleeding in the brain.",
    "what is jaundice": "Jaundice is a yellow discoloration of the skin and eyes, often indicating liver problems.",
    "what is malaria": "Malaria is a mosquito-borne infectious disease affecting humans and other animals.",
    "what is chicken pox": "Chicken pox is a highly contagious viral infection causing an itchy rash.",
    "what is dengue": "Dengue is a mosquito-borne viral infection causing flu-like symptoms.",
    "what is typhoid": "Typhoid is a bacterial infection that can lead to a high fever and gastrointestinal symptoms.",
    "what is hepatitis a": "hepatitis A is a viral liver disease.",
    "what is hepatitis b": "Hepatitis B is a viral infection that attacks the liver.",
    "what is hepatitis c": "Hepatitis C is a viral infection that causes liver inflammation.",
    "what is hepatitis d": "Hepatitis D is a serious liver disease caused by the hepatitis D virus.",
    "what is hepatitis e": "Hepatitis E is a viral infection that causes liver inflammation.",
    "what is alcoholic hepatitis": "Alcoholic hepatitis is inflammation of the liver due to alcohol consumption.",
    "what is tuberculosis": "Tuberculosis is a bacterial infection that primarily affects the lungs.",
    "what is common cold": "Common Cold is a viral infection of the upper respiratory tract.",
    "what is pneumonia": "Pneumonia is an inflammatory condition affecting the air sacs in the lungs.",
    "what is dimorphic hemmorhoids(piles)": "Dimorphic hemmorhoids(piles) is a condition characterized by swollen blood vessels in the rectum.",
    "what is heart attack": "Heart attack is a sudden and severe reduction in blood flow to the heart muscle.",
    "what are varicose veins": "Varicose veins are enlarged, twisted veins that usually appear on the legs.",
    "what is hypothyroidism": "Hypothyroidism is a condition where the thyroid gland doesn't produce enough thyroid hormone.",
    "what is hyperthyroidism": "Hyperthyroidism is a condition where the thyroid gland produces too much thyroid hormone.",
    "what is hypoglycemia": "Hypoglycemia is a condition characterized by abnormally low blood sugar levels.",
    "what is osteoarthristis": "Osteoarthristis is a degenerative joint disease that affects the cartilage in joints.",
    "what is arthritis": "Arthritis is inflammation of one or more joints, causing pain and stiffness.",
    "what is (vertigo) paroymsal positional vertigo": "(Vertigo) Paroxysmal Positional Vertigo is a type of dizziness caused by specific head movements.",
    "what is acne": "Acne is a skin condition that occurs when hair follicles become clogged with oil and dead skin cells.",
    "what is urinary tract infection": "Urinary tract infection is an infection in any part of the urinary system.",
    "what is psoriasis": "Psoriasis is a chronic skin condition characterized by red, itchy, and scaly patches.",
    "what is impetigo": "Impetigo is a highly contagious skin infection causing red sores that can break open.",
    "what diet is recommended for fungal infection": "Antifungal Diet, Probiotics, Garlic, Coconut oil, Turmeric.",
    "what diet is recommended for allergy": "Elimination Diet, Omega-3-rich foods, Vitamin C-rich foods, Quercetin-rich foods, Probiotics.",
    "what diet is recommended for gerd": "Low-Acid Diet, Fiber-rich foods, Ginger, Licorice, Aloe vera juice.",
    "what diet is recommended for chronic cholestasis": "Low-Fat Diet, High-Fiber Diet, Lean proteins, Whole grains, Fresh fruits and vegetables.",
    "what diet is recommended for drug reaction": "Antihistamine Diet, Omega-3-rich foods, Vitamin C-rich foods, Quercetin-rich foods, Probiotics.",
    "what diet is recommended for peptic ulcer disease": "Low-Acid Diet, Fiber-rich foods, Ginger, Licorice, Aloe vera juice.",
    "what diet is recommended for aids": "Balanced Diet, Protein-rich foods, Fruits and vegetables, Whole grains, Healthy fats.",
    "what diet is recommended for diabetes": "Low-Glycemic Diet, Fiber-rich foods, Lean proteins, Healthy fats, Low-fat dairy.",
    "what diet is recommended for gastroenteritis": "Bland Diet, Bananas, Rice, Applesauce, Toast.",
    "what diet is recommended for bronchial asthma": "Anti-Inflammatory Diet, Omega-3-rich foods, Fruits and vegetables, Whole grains, Lean proteins.",
    "what diet is recommended for hypertension": "DASH Diet, Low-sodium foods, Fruits and vegetables, Whole grains, Lean proteins.",
    "what diet is recommended for migraine": "Migraine Diet, Low-Tyramine Diet, Caffeine withdrawal, Hydration, Magnesium-rich foods.",
    "what diet is recommended for cervical spondylosis": "Arthritis Diet, Anti-Inflammatory Diet, Omega-3-rich foods, Fruits and vegetables, Whole grains.",
    "what diet is recommended for paralysis (brain hemorrhage)": "Heart-Healthy Diet, Low-sodium foods, Fruits and vegetables, Whole grains, Lean proteins.",
    "what diet is recommended for jaundice": "Liver-Healthy Diet, Low-fat Diet, Fruits and vegetables, Whole grains, Lean proteins.",
    "what diet is recommended for malaria": "Malaria Diet, Hydration, High-Calorie Diet, Soft and bland foods, Oral rehydration solutions.",
    "what diet is recommended for chicken pox": "Chicken Pox Diet, High-Calorie Diet, Soft and bland foods, Hydration, Protein-rich foods.",
    "what diet is recommended for dengue": "Dengue Diet, Hydration, High-Calorie Diet, Soft and bland foods, Protein-rich foods.",
    "what diet is recommended for typhoid": "Typhoid Diet, High-Calorie Diet, Soft and bland foods, Hydration, Protein-rich foods.",
    "what diet is recommended for hepatitis a": "Hepatitis A Diet, High-Calorie Diet, Soft and bland foods, Hydration, Protein-rich foods.",
    "what diet is recommended for hepatitis b": "Hepatitis B Diet, High-Calorie Diet, Soft and bland foods, Hydration, Protein-rich foods.",
    "what diet is recommended for hepatitis c": "Hepatitis C Diet, High-Calorie Diet, Soft and bland foods, Hydration, Protein-rich foods.",
    "what diet is recommended for hepatitis d": "Hepatitis D Diet, High-Calorie Diet, Soft and bland foods, Hydration, Protein-rich foods.",
    "what diet is recommended for hepatitis e": "Hepatitis E Diet, High-Calorie Diet, Soft and bland foods, Hydration, Protein-rich foods.",
    "what diet is recommended for alcoholic hepatitis": "Liver-Healthy Diet, Low-fat Diet, Fruits and vegetables, Whole grains, Lean proteins.",
    "what diet is recommended for tuberculosis": "TB Diet, High-Calorie Diet, Soft and bland foods, Hydration, Protein-rich foods.",
    "what diet is recommended for common cold": "Cold Diet, Hydration, Warm fluids, Rest, Honey and lemon tea.",
    "what diet is recommended for pneumonia": "Pneumonia Diet, High-Calorie Diet, Soft and bland foods, Hydration, Protein-rich foods.",
    "what diet is recommended for dimorphic hemmorhoids(piles)": "Hemorrhoids Diet, High-Fiber Diet, Hydration, Warm baths, Stool softeners.",
    "what diet is recommended for heart attack": "Heart-Healthy Diet, Low-sodium foods, Fruits and vegetables, Whole grains, Lean proteins.",
    "what diet is recommended for varicose veins": "Varicose Veins Diet, High-Fiber Diet, Fruits and vegetables, Whole grains, Low-sodium foods.",
    "what diet is recommended for hypothyroidism": "Hypothyroidism Diet, Iodine-rich foods, Selenium-rich foods, Fruits and vegetables, Whole grains.",
    "what diet is recommended for hyperthyroidism": "Hyperthyroidism Diet, Low-Iodine Diet, Calcium-rich foods, Selenium-rich foods, Fruits and vegetables.",
    "what diet is recommended for hypoglycemia": "Hypoglycemia Diet, Complex carbohydrates, Protein-rich snacks, Fiber-rich foods, Healthy fats.",
    "what diet is recommended for osteoarthristis": "Arthritis Diet, Anti-Inflammatory Diet, Omega-3-rich foods, Fruits and vegetables, Whole grains.",
    "what diet is recommended for arthritis": "Arthritis Diet, Anti-Inflammatory Diet, Omega-3-rich foods, Fruits and vegetables, Whole grains.",
    "what diet is recommended for (vertigo) paroymsal positional vertigo": "Vertigo Diet, Low-Salt Diet, Hydration, Ginger tea, Vitamin D-rich foods.",
    "what diet is recommended for acne": "Acne Diet, Low-Glycemic Diet, Hydration, Fruits and vegetables, Probiotics.",
    "what diet is recommended for urinary tract infection": "UTI Diet, Hydration, Cranberry juice, Probiotics, Vitamin C-rich foods.",
    "what diet is recommended for psoriasis": "Psoriasis Diet, Anti-Inflammatory Diet, Omega-3-rich foods, Fruits and vegetables, Whole grains.",
    "what diet is recommended for impetigo": "Impetigo Diet, Antibiotic treatment, Fruits and vegetables, Hydration, Protein-rich foods.",
}
@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message', '').lower().strip()
    user_message = str(user_message)
    user_message = re.sub(r'[^\w\s]', '', user_message)

    # 1. Exact match first
    if user_message in qa_pairs:
        return jsonify({'reply': qa_pairs[user_message]})

    # 2. Partial match
    for question, answer in qa_pairs.items():
        q_clean = question.lower().strip()
        if q_clean in user_message or user_message in q_clean:
            return jsonify({'reply': answer})
    # Default reply
    return jsonify({'reply': "I'm here to help with hospital recommendations and health queries related to diet and disease! Please ask your question."})

@app.route('/chatbot')
def chatbot_interface():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('chatbot_interface.html', username=session['user'])
@app.route('/history/<username>')
def user_history(username):
    cur = mysql.connection.cursor()
    cur.execute("SELECT name, age, gender, location, symptoms, predicted_disease FROM user_queries WHERE username = %s ORDER BY id ASC", (username,))
    history = cur.fetchall()
    cur.close()
    return render_template('history.html', history=history, username=username)
@app.route('/users')
def users():
    cur = mysql.connection.cursor()
    cur.execute("SELECT username FROM users")
    users = cur.fetchall()
    cur.close()
    return render_template('users.html', users=users)
@app.route('/history')
def history():
    if 'user' not in session:
        return redirect(url_for('login'))
    username = session['user']
    cur = mysql.connection.cursor()
    cur.execute("SELECT name, age, gender, location, symptoms, predicted_disease FROM user_queries WHERE username = %s ORDER BY id DESC", (username,))
    history = cur.fetchall()
    cur.close()
    return render_template('history.html', history=history, username=username)
@app.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # Simple hardcoded admin credentials (change as needed)
        if username == 'sandhya28' and password == '123456':
            session['admin'] = True
            return redirect(url_for('admin_panel'))
        else:
            flash('Invalid admin credentials.')
    return render_template('admin_login.html')

@app.route('/admin-panel')
def admin_panel():
    if not session.get('admin'):
        return redirect(url_for('admin_login.html'))
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM users")
    users = cur.fetchall()
    cur.execute("SELECT * FROM user_queries")
    queries = cur.fetchall()
    cur.close()
    # Add hospital recommendations for each query
    queries_with_hospitals = []
    for q in queries:
        disease = q[6]  # predicted_disease
        location = q[4] # user location
        # Filter hospitals DataFrame for matching disease and location
        matches = hospitals[
            (hospitals['Disease'].str.strip().str.lower() == disease.strip().lower()) &
            (hospitals['Location'].str.strip().str.lower().str.contains(location.strip().lower()))
        ]
        if matches.empty:
            matches = hospitals[hospitals['Disease'].str.strip().str.lower() == disease.strip().lower()]
        hospital_names = matches['Hospital'].tolist()
        # --- Save recommendations to SQL for this query ---
        cur2 = mysql.connection.cursor()
        print(f"Query ID: {q[0]}, Hospitals: {hospital_names}")
        cur2.execute(
            "UPDATE user_queries SET hospitals=%s WHERE id=%s",
            (",".join(hospital_names), q[0])
        )
        mysql.connection.commit()
        cur2.close()
        # --------------------------------------------------
        queries_with_hospitals.append(q + (hospital_names,))
    return render_template('admin_panel.html', users=users, queries=queries_with_hospitals)
# Edit user route
@app.route('/admin/edit-user/<int:user_id>', methods=['GET', 'POST'])
def edit_user(user_id):
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    cur = mysql.connection.cursor()
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        cur.execute("UPDATE users SET username=%s, email=%s WHERE id=%s", (username, email, user_id))
        mysql.connection.commit()
        cur.close()
        flash('User updated successfully.')
        return redirect(url_for('admin_panel'))
    cur.execute("SELECT id, username, email FROM users WHERE id=%s", (user_id,))
    user = cur.fetchone()
    cur.close()
    return render_template('edit_user.html', user=user)

# Edit query route
@app.route('/admin/edit-query/<int:query_id>', methods=['GET', 'POST'])
def edit_query(query_id):
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    cur = mysql.connection.cursor()
    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        gender = request.form['gender']
        location = request.form['location']
        symptoms = request.form['symptoms']
        predicted_disease = request.form['predicted_disease']
        username = request.form['username']
        hospitals_field = request.form.get('hospitals', '')
        cur.execute("""
            UPDATE user_queries SET name=%s, age=%s, gender=%s, location=%s, symptoms=%s, predicted_disease=%s, username=%s, hospitals=%s
            WHERE id=%s
        """, (name, age, gender, location, symptoms, predicted_disease, username, hospitals_field, query_id))
        mysql.connection.commit()
        cur.close()
        flash('Query updated successfully.')
        return redirect(url_for('admin_panel'))
    cur.execute("SELECT * FROM user_queries WHERE id=%s", (query_id,))
    query = cur.fetchone()
    cur.close()
    return render_template('edit_query.html', query=query)
@app.route('/admin/save-recommendation/<int:query_id>', methods=['POST'])
def save_recommendation(query_id):
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    hospitals_field = request.form.get('hospitals', '')
    cur = mysql.connection.cursor()
    cur.execute(
        "UPDATE user_queries SET hospitals=%s WHERE id=%s",
        (hospitals_field, query_id)
    )
    mysql.connection.commit()
    cur.close()
    flash('Hospital recommendation saved.')
    return redirect(url_for('admin_panel'))
@app.route('/admin-logout')
def admin_logout():
    session.pop('admin', None)
    return redirect(url_for('admin_login'))
@app.route('/')
def home():
    return redirect(url_for('login'))
@app.route('/about')
def about():
    return render_template("about.html")
# contact view funtion and path
@app.route('/contact')
def contact():
    return render_template("contact.html")

# developer view funtion and path
@app.route('/developer')
def developer():
    return render_template("developer.html")

# about view funtion and path
@app.route('/blog')
def blog():
    return render_template("blog.html")

# about view funtion and path
@app.route('/upload',  methods=['GET', 'POST'])
def upload():
    return render_template("upload.html")

import numpy as np

if __name__ == '__main__':
   app.run(debug=True)
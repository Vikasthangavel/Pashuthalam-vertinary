import pandas as pd
import numpy as np
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_bcrypt import Bcrypt
import os
from datetime import datetime, timedelta


# Import database components
from db import (
    db, get_database_uri, init_database, Doctor, Farmer, MedicineRecommendation, RecommendationItem,
    validate_doctor_data, create_doctor, authenticate_doctor,
    get_doctor_by_id, get_all_doctors, delete_doctor, update_doctor,
    get_farmer_by_mobile, create_farmer, get_farmer_by_id,
    create_medicine_recommendation, create_recommendation_item, get_recommendations_by_farmer, get_recommendations_by_doctor,
    claim_recommendation, unclaim_recommendation, get_unclaimed_recommendations, get_claimed_recommendations,
    get_recommendation_by_id, get_recommendation_item_by_id, get_doctor_analytics, get_doctor_patients_with_recommendations
)

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-change-this-in-production')

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = get_database_uri()
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db.init_app(app)
bcrypt = Bcrypt(app)



# Load poultry optimal dataset
try:
    poultry_df = pd.read_csv("poultry_dataset_optimal.csv")
    print("✅ Poultry optimal dataset loaded successfully")
    print(f"Found {len(poultry_df['Disease'].unique())} unique diseases in poultry dataset: {list(poultry_df['Disease'].unique())}")
except Exception as e:
    print(f"❌ Error loading poultry optimal dataset: {e}")
    poultry_df = None

# Function to recommend antibiotic, dosage & treatment days based on optimal poultry dataset
def recommend_poultry_treatment(age, weight, disease, breed=None, top_n=3):
    """Get antibiotic recommendation based on optimal poultry dataset"""
    if poultry_df is None:
        return None
    
    # Filter dataset by disease
    subset = poultry_df[poultry_df["Disease"].str.lower() == disease.lower()]
    if subset.empty:
        return None
    
    # Further filter by breed if provided
    if breed:
        breed_subset = subset[subset["Breed"].str.lower() == breed.lower()]
        if not breed_subset.empty:
            subset = breed_subset
    
    # Compute distance to nearest records (Age + Weight)
    subset = subset.copy()
    subset["distance"] = np.sqrt((subset["Age (days)"] - age) ** 2 + (subset["Weight (kg)"] - weight) ** 2)
    
    # Pick closest matches
    closest = subset.nsmallest(top_n, "distance")
    recommendations = []
    
    for _, row in closest.iterrows():
        recommendations.append({
            'antibiotic': row['Suggested Antibiotic'],
            'dosage_mg': row['Dosage of Antibiotic (mg)'],
            'treatment_days': int(row['Treatment Days']),
            'age_reference': row['Age (days)'],
            'weight_reference': row['Weight (kg)'],
            'breed_reference': row['Breed'],
            'similarity_score': 1.0 / (1.0 + row['distance'])
        })
    
    return recommendations

# Realistic Veterinary Dosage Model
# Dynamic dosage standards based on optimal dataset  
def get_veterinary_dosage_standards():
    """Generate dosage standards from optimal poultry dataset"""
    if poultry_df is None:
        return {'Poultry': {}}
    
    standards = {'Poultry': {}}
    
    for antibiotic in poultry_df['Suggested Antibiotic'].unique():
        antibiotic_data = poultry_df[poultry_df['Suggested Antibiotic'] == antibiotic]
        
        # Calculate average dosage per kg (convert mg to ml - rough approximation: 10mg = 1ml)
        avg_dosage_mg_per_kg = (antibiotic_data['Dosage of Antibiotic (mg)'] / antibiotic_data['Weight (kg)']).mean()
        base_dosage_ml_per_kg = round(avg_dosage_mg_per_kg / 10.0, 2)  # Convert mg to ml
        
        # Calculate min and max total doses
        min_dose = round(antibiotic_data['Dosage of Antibiotic (mg)'].min() / 10.0, 1)
        max_dose = round(antibiotic_data['Dosage of Antibiotic (mg)'].max() / 10.0, 1)
        
        # Calculate average treatment days
        avg_days = int(antibiotic_data['Treatment Days'].mean())
        
        standards['Poultry'][antibiotic] = {
            'base_dosage_per_kg': base_dosage_ml_per_kg,
            'min_total_dose': max(1.0, min_dose),
            'max_total_dose': max_dose,
            'frequency': f'Based on optimal dataset - Average {avg_days} days treatment'
        }
    
    return standards

VETERINARY_DOSAGE_STANDARDS = get_veterinary_dosage_standards()

# Disease to Treatment Mapping
# Dynamic disease treatment map based on optimal dataset
def get_disease_treatment_map():
    """Generate disease treatment map from optimal poultry dataset"""
    if poultry_df is None:
        return {}
    
    disease_map = {}
    for disease in poultry_df['Disease'].unique():
        # Get the most common antibiotic for this disease
        disease_data = poultry_df[poultry_df['Disease'] == disease]
        antibiotic_counts = disease_data['Suggested Antibiotic'].value_counts()
        
        primary_treatment = antibiotic_counts.index[0]
        alternative_treatments = antibiotic_counts.index[1:4].tolist()  # Get top 3 alternatives
        
        # Calculate average treatment days
        avg_days = int(disease_data['Treatment Days'].mean())
        
        disease_map[disease] = {
            'primary_treatment': primary_treatment,
            'alternative_treatments': alternative_treatments,
            'category': 'Poultry',
            'average_treatment_days': avg_days,
            'notes': f'Based on optimal poultry dataset. Average treatment: {avg_days} days.'
        }
    
    return disease_map

DISEASE_TREATMENT_MAP = get_disease_treatment_map()

@app.route('/')
def index():
    """Home page"""
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page for medical shops"""
    if request.method == 'POST':
        mobile_no = request.form.get('mobile_no')
        password = request.form.get('password')
        
        if not mobile_no or not password:
            flash('Please provide both mobile number and password', 'danger')
            return render_template('login.html')
        
        doctor, error = authenticate_doctor(mobile_no, password)
        if doctor:
            session['doctor_id'] = doctor.id
            session['hospital_name'] = doctor.hospital_name
            flash(f'Welcome back, {doctor.hospital_name}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash(f'Login failed: {error}', 'danger')
    
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    """Signup page for new doctors/hospitals"""
    if request.method == 'POST':
        doctor_data = {
            'hospital_name': request.form.get('hospital_name'),
            'doctor_name': request.form.get('doctor_name'),
            'mobile_no': request.form.get('mobile_no'),
            'address': request.form.get('address'),
            'pincode': request.form.get('pincode'),
            'map_link': request.form.get('map_link'),
            'password': request.form.get('password'),
            'confirm_password': request.form.get('confirm_password')
        }
        
        validation_error = validate_doctor_data(doctor_data)
        if validation_error:
            flash(validation_error, 'danger')
            return render_template('signup.html', doctor_data=doctor_data)
        
        doctor, error = create_doctor(doctor_data)
        if doctor:
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
        else:
            flash(error or 'Failed to create account. Please try again.', 'danger')
            return render_template('signup.html', doctor_data=doctor_data)
    
    return render_template('signup.html')

@app.route('/dashboard')
def dashboard():
    """Dashboard page for logged-in medical shops"""
    if 'doctor_id' not in session:
        flash('Please log in to access your dashboard', 'warning')
        return redirect(url_for('login'))
    
    doctor = get_doctor_by_id(session['doctor_id'])
    if not doctor:
        # Doctor not found, clear session and redirect to login
        session.clear()
        flash('Your session has expired. Please log in again.', 'warning')
        return redirect(url_for('login'))
    
    return render_template('dashboard.html', doctor=doctor)

@app.route('/profile')
def profile():
    """Profile page for logged-in medical shops"""
    if 'doctor_id' not in session:
        flash('Please log in to access your profile', 'warning')
        return redirect(url_for('login'))
    
    doctor = get_doctor_by_id(session['doctor_id'])
    if not doctor:
        # Doctor not found, clear session and redirect to login
        session.clear()
        flash('Your session has expired. Please log in again.', 'warning')
        return redirect(url_for('login'))
    
    return render_template('profile.html', doctor=doctor)

@app.route('/logout')
def logout():
    """Logout route for logged-in users"""
    session.pop('doctor_id', None)
    session.pop('hospital_name', None)
    flash('You have been logged out', 'success')
    return redirect(url_for('index'))

@app.route('/analytics')
def analytics():
    """Analytics and reporting page"""
    if 'doctor_id' not in session:
        flash('Please log in to access analytics', 'warning')
        return redirect(url_for('login'))
    
    try:
        # Get analytics data for the logged-in doctor
        analytics_data = get_doctor_analytics(session['doctor_id'])
        doctor = get_doctor_by_id(session['doctor_id'])
        
        return render_template('analytics.html', 
                             analytics=analytics_data, 
                             doctor=doctor)
    except Exception as e:
        print(f"Error in analytics route: {e}")
        flash('Error loading analytics data', 'error')
        return render_template('analytics.html', 
                             analytics=None, 
                             doctor=None)

@app.route('/api/analytics/patients')
def get_analytics_patients():
    """API endpoint to get patient data for analytics"""
    if 'doctor_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    try:
        patients = get_doctor_patients_with_recommendations(session['doctor_id'])
        return jsonify({
            'success': True,
            'patients': patients
        })
    except Exception as e:
        print(f"Error getting analytics patients: {e}")
        return jsonify({'error': 'Failed to fetch patient data'}), 500

@app.route('/customers')
def customers():
    """Customer management page"""
    if 'doctor_id' not in session:
        flash('Please log in to manage customers', 'warning')
        return redirect(url_for('login'))
    
    # Future implementation: fetch customer data
    return render_template('customers.html')

# Farmer management routes
@app.route('/search-farmer', methods=['POST'])
def search_farmer():
    """Search for a farmer by mobile number"""
    if 'doctor_id' not in session:
        flash('Please log in to search for farmers', 'warning')
        return redirect(url_for('login'))
    
    mobile_no = request.form.get('mobile_no', '').strip()
    
    if not mobile_no or len(mobile_no) != 10 or not mobile_no.isdigit():
        flash('Please enter a valid 10-digit mobile number', 'warning')
        return redirect(url_for('dashboard'))
    
    farmer = get_farmer_by_mobile(mobile_no)
    
    # Check if it's an AJAX request
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    
    if farmer:
        # Farmer found
        if is_ajax:
            return jsonify({
                'status': 'found',
                'message': f'Farmer found',
                'redirect': url_for('medicine', farmer_id=farmer.id)
            })
        # Regular request
        return redirect(url_for('medicine', farmer_id=farmer.id))
    else:
        # Farmer not found
        if is_ajax:
            return jsonify({
                'status': 'not_found',
                'message': f'No farmer found with mobile number {mobile_no}',
                'mobile_no': mobile_no
            })
        # Fallback for non-AJAX requests
        flash(f'No farmer found with mobile number {mobile_no}. Please register the farmer.', 'info')
        session['temp_mobile_no'] = mobile_no  # Store mobile number temporarily
        return redirect(url_for('dashboard', add_farmer=True, mobile_no=mobile_no))

@app.route('/api/check-farmer', methods=['POST'])
def check_farmer_api():
    """API endpoint to check if farmer exists by mobile number for popup"""
    print(f"API called - Session keys: {list(session.keys())}")
    print(f"Doctor ID in session: {'doctor_id' in session}")
    
    if 'doctor_id' not in session:
        print("No doctor_id in session - returning 401")
        return jsonify({'status': 'error', 'message': 'Please log in'}), 401
    
    data = request.get_json()
    print(f"Request data: {data}")
    mobile_no = data.get('mobile_no', '').strip() if data else ''
    
    if not mobile_no or len(mobile_no) != 10 or not mobile_no.isdigit():
        return jsonify({'status': 'error', 'message': 'Please enter a valid 10-digit mobile number'}), 400
    
    farmer = get_farmer_by_mobile(mobile_no)
    
    if farmer:
        return jsonify({
            'status': 'found',
            'farmer_id': farmer.id,
            'farmer_name': farmer.name,
            'message': f'Farmer {farmer.name} found'
        })
    else:
        return jsonify({
            'status': 'not_found',
            'mobile_no': mobile_no,
            'message': f'No farmer found with mobile number {mobile_no}'
        })

@app.route('/add-farmer', methods=['POST'])
def add_farmer():
    """Add a new farmer"""
    if 'doctor_id' not in session:
        flash('Please log in to add farmers', 'warning')
        return redirect(url_for('login'))
    
    name = request.form.get('name', '').strip()
    mobile_no = request.form.get('mobile_no', '').strip()
    address = request.form.get('address', '').strip()
    pincode = request.form.get('pincode', '').strip()
    
    if not name or not mobile_no:
        flash('Name and mobile number are required', 'warning')
        return redirect(url_for('dashboard'))
    
    if len(mobile_no) != 10 or not mobile_no.isdigit():
        flash('Please enter a valid 10-digit mobile number', 'warning')
        return redirect(url_for('dashboard'))
    
    # Check if farmer already exists
    existing_farmer = get_farmer_by_mobile(mobile_no)
    if existing_farmer:
        flash(f'A farmer with mobile number {mobile_no} already exists', 'warning')
        return redirect(url_for('medicine', farmer_id=existing_farmer.id))
    
    # Create new farmer with current doctor ID
    farmer, error = create_farmer(name, mobile_no, address, pincode, doctor_id=session['doctor_id'])
    
    if farmer:
        flash(f'Farmer {name} has been successfully added', 'success')
        return redirect(url_for('medicine', farmer_id=farmer.id))
    else:
        flash(f'Failed to add farmer: {error}', 'danger')
        return redirect(url_for('dashboard'))

@app.route('/orders')
def orders():
    """Order management page"""
    if 'doctor_id' not in session:
        flash('Please log in to manage orders', 'warning')
        return redirect(url_for('login'))
    
    # Future implementation: fetch order data
    return render_template('orders.html')

@app.route('/settings')
def settings():
    """User settings page"""
    if 'doctor_id' not in session:
        flash('Please log in to access settings', 'warning')
        return redirect(url_for('login'))
    
    doctor = get_doctor_by_id(session['doctor_id'])
    if not doctor:
        # Doctor not found, clear session and redirect to login
        session.clear()
        flash('Your session has expired. Please log in again.', 'warning')
        return redirect(url_for('login'))
    
    return render_template('settings.html', doctor=doctor)



@app.route('/update-profile', methods=['POST'])
def update_profile():
    """Update doctor profile"""
    if 'doctor_id' not in session:
        flash('Please log in to update your profile', 'warning')
        return redirect(url_for('login'))
    
    doctor_data = {
        'hospital_name': request.form.get('hospital_name'),
        'doctor_name': request.form.get('doctor_name'),
        'address': request.form.get('address'),
        'pincode': request.form.get('pincode'),
        'map_link': request.form.get('map_link')
    }
    
    # Only update password if provided
    password = request.form.get('password')
    if password and password.strip():
        doctor_data['password'] = password
    
    success, message = update_doctor(session['doctor_id'], doctor_data)
    if success:
        flash('Profile updated successfully!', 'success')
    else:
        flash(message or 'Failed to update profile', 'danger')
    
    return redirect(url_for('settings'))

# API Routes
@app.route('/api/doctors')
def api_doctors():
    """Get all doctors (admin only in production)"""
    doctors = get_all_doctors()
    return jsonify([doctor.to_dict() for doctor in doctors])

@app.route('/api/doctor/<int:doctor_id>')
def api_doctor(doctor_id):
    """Get doctor by ID"""
    doctor = get_doctor_by_id(doctor_id)
    if doctor:
        return jsonify(doctor.to_dict())
    return jsonify({'error': 'Doctor not found'}), 404

@app.route('/api/validate-mobile', methods=['POST'])
def validate_mobile():
    """API endpoint to validate mobile number during signup"""
    try:
        data = request.get_json()
        mobile_no = data.get('mobile_no', '').strip()
        
        # Validate mobile number format
        if not mobile_no.isdigit() or len(mobile_no) != 10:
            return jsonify({
                'valid': False,
                'message': 'Mobile number must be 10 digits'
            })
        
        # Check if mobile number is already registered
        from db import Doctor
        existing_doctor = Doctor.query.filter_by(mobile_no=mobile_no).first()
        
        if existing_doctor:
            return jsonify({
                'valid': False,
                'message': 'This mobile number is already registered'
            })
        
        return jsonify({
            'valid': True,
            'message': 'Mobile number is available'
        })
    
    except Exception as e:
        return jsonify({
            'valid': False,
            'message': 'Error validating mobile number'
        }), 500

@app.route('/medicine')
@app.route('/medicine/<int:farmer_id>')
def medicine(farmer_id=None):
    """Medicine recommendation page"""
    if 'doctor_id' not in session:
        flash('Please log in to access medicine recommendations', 'warning')
        return redirect(url_for('login'))
    
    # Get disease list for the form - this will be used in the server-side rendering
    diseases = list(DISEASE_TREATMENT_MAP.keys())
    
    # Add diseases from poultry dataset
    if poultry_df is not None:
        try:
            poultry_diseases = poultry_df['Disease'].unique().tolist()
            print(f"Found {len(poultry_diseases)} unique diseases in poultry dataset: {poultry_diseases}")
            for disease in poultry_diseases:
                if disease not in diseases:
                    diseases.append(disease)
        except Exception as e:
            print(f"Error processing poultry diseases: {e}")
    
    # Sort the combined disease list
    diseases = sorted(diseases)
    
    doctor = get_doctor_by_id(session['doctor_id'])
    if not doctor:
        # Doctor not found, clear session and redirect to login
        session.clear()
        flash('Your session has expired. Please log in again.', 'warning')
        return redirect(url_for('login'))
    
    # Get farmer if ID is provided
    farmer = None
    if farmer_id:
        farmer = get_farmer_by_id(farmer_id)
        if not farmer:
            flash('Farmer not found', 'warning')
    
    # Get previous recommendations for this farmer if available
    recommendations = []
    if farmer:
        # Check if farmer is a tuple (from our modified query) or a full object
        if isinstance(farmer, tuple):
            farmer_id = farmer[0]  # The ID is the first element in the tuple
        else:
            farmer_id = farmer.id
        recommendations = get_recommendations_by_farmer(farmer_id)

    # Build a safe JSON-ready structure for recommendations to use in JS
    recommendations_json = []
    try:
        for rec in (recommendations or []):
            # Safely get attributes whether rec is an object or dict
            def get_attr(obj, name, default=None):
                return getattr(obj, name, obj.get(name, default) if isinstance(obj, dict) else default)

            created_at = get_attr(rec, 'created_at')
            date_str = created_at.strftime('%d %b %Y') if created_at else ''
            
            # Get mobile number from farmer
            mobile_no = get_attr(rec.farmer, 'mobile_no', '') if hasattr(rec, 'farmer') and rec.farmer else ''
            
            # Build items array from recommendation_items
            items = []
            if hasattr(rec, 'recommendation_items') and rec.recommendation_items:
                for item in rec.recommendation_items:
                    start_date = get_attr(item, 'start_date')
                    end_date = get_attr(item, 'end_date')
                    daily_frequency = get_attr(item, 'daily_frequency')
                    treatment_days = get_attr(item, 'treatment_days')
                    
                    period_str = ''
                    if start_date and end_date:
                        try:
                            period_str = f"{start_date.strftime('%d %b')} - {end_date.strftime('%d %b %Y')}"
                        except Exception:
                            period_str = ''
                    elif treatment_days:
                        period_str = f"{treatment_days} days"

                    dosage_suffix = ''
                    try:
                        if daily_frequency and int(daily_frequency) > 1:
                            dosage_suffix = f" ({int(daily_frequency)}x/day)"
                    except Exception:
                        pass
                    
                    items.append({
                        'animalType': get_attr(item, 'animal_type', ''),
                        'disease': get_attr(item, 'disease', ''),
                        'antibiotic': get_attr(item, 'antibiotic_name', ''),
                        'dosage': f"{get_attr(item, 'single_dose_ml', '')} ml{dosage_suffix}",
                        'period': period_str,
                        'totalDosage': f"{get_attr(item, 'total_treatment_dosage_ml', '')} ml"
                    })

            # For backward compatibility, also provide old format using first item if available
            first_item = items[0] if items else {}
            
            recommendations_json.append({
                'id': get_attr(rec, 'id', ''),
                'date': date_str,
                'mobileNo': mobile_no,
                'animalType': first_item.get('animalType', ''),
                'disease': first_item.get('disease', ''),
                'antibiotic': first_item.get('antibiotic', ''),
                'dosage': first_item.get('dosage', ''),
                'period': first_item.get('period', ''),
                'totalDosage': first_item.get('totalDosage', ''),
                'isClaimed': get_attr(rec, 'is_claimed', False),
                'items': items  # New items array for updated frontend
            })
    except Exception as e:
        print(f"Error building recommendations_json: {e}")
    
    return render_template('medicine.html', 
                           doctor=doctor, 
                           diseases=diseases, 
                           farmer=farmer, 
                           recommendations=recommendations,
                           recommendations_json=recommendations_json)

# API endpoint to get treatment suggestions from optimal dataset
@app.route('/api/medicine/suggest', methods=['POST'])
def suggest_treatment():
    """Get treatment suggestions from optimal poultry dataset"""
    try:
        data = request.get_json()
        age = data.get('age')
        weight = data.get('weight')
        disease = data.get('disease')
        breed = data.get('breed')
        
        if not all([age, weight, disease]):
            return jsonify({
                'success': False,
                'error': 'Age, weight, and disease are required'
            }), 400
        
        # Get recommendations from optimal dataset
        suggestions = recommend_poultry_treatment(
            age=int(age),
            weight=float(weight),
            disease=disease,
            breed=breed,
            top_n=3
        )
        
        if not suggestions:
            return jsonify({
                'success': False,
                'error': 'No treatment suggestions found for the given parameters'
            }), 404
        
        return jsonify({
            'success': True,
            'suggestions': suggestions
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/medicine/predict', methods=['POST'])
def predict_medicine_treatment():
    """API endpoint to predict treatment details without saving (Preview)"""
    if 'doctor_id' not in session:
        return jsonify({'success': False, 'error': 'Authentication required'}), 401
    
    try:
        data = request.get_json()
        
        disease = data.get('disease')
        animal_type = data.get('animal_type')
        weight = data.get('weight')
        age = data.get('age')
        antibiotics_list = data.get('antibiotics', [])
        
        if not all([disease, animal_type, weight, age]):
             return jsonify({'success': False, 'error': 'Missing required fields'}), 400

        try:
            weight = float(weight)
            age = int(age)
        except ValueError:
             return jsonify({'success': False, 'error': 'Invalid weight or age'}), 400
             
        predictions = []
        
        for antibiotic_data in antibiotics_list:
            antibiotic_name = antibiotic_data.get('antibiotic')
            daily_frequency = int(antibiotic_data.get('daily_frequency', 2))
            
            # AI Logic
            ai_suggestions = recommend_poultry_treatment(age, weight, disease, top_n=1)
            
            if ai_suggestions and len(ai_suggestions) > 0:
                treatment_days = ai_suggestions[0]['treatment_days']
                suggested_dosage_mg = ai_suggestions[0]['dosage_mg']
                single_dose_ml = round(suggested_dosage_mg / 10.0, 1)
                single_dose_ml = max(1.0, min(single_dose_ml, 15.0))
                source = "AI"
            else:
                treatment_days = int(antibiotic_data.get('treatment_days', 7))
                single_dose_ml = round(weight * 0.5, 1)
                single_dose_ml = max(1.0, min(single_dose_ml, 10.0))
                source = "Fallback"
                
            predictions.append({
                'antibiotic': antibiotic_name,
                'treatment_days': treatment_days,
                'single_dose_ml': single_dose_ml,
                'daily_frequency': daily_frequency,
                'source': source
            })
            
        return jsonify({
            'success': True,
            'predictions': predictions
        })

    except Exception as e:
        print(f"Error predicting medicine: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/medicine/recommend', methods=['POST'])
def recommend_medicine():
    """API endpoint for medicine recommendations with multiple antibiotics support"""
    if 'doctor_id' not in session:
        return jsonify({'success': False, 'error': 'Authentication required'}), 401
    
    try:
        data = request.get_json()
        
        # Required fields for the recommendation header
        disease = data.get('disease')
        animal_type = data.get('animal_type')
        weight = data.get('weight')
        age = data.get('age')
        farmer_id = data.get('farmer_id')
        antibiotics_list = data.get('antibiotics', [])  # List of antibiotic treatments
        
        # Validate inputs
        if not all([disease, animal_type, weight, age, farmer_id]):
            return jsonify({
                'success': False,
                'error': 'Missing required fields'
            }), 400
        
        if not antibiotics_list or len(antibiotics_list) == 0:
            return jsonify({
                'success': False,
                'error': 'At least one antibiotic treatment must be provided'
            }), 400
        
        # Convert weight to float and age to int
        try:
            weight = float(weight)
            age = int(age)
        except ValueError:
            return jsonify({
                'success': False,
                'error': 'Weight must be a number and age must be an integer'
            }), 400
        
        # Create the main recommendation record
        from db import MedicineRecommendation, RecommendationItem, db
        
        recommendation = MedicineRecommendation(
            farmer_id=farmer_id,
            doctor_id=session['doctor_id'],
            is_claimed=False,
            claimed_by_shop_id=None
        )
        
        # Save the recommendation to get its ID
        db.session.add(recommendation)
        db.session.flush()  # Get the ID without committing
        
        items_data = []
        response_items = []
        
        # Process each antibiotic
        for idx, antibiotic_data in enumerate(antibiotics_list):
            antibiotic_name = antibiotic_data.get('antibiotic')
            daily_frequency = int(antibiotic_data.get('daily_frequency', 2))
            notes = antibiotic_data.get('notes', '')
            
            # Check for explicit values provided (e.g. from preview)
            provided_days = antibiotic_data.get('treatment_days')
            provided_dose = antibiotic_data.get('single_dose_ml')
            
            if provided_days and provided_dose:
                treatment_days = int(provided_days)
                single_dose_ml = float(provided_dose)
            else:
                # Get AI-predicted treatment days from optimal dataset
                ai_suggestions = recommend_poultry_treatment(age, weight, disease, top_n=1)
                if ai_suggestions and len(ai_suggestions) > 0:
                    # Use AI-predicted treatment days
                    treatment_days = ai_suggestions[0]['treatment_days']
                    # Also use AI-suggested dosage if available
                    suggested_dosage_mg = ai_suggestions[0]['dosage_mg']
                    # Convert mg to ml (rough approximation: 1ml ≈ 10mg for liquid antibiotics)
                    single_dose_ml = round(suggested_dosage_mg / 10.0, 1)
                    single_dose_ml = max(1.0, min(single_dose_ml, 15.0))  # Between 1-15ml
                else:
                    # Fallback to manual input or default
                    treatment_days = int(antibiotic_data.get('treatment_days', 7))
                    # Calculate dosage based on weight (fallback method)
                    single_dose_ml = round(weight * 0.5, 1)  # 0.5ml per kg as example
                    single_dose_ml = max(1.0, min(single_dose_ml, 10.0))  # Between 1-10ml
            
            # Auto-calculate dates starting from today
            start_date = datetime.now().date()
            end_date = start_date + timedelta(days=treatment_days)
            
            # Calculate total dosages
            total_daily_dosage_ml = single_dose_ml * daily_frequency
            total_treatment_dosage_ml = total_daily_dosage_ml * treatment_days
            
            # Create frequency description
            frequency_text = ""
            if daily_frequency == 1:
                frequency_text = "Once daily"
            elif daily_frequency == 2:
                frequency_text = "Twice daily"
            elif daily_frequency == 3:
                frequency_text = "Three times daily"
            else:
                frequency_text = f"{daily_frequency} times daily"
            
            frequency_description = f"{frequency_text} for {treatment_days} days"
            
            # Create recommendation item
            item = RecommendationItem(
                recommendation_id=recommendation.id,
                animal_type=animal_type,
                weight=weight,
                age=age,
                total_limit=total_treatment_dosage_ml,  # Use total treatment dosage as limit
                disease=disease,
                antibiotic_name=antibiotic_name,
                single_dose_ml=single_dose_ml,
                start_date=start_date,
                end_date=end_date,
                treatment_days=treatment_days,
                daily_frequency=daily_frequency,
                total_daily_dosage_ml=total_daily_dosage_ml,
                total_treatment_dosage_ml=total_treatment_dosage_ml,
                frequency_description=frequency_description,
                calculation_note=notes
            )
            
            db.session.add(item)
            
            # Prepare response data
            response_items.append({
                'antibiotic_name': antibiotic_name,
                'animal_type': animal_type,
                'disease': disease,
                'single_dose_ml': single_dose_ml,
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'treatment_days': treatment_days,
                'daily_frequency': daily_frequency,
                'total_daily_dosage_ml': total_daily_dosage_ml,
                'total_treatment_dosage_ml': total_treatment_dosage_ml,
                'frequency_description': frequency_description,
                'notes': notes
            })
        
        # Commit all changes
        db.session.commit()
        
        # Get farmer details
        farmer = get_farmer_by_id(farmer_id)
        farmer_mobile = farmer.mobile_no if farmer else ''
        
        # Format response
        response = {
            'success': True,
            'recommendation': {
                'id': recommendation.id,
                'farmer_id': farmer_id,
                'doctor_id': session['doctor_id'],
                'is_claimed': False,
                'claimed_by': None,
                'disease': disease,
                'animal_type': animal_type,
                'weight_kg': weight,
                'age_days': age,
                'farmer_mobile': farmer_mobile,
                'created_at': recommendation.created_at.isoformat() if hasattr(recommendation, 'created_at') else datetime.now().isoformat(),
                'items': response_items,
                'total_antibiotics': len(response_items),
                'notes': f"Multi-antibiotic treatment plan with {len(response_items)} medications"
            }
        }
        
        return jsonify(response)
    
    except Exception as e:
        db.session.rollback()
        print(f"Error in medicine recommendation: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

@app.route('/api/medicine/diseases', methods=['GET'])
def get_diseases():
    """API endpoint to get all diseases from optimal dataset"""
    try:
        # Load the optimal dataset
        df = pd.read_csv('poultry_dataset_optimal.csv')
        
        # Get unique diseases
        diseases = sorted(df['Disease'].unique().tolist())
        
        return jsonify({
            'success': True,
            'diseases': diseases
        })
    
    except Exception as e:
        print(f"Error retrieving diseases: {str(e)}")
        return jsonify({
            'success': False, 
            'error': 'Internal server error'
        }), 500

@app.route('/api/medicine/antibiotics', methods=['POST'])
def get_antibiotics_for_disease():
    """API endpoint to get available antibiotics for a specific disease"""
    try:
        data = request.get_json()
        disease = data.get('disease')
        
        if not disease:
            return jsonify({
                'success': False,
                'error': 'Missing disease parameter',
                'antibiotics': [],
                'dataset_loaded': poultry_df is not None
            }), 400
        
        # Debug: print(f"Getting antibiotics for disease: {disease}")
        antibiotics = []
        
        # Check standard database
        if disease in DISEASE_TREATMENT_MAP:
            info = DISEASE_TREATMENT_MAP[disease]
            antibiotics.append(info['primary_treatment'])
            antibiotics.extend(info['alternative_treatments'])
            print(f"Found antibiotics in standard DB: {antibiotics}")
        
        # Check poultry dataset - more comprehensively
        dataset_used = False
        if poultry_df is not None:
            try:
                # Debug: print(f"Searching poultry dataset for disease: {disease}")
                dataset_used = True
                
                # First try exact match (case-insensitive)
                poultry_subset = poultry_df[poultry_df['Disease'].str.lower() == disease.lower()]
                
                # If no exact match, try partial match
                if poultry_subset.empty:
                    print(f"No exact match for {disease}, trying partial match")
                    poultry_subset = poultry_df[poultry_df['Disease'].str.lower().str.contains(disease.lower())]
                
                # If still no match, try keyword matching
                if poultry_subset.empty and ('bacterial' in disease.lower() or 'infection' in disease.lower()):
                    print(f"No partial match for {disease}, trying 'Bacterial' category")
                    poultry_subset = poultry_df[poultry_df['Disease'] == 'Bacterial']
                
                # If still no match, try major categories from the actual dataset
                if poultry_subset.empty:
                    available_diseases = poultry_df['Disease'].unique().tolist()
                    for available_disease in available_diseases:
                        if any(word in disease.lower() for word in available_disease.lower().split()):
                            print(f"Trying similarity match with: {available_disease}")
                            poultry_subset = poultry_df[poultry_df['Disease'] == available_disease]
                            if not poultry_subset.empty:
                                break
                
                # Process results if we found any matches
                if not poultry_subset.empty:
                    poultry_antibiotics = poultry_subset['Suggested Antibiotic'].unique().tolist()
                    # Debug: print(f"Found antibiotics in poultry dataset: {poultry_antibiotics}")
                    for antibiotic in poultry_antibiotics:
                        if antibiotic not in antibiotics:
                            antibiotics.append(antibiotic)
                else:
                    print(f"No matching disease found in poultry dataset for: {disease}")
            except Exception as e:
                print(f"Error extracting poultry antibiotics: {e}")
                dataset_used = False
        else:
            print("Poultry dataset not loaded - skipping poultry-specific recommendations")
        
        # Ensure we always return at least a default option
        if not antibiotics:
            print(f"No antibiotics found for disease: {disease}, adding generic options")
            # Add antibiotics from the optimal dataset as fallback
            if poultry_df is not None:
                antibiotics = poultry_df['Suggested Antibiotic'].unique().tolist()[:3]  # Get first 3
            else:
                antibiotics = ["Amprolium", "Doxycycline", "Oxytetracycline"]  # Dataset antibiotics as fallback
        
        # Debug: print(f"Returning antibiotics: {antibiotics}")
        return jsonify({
            'success': True,
            'antibiotics': sorted(antibiotics),
            'dataset_loaded': poultry_df is not None,
            'dataset_used': dataset_used
        })
    
    except Exception as e:
        print(f"Error retrieving antibiotics: {str(e)}")
        return jsonify({
            'success': False, 
            'error': 'Internal server error',
            'antibiotics': []  # Always provide an empty array even on error
        }), 500

@app.route('/api/medicine/antibiotics/by_category', methods=['POST'])
def get_antibiotics_by_category():
    """API endpoint to get recommended antibiotics by category"""
    if 'doctor_id' not in session:
        return jsonify({'success': False, 'error': 'Authentication required'}), 401
    
    try:
        data = request.get_json()
        
        # Required fields
        category = data.get('category')
        
        # Validate inputs
        if not category:
            return jsonify({
                'success': False,
                'error': 'Missing category'
            }), 400
        
        # Check if category exists
        if category not in VETERINARY_DOSAGE_STANDARDS:
            return jsonify({
                'success': False,
                'error': f'Category "{category}" not found'
            }), 404
        
        # Get antibiotics for this category
        antibiotics = list(VETERINARY_DOSAGE_STANDARDS[category].keys())
        antibiotic_details = []
        
        for antibiotic in antibiotics:
            info = VETERINARY_DOSAGE_STANDARDS[category][antibiotic]
            antibiotic_details.append({
                'name': antibiotic,
                'base_dosage_per_kg': info['base_dosage_per_kg'],
                'min_total_dose': info['min_total_dose'],
                'max_total_dose': info['max_total_dose'],
                'frequency': info['frequency']
            })
        
        return jsonify({
            'success': True,
            'category': category,
            'antibiotics': antibiotic_details
        })
    
    except Exception as e:
        print(f"Error retrieving antibiotics: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

@app.route('/api/medicine/auto-dosage', methods=['POST'])
def calculate_auto_dosage():
    """API endpoint to automatically calculate dosage based on animal and medicine"""
    if 'doctor_id' not in session:
        return jsonify({'success': False, 'error': 'Authentication required'}), 401
    
    try:
        data = request.get_json()
        
        # Required fields
        category = data.get('category')
        medicine = data.get('medicine')
        weight = data.get('weight')
        
        # Validate inputs
        if not all([category, medicine, weight]):
            return jsonify({
                'success': False,
                'error': 'Missing required fields'
            }), 400
        
        # Convert weight to float
        try:
            weight = float(weight)
        except ValueError:
            return jsonify({
                'success': False,
                'error': 'Weight must be a number'
            }), 400
        
        # Check if category exists
        if category not in VETERINARY_DOSAGE_STANDARDS:
            return jsonify({
                'success': False,
                'error': f'Category "{category}" not found'
            }), 404
        
        # Check if medicine exists
        if medicine not in VETERINARY_DOSAGE_STANDARDS[category]:
            return jsonify({
                'success': False,
                'error': f'Medicine "{medicine}" not found in category "{category}"'
            }), 404
        
        # Get medicine info
        medicine_info = VETERINARY_DOSAGE_STANDARDS[category][medicine]
        
        # Calculate dosage
        base_dosage = medicine_info['base_dosage_per_kg']
        total_dosage = round(base_dosage * weight, 1)
        
        # Apply constraints
        total_dosage = max(total_dosage, medicine_info['min_total_dose'])
        total_dosage = min(total_dosage, medicine_info['max_total_dose'])
        
        return jsonify({
            'success': True,
            'dosage': {
                'medicine': medicine,
                'category': category,
                'weight_kg': weight,
                'total_dosage_ml': total_dosage,
                'frequency': medicine_info['frequency']
            }
        })
    
    except Exception as e:
        print(f"Error calculating dosage: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500



# Main entry point
if __name__ == '__main__':
    with app.app_context():
        init_database(app)
    app.run(debug=False,port=5002)

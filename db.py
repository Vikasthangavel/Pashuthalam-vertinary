"""
Database configuration and models for Medical Shop Application
"""

from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os
from dotenv import load_dotenv
from sqlalchemy import text

# Load environment variables
load_dotenv()

# Initialize SQLAlchemy (will be bound to app in app.py)
db = SQLAlchemy()

# Database configuration function
def get_database_uri():
    """Get database URI from environment variables"""
    import urllib.parse
    
    DB_USER = os.getenv('DB_USER', 'root')
    DB_PASSWORD = os.getenv('DB_PASSWORD', 'password')
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = os.getenv('DB_PORT', '3306')
    DB_NAME = os.getenv('DB_NAME', 'AgriSafe')
    
    # URL encode the password to handle special characters like @, #, etc.
    encoded_password = urllib.parse.quote_plus(DB_PASSWORD)
    
    return f'mysql+pymysql://{DB_USER}:{encoded_password}@{DB_HOST}:{DB_PORT}/{DB_NAME}'

# Doctor Model
class Doctor(db.Model):
    """Model for doctor registration and authentication"""
    __tablename__ = 'doctors'
    
    id = db.Column(db.Integer, primary_key=True)
    hospital_name = db.Column(db.String(100), nullable=False)
    doctor_name = db.Column(db.String(100), nullable=False)
    mobile_no = db.Column(db.String(15), nullable=False, unique=True)
    pincode = db.Column(db.String(10), nullable=False)
    address = db.Column(db.Text, nullable=False)
    map_link = db.Column(db.Text, nullable=True)
    password_hash = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    recommendations = db.relationship('MedicineRecommendation', backref='doctor', lazy=True)
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        """Check if provided password matches hash"""
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'hospital_name': self.hospital_name,
            'doctor_name': self.doctor_name,
            'mobile_no': self.mobile_no,
            'pincode': self.pincode,
            'address': self.address,
            'map_link': self.map_link,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<Doctor {self.doctor_name}>'

# Farmer Model
class Farmer(db.Model):
    """Model for farmer/customer registration"""
    __tablename__ = 'farmers'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    mobile_no = db.Column(db.String(15), nullable=False, unique=True)
    area = db.Column(db.Text, nullable=True)  # Changed from address to area to match error
    pincode = db.Column(db.String(10), nullable=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    recommendations = db.relationship('MedicineRecommendation', backref='farmer', lazy=True)
    doctor = db.relationship('Doctor', backref='farmers', lazy=True)
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'mobile_no': self.mobile_no,
            'area': self.area,
            'pincode': self.pincode,
            'doctor_id': self.doctor_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<Farmer {self.name}>'

# Medicine Recommendation Model (Simplified)
class MedicineRecommendation(db.Model):
    """Model for medicine recommendations - header table"""
    __tablename__ = 'medicine_recommendations'
    
    id = db.Column(db.Integer, primary_key=True)
    farmer_id = db.Column(db.Integer, db.ForeignKey('farmers.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id'), nullable=False)
    is_claimed = db.Column(db.Boolean, default=False, nullable=False)
    claimed_by_shop_id = db.Column(db.String(100), nullable=True)  # Who claimed the recommendation (shop name/person)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    recommendation_items = db.relationship('RecommendationItem', backref='recommendation', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'farmer_id': self.farmer_id,
            'doctor_id': self.doctor_id,
            'is_claimed': self.is_claimed,
            'claimed_by': self.claimed_by_shop_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'items': [item.to_dict() for item in self.recommendation_items] if self.recommendation_items else []
        }
    
    def __repr__(self):
        return f'<MedicineRecommendation {self.id}>'

# Recommendation Items Model (Detail table)
class RecommendationItem(db.Model):
    """Model for individual recommendation items - stores antibiotic details"""
    __tablename__ = 'recommendation_items'
    
    id = db.Column(db.Integer, primary_key=True)
    recommendation_id = db.Column(db.Integer, db.ForeignKey('medicine_recommendations.id'), nullable=False)
    antibiotic_name = db.Column(db.String(100), nullable=False)
    total_limit = db.Column(db.Float, nullable=False)  # Total dosage limit/amount needed
    animal_type = db.Column(db.String(50), nullable=False)
    weight = db.Column(db.Float, nullable=False)  # Animal weight in kg
    age = db.Column(db.Integer, nullable=False)  # Animal age in days
    disease = db.Column(db.String(100), nullable=False)
    single_dose_ml = db.Column(db.Float, nullable=False)
    start_date = db.Column(db.Date, default=datetime.utcnow().date)
    end_date = db.Column(db.Date, nullable=True)
    treatment_days = db.Column(db.Integer, nullable=False)
    daily_frequency = db.Column(db.Integer, nullable=False, default=1)
    total_daily_dosage_ml = db.Column(db.Float, nullable=False)
    total_treatment_dosage_ml = db.Column(db.Float, nullable=False)
    frequency_description = db.Column(db.String(100), nullable=True)
    dosage_per_kg = db.Column(db.Float, nullable=True)
    age_category = db.Column(db.String(50), nullable=True)
    confidence = db.Column(db.Float, nullable=True)
    calculation_note = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'recommendation_id': self.recommendation_id,
            'antibiotic_name': self.antibiotic_name,
            'total_limit': self.total_limit,
            'animal_type': self.animal_type,
            'weight': self.weight,
            'age': self.age,
            'disease': self.disease,
            'single_dose_ml': self.single_dose_ml,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'treatment_days': self.treatment_days,
            'daily_frequency': self.daily_frequency,
            'total_daily_dosage_ml': self.total_daily_dosage_ml,
            'total_treatment_dosage_ml': self.total_treatment_dosage_ml,
            'frequency_description': self.frequency_description,
            'dosage_per_kg': self.dosage_per_kg,
            'age_category': self.age_category,
            'confidence': self.confidence,
            'calculation_note': self.calculation_note,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<RecommendationItem {self.id} - {self.antibiotic_name}>'

# Call Log Model


def init_database(app):
    """Initialize database with app context and create all necessary tables and indexes"""
    try:
        with app.app_context():
            # Create all tables from SQLAlchemy models
            db.create_all()
            
            # Create additional indexes for better performance
            create_database_indexes()
            
            print("✅ Database tables and indexes created successfully")
            return True
    except Exception as e:
        print(f"❌ Error creating database tables: {e}")
        return False

def create_database_indexes():
    """Create additional database indexes for performance optimization"""
    try:
        # List of indexes to create
        indexes = [
            # Medical shops indexes
            "CREATE INDEX idx_medical_shops_mobile ON medical_shops(mobile_no)",
            "CREATE INDEX idx_medical_shops_pincode ON medical_shops(pincode)",
            
            # Farmers indexes  
            "CREATE INDEX idx_farmers_mobile ON farmers(mobile_no)",
            "CREATE INDEX idx_farmers_pincode ON farmers(pincode)",
            "CREATE INDEX idx_farmers_medical_shop ON farmers(medical_shop_id)",
            
            # Medicine recommendations indexes
            "CREATE INDEX idx_medicine_rec_farmer ON medicine_recommendations(farmer_id)",
            "CREATE INDEX idx_medicine_rec_shop ON medicine_recommendations(medical_shop_id)",
            "CREATE INDEX idx_medicine_rec_created ON medicine_recommendations(created_at)",
            "CREATE INDEX idx_medicine_rec_dates ON medicine_recommendations(start_date, end_date)",
            
            # Recommendation items indexes
            "CREATE INDEX idx_rec_items_recommendation ON recommendation_items(recommendation_id)",
            "CREATE INDEX idx_rec_items_antibiotic ON recommendation_items(antibiotic_name)"
        ]
        
        # Execute each index creation
        for index_sql in indexes:
            try:
                db.session.execute(text(index_sql))
                db.session.commit()
            except Exception as e:
                # Index might already exist, continue (suppress error messages for existing indexes)
                db.session.rollback()
                
        print("✅ Database indexes created/verified successfully")
        
    except Exception as e:
        print(f"⚠️ Warning: Some indexes may not have been created: {e}")

def setup_database_schema():
    """Complete database schema setup including any necessary migrations"""
    try:
        # Ensure all columns exist with proper constraints
        migration_queries = [
            # Ensure farmers table has all required columns
            "ALTER TABLE farmers ADD COLUMN IF NOT EXISTS pincode VARCHAR(10)",
            "ALTER TABLE farmers ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP",
            "ALTER TABLE farmers MODIFY COLUMN medical_shop_id INT NULL DEFAULT NULL",
            
            # Ensure medicine_recommendations table has date columns
            "ALTER TABLE medicine_recommendations ADD COLUMN IF NOT EXISTS start_date DATE",
            "ALTER TABLE medicine_recommendations ADD COLUMN IF NOT EXISTS end_date DATE",
            "ALTER TABLE medicine_recommendations ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP",
            "ALTER TABLE medicine_recommendations MODIFY COLUMN frequency_description VARCHAR(100) NULL",
            "ALTER TABLE medicine_recommendations MODIFY COLUMN dosage_per_kg FLOAT NULL",
            "ALTER TABLE medicine_recommendations MODIFY COLUMN age_category VARCHAR(20) NULL"
        ]
        
        for query in migration_queries:
            try:
                db.session.execute(text(query))
                db.session.commit()
            except Exception as e:
                # Column might already exist, continue
                print(f"Schema migration note: {e}")
                db.session.rollback()
                
        print("✅ Database schema setup completed successfully")
        return True
        
    except Exception as e:
        print(f"❌ Error setting up database schema: {e}")
        return False

def validate_doctor_data(data):
    """Validate doctor registration data"""
    errors = []
    
    # Required fields
    required_fields = ['hospital_name', 'doctor_name', 'mobile_no', 'pincode', 'address', 'password']
    for field in required_fields:
        if not data.get(field, '').strip():
            errors.append(f'{field.replace("_", " ").title()} is required')
    
    # Mobile number validation
    mobile_no = data.get('mobile_no', '').strip()
    if mobile_no:
        if len(mobile_no) != 10 or not mobile_no.isdigit():
            errors.append('Mobile number must be exactly 10 digits')
        
        # Check if mobile number already exists
        existing_doctor = Doctor.query.filter_by(mobile_no=mobile_no).first()
        if existing_doctor:
            errors.append('Mobile number already registered')
    
    # Pincode validation
    pincode = data.get('pincode', '').strip()
    if pincode and (len(pincode) != 6 or not pincode.isdigit()):
        errors.append('Pincode must be exactly 6 digits')
    
    # Password validation
    password = data.get('password', '')
    confirm_password = data.get('confirm_password', '')
    
    if password and len(password) < 6:
        errors.append('Password must be at least 6 characters long')
    
    if password != confirm_password:
        errors.append('Passwords do not match')
    
    return errors

def create_doctor(data):
    """Create a new doctor record"""
    try:
        new_doctor = Doctor(
            hospital_name=data['hospital_name'].strip(),
            doctor_name=data['doctor_name'].strip(),
            mobile_no=data['mobile_no'].strip(),
            pincode=data['pincode'].strip(),
            address=data['address'].strip(),
            map_link=data.get('map_link', '').strip() or None
        )
        new_doctor.set_password(data['password'])
        
        db.session.add(new_doctor)
        db.session.commit()
        
        return new_doctor, None
    except Exception as e:
        db.session.rollback()
        return None, str(e)

def authenticate_doctor(mobile_no, password):
    """Authenticate doctor login"""
    try:
        # Handle different mobile number formats
        # If number has country code (91), try both with and without
        formatted_mobile = mobile_no
        
        # If mobile has country code (starts with 91 and is 12 digits)
        if mobile_no.startswith('91') and len(mobile_no) == 12:
            # Try both with country code and without
            doctor = Doctor.query.filter(
                (Doctor.mobile_no == mobile_no) | 
                (Doctor.mobile_no == mobile_no[2:])
            ).first()
        # If it's a 10-digit number, also try with 91 prefix
        elif len(mobile_no) == 10:
            doctor = Doctor.query.filter(
                (Doctor.mobile_no == mobile_no) | 
                (Doctor.mobile_no == f"91{mobile_no}")
            ).first()
        else:
            # Regular search with exact match
            doctor = Doctor.query.filter_by(mobile_no=mobile_no).first()
            
        if doctor and doctor.check_password(password):
            return doctor, None
        else:
            return None, 'Invalid mobile number or password'
    except Exception as e:
        return None, str(e)

def get_doctor_by_id(doctor_id):
    """Get doctor by ID"""
    try:
        return Doctor.query.get(doctor_id)
    except Exception as e:
        print(f"Error getting doctor by ID: {e}")
        return None

def get_all_doctors():
    """Get all doctors (for admin purposes)"""
    try:
        return Doctor.query.all()
    except Exception as e:
        print(f"Error getting all doctors: {e}")
        return []

def delete_doctor(doctor_id):
    """Delete a doctor record"""
    try:
        doctor = Doctor.query.get(doctor_id)
        if doctor:
            db.session.delete(doctor)
            db.session.commit()
            return True, None
        else:
            return False, "Doctor not found"
    except Exception as e:
        db.session.rollback()
        return False, str(e)

def update_doctor(doctor_id, data):
    """Update doctor information"""
    try:
        doctor = Doctor.query.get(doctor_id)
        if not doctor:
            return None, "Doctor not found"
        
        # Update fields if provided
        if 'hospital_name' in data:
            doctor.hospital_name = data['hospital_name'].strip()
        if 'doctor_name' in data:
            doctor.doctor_name = data['doctor_name'].strip()
        if 'address' in data:
            doctor.address = data['address'].strip()
        if 'map_link' in data:
            doctor.map_link = data['map_link'].strip() or None
        if 'pincode' in data and len(data['pincode']) == 6 and data['pincode'].isdigit():
            doctor.pincode = data['pincode'].strip()
        
        # Password update (if provided)
        if 'password' in data and data['password']:
            doctor.set_password(data['password'])
        
        db.session.commit()
        return doctor, None
    except Exception as e:
        db.session.rollback()
        return None, str(e)

# Farmer-related functions
def get_farmer_by_mobile(mobile_no):
    """Get farmer by mobile number"""
    try:
        return Farmer.query.filter_by(mobile_no=mobile_no).first()
    except Exception as e:
        print(f"Error getting farmer by mobile: {e}")
        return None

def create_farmer(name, mobile_no, address=None, pincode=None, doctor_id=None):
    """Create a new farmer record"""
    try:
        new_farmer = Farmer(
            name=name.strip(),
            mobile_no=mobile_no.strip(),
            area=address.strip() if address else None,
            pincode=pincode.strip() if pincode else None,
            doctor_id=doctor_id
        )
        
        db.session.add(new_farmer)
        db.session.commit()
        
        return new_farmer, None
    except Exception as e:
        db.session.rollback()
        return None, str(e)

def get_all_farmers():
    """Get all farmers"""
    try:
        return Farmer.query.all()
    except Exception as e:
        print(f"Error getting all farmers: {e}")
        return []

def get_farmer_by_id(farmer_id):
    """Get farmer by ID"""
    try:
        return Farmer.query.get(farmer_id)
    except Exception as e:
        print(f"Error getting farmer by ID: {e}")
        return None

# Medicine recommendation functions
def create_medicine_recommendation(data):
    """Create a new medicine recommendation record with items"""
    try:
        # Create the main recommendation record
        new_recommendation = MedicineRecommendation(
            farmer_id=data['farmer_id'],
            doctor_id=data['doctor_id']
        )
        
        db.session.add(new_recommendation)
        db.session.flush()  # Get the ID without committing
        
        # Create recommendation item
        recommendation_item = RecommendationItem(
            recommendation_id=new_recommendation.id,
            antibiotic_name=data['antibiotic_name'],
            total_limit=data.get('total_treatment_dosage_ml', data.get('total_limit', 0)),
            animal_type=data['animal_type'],
            weight=data['animal_weight'],
            age=data['animal_age_days'],
            disease=data['disease'],
            single_dose_ml=data['single_dose_ml'],
            treatment_days=data['treatment_days'],
            daily_frequency=data.get('daily_frequency', 1),
            total_daily_dosage_ml=data['total_daily_dosage_ml'],
            total_treatment_dosage_ml=data['total_treatment_dosage_ml'],
            frequency_description=data.get('frequency_description'),
            dosage_per_kg=data.get('dosage_per_kg'),
            age_category=data.get('age_category'),
            confidence=data.get('confidence'),
            calculation_note=data.get('calculation_note')
        )
        
        if 'start_date' in data:
            recommendation_item.start_date = data['start_date']
            
        if 'end_date' in data:
            recommendation_item.end_date = data['end_date']
        
        db.session.add(recommendation_item)
        db.session.commit()
        
        return new_recommendation, None
    except Exception as e:
        db.session.rollback()
        return None, str(e)

def create_recommendation_item(recommendation_id, data):
    """Create a new recommendation item for an existing recommendation"""
    try:
        recommendation_item = RecommendationItem(
            recommendation_id=recommendation_id,
            antibiotic_name=data['antibiotic_name'],
            total_limit=data.get('total_limit', data.get('total_treatment_dosage_ml', 0)),
            animal_type=data['animal_type'],
            weight=data['weight'],
            age=data['age'],
            disease=data['disease'],
            single_dose_ml=data['single_dose_ml'],
            treatment_days=data['treatment_days'],
            daily_frequency=data.get('daily_frequency', 1),
            total_daily_dosage_ml=data['total_daily_dosage_ml'],
            total_treatment_dosage_ml=data['total_treatment_dosage_ml'],
            frequency_description=data.get('frequency_description'),
            dosage_per_kg=data.get('dosage_per_kg'),
            age_category=data.get('age_category'),
            confidence=data.get('confidence'),
            calculation_note=data.get('calculation_note')
        )
        
        if 'start_date' in data:
            recommendation_item.start_date = data['start_date']
            
        if 'end_date' in data:
            recommendation_item.end_date = data['end_date']
        
        db.session.add(recommendation_item)
        db.session.commit()
        
        return recommendation_item, None
    except Exception as e:
        db.session.rollback()
        return None, str(e)

def get_recommendations_by_farmer(farmer_id):
    """Get all medicine recommendations for a specific farmer with items"""
    try:
        return MedicineRecommendation.query.options(
            db.joinedload(MedicineRecommendation.farmer),
            db.joinedload(MedicineRecommendation.recommendation_items)
        ).filter_by(farmer_id=farmer_id).order_by(MedicineRecommendation.created_at.desc()).all()
    except Exception as e:
        print(f"Error getting recommendations for farmer: {e}")
        return []

def get_recommendations_by_doctor(doctor_id):
    """Get all medicine recommendations made by a specific doctor with items"""
    try:
        return MedicineRecommendation.query.options(
            db.joinedload(MedicineRecommendation.recommendation_items)
        ).filter_by(doctor_id=doctor_id).order_by(MedicineRecommendation.created_at.desc()).all()
    except Exception as e:
        print(f"Error getting recommendations for doctor: {e}")
        return []

def get_recommendation_by_id(recommendation_id):
    """Get medicine recommendation by ID with items"""
    try:
        return MedicineRecommendation.query.options(
            db.joinedload(MedicineRecommendation.recommendation_items)
        ).get(recommendation_id)
    except Exception as e:
        print(f"Error getting recommendation by ID: {e}")
        return None

def claim_recommendation(recommendation_id, claimed_by):
    """Mark a recommendation as claimed"""
    try:
        recommendation = MedicineRecommendation.query.get(recommendation_id)
        if recommendation:
            recommendation.is_claimed = True
            recommendation.claimed_by_shop_id = claimed_by
            recommendation.updated_at = datetime.utcnow()
            db.session.commit()
            return True, None
        else:
            return False, "Recommendation not found"
    except Exception as e:
        db.session.rollback()
        return False, str(e)

def unclaim_recommendation(recommendation_id):
    """Mark a recommendation as unclaimed"""
    try:
        recommendation = MedicineRecommendation.query.get(recommendation_id)
        if recommendation:
            recommendation.is_claimed = False
            recommendation.claimed_by_shop_id = None
            recommendation.updated_at = datetime.utcnow()
            db.session.commit()
            return True, None
        else:
            return False, "Recommendation not found"
    except Exception as e:
        db.session.rollback()
        return False, str(e)

def get_unclaimed_recommendations():
    """Get all unclaimed medicine recommendations"""
    try:
        return MedicineRecommendation.query.options(
            db.joinedload(MedicineRecommendation.farmer),
            db.joinedload(MedicineRecommendation.recommendation_items)
        ).filter_by(is_claimed=False).order_by(MedicineRecommendation.created_at.desc()).all()
    except Exception as e:
        print(f"Error getting unclaimed recommendations: {e}")
        return []

def get_claimed_recommendations(claimed_by=None):
    """Get all claimed medicine recommendations, optionally filtered by claimer"""
    try:
        query = MedicineRecommendation.query.options(
            db.joinedload(MedicineRecommendation.farmer),
            db.joinedload(MedicineRecommendation.recommendation_items)
        ).filter_by(is_claimed=True)
        
        if claimed_by:
            query = query.filter_by(claimed_by_shop_id=claimed_by)
            
        return query.order_by(MedicineRecommendation.updated_at.desc()).all()
    except Exception as e:
        print(f"Error getting claimed recommendations: {e}")
        return []

def get_recommendation_item_by_id(item_id):
    """Get recommendation item by ID"""
    try:
        return RecommendationItem.query.get(item_id)
    except Exception as e:
        print(f"Error getting recommendation item by ID: {e}")
        return None

# Analytics Functions
def get_doctor_analytics(doctor_id):
    """Get comprehensive analytics for a specific doctor"""
    try:
        from sqlalchemy import func, extract
        from datetime import datetime, timedelta
        
        # Basic stats
        total_patients = Farmer.query.filter_by(doctor_id=doctor_id).count()
        total_recommendations = MedicineRecommendation.query.filter_by(doctor_id=doctor_id).count()
        claimed_recommendations = MedicineRecommendation.query.filter_by(doctor_id=doctor_id, is_claimed=True).count()
        unclaimed_recommendations = total_recommendations - claimed_recommendations
        
        # Recent activity (last 30 days)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        recent_patients = Farmer.query.filter(
            Farmer.doctor_id == doctor_id,
            Farmer.created_at >= thirty_days_ago
        ).count()
        
        recent_recommendations = MedicineRecommendation.query.filter(
            MedicineRecommendation.doctor_id == doctor_id,
            MedicineRecommendation.created_at >= thirty_days_ago
        ).count()
        
        # Most common diseases
        disease_stats = db.session.query(
            RecommendationItem.disease,
            func.count(RecommendationItem.disease).label('count')
        ).join(MedicineRecommendation).filter(
            MedicineRecommendation.doctor_id == doctor_id
        ).group_by(RecommendationItem.disease).order_by(
            func.count(RecommendationItem.disease).desc()
        ).limit(5).all()
        
        # Most prescribed antibiotics
        antibiotic_stats = db.session.query(
            RecommendationItem.antibiotic_name,
            func.count(RecommendationItem.antibiotic_name).label('count')
        ).join(MedicineRecommendation).filter(
            MedicineRecommendation.doctor_id == doctor_id
        ).group_by(RecommendationItem.antibiotic_name).order_by(
            func.count(RecommendationItem.antibiotic_name).desc()
        ).limit(5).all()
        
        # Animal type distribution
        animal_stats = db.session.query(
            RecommendationItem.animal_type,
            func.count(RecommendationItem.animal_type).label('count')
        ).join(MedicineRecommendation).filter(
            MedicineRecommendation.doctor_id == doctor_id
        ).group_by(RecommendationItem.animal_type).order_by(
            func.count(RecommendationItem.animal_type).desc()
        ).all()
        
        # Monthly recommendation trend (last 6 months)
        monthly_stats = db.session.query(
            extract('month', MedicineRecommendation.created_at).label('month'),
            extract('year', MedicineRecommendation.created_at).label('year'),
            func.count(MedicineRecommendation.id).label('count')
        ).filter(
            MedicineRecommendation.doctor_id == doctor_id,
            MedicineRecommendation.created_at >= datetime.utcnow() - timedelta(days=180)
        ).group_by(
            extract('year', MedicineRecommendation.created_at),
            extract('month', MedicineRecommendation.created_at)
        ).order_by('year', 'month').all()
        
        return {
            'total_patients': total_patients,
            'total_recommendations': total_recommendations,
            'claimed_recommendations': claimed_recommendations,
            'unclaimed_recommendations': unclaimed_recommendations,
            'recent_patients': recent_patients,
            'recent_recommendations': recent_recommendations,
            'disease_stats': [{'disease': d[0], 'count': d[1]} for d in disease_stats],
            'antibiotic_stats': [{'antibiotic': a[0], 'count': a[1]} for a in antibiotic_stats],
            'animal_stats': [{'animal_type': a[0], 'count': a[1]} for a in animal_stats],
            'monthly_stats': [{'month': int(m[0]), 'year': int(m[1]), 'count': m[2]} for m in monthly_stats]
        }
        
    except Exception as e:
        print(f"Error getting doctor analytics: {e}")
        return {
            'total_patients': 0,
            'total_recommendations': 0,
            'claimed_recommendations': 0,
            'unclaimed_recommendations': 0,
            'recent_patients': 0,
            'recent_recommendations': 0,
            'disease_stats': [],
            'antibiotic_stats': [],
            'animal_stats': [],
            'monthly_stats': []
        }

def get_doctor_patients_with_recommendations(doctor_id):
    """Get all patients who have recommendations from a specific doctor"""
    try:
        from sqlalchemy import func
        
        # Get distinct patients with their recommendation counts
        patients_data = db.session.query(
            Farmer.id,
            Farmer.name,
            Farmer.mobile_no,
            Farmer.area,
            Farmer.pincode,
            func.count(MedicineRecommendation.id).label('recommendation_count'),
            func.max(MedicineRecommendation.created_at).label('last_recommendation')
        ).join(
            MedicineRecommendation, Farmer.id == MedicineRecommendation.farmer_id
        ).filter(
            MedicineRecommendation.doctor_id == doctor_id
        ).group_by(
            Farmer.id, Farmer.name, Farmer.mobile_no, Farmer.area, Farmer.pincode
        ).order_by(
            func.max(MedicineRecommendation.created_at).desc()
        ).all()
        
        # Convert to list of dictionaries
        patients_list = []
        for patient in patients_data:
            patients_list.append({
                'id': patient.id,
                'name': patient.name,
                'mobile_no': patient.mobile_no,
                'area': patient.area or 'Not specified',
                'pincode': patient.pincode or 'Not specified',
                'recommendation_count': patient.recommendation_count,
                'last_recommendation': patient.last_recommendation.strftime('%Y-%m-%d') if patient.last_recommendation else 'Never'
            })
            
        return patients_list
        
    except Exception as e:
        print(f"Error getting patients with recommendations: {e}")
        return []


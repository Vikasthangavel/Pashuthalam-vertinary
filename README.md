# Medical Shop Web Application

A responsive Flask web application for medical shop management with MySQL database integration. This application provides user authentication (login & signup) with mobile-first responsive design and advanced medicine recommendation system for livestock and poultry.

## Features

- **User Authentication**: Secure login and signup system
- **Responsive Design**: Optimized for both mobile and desktop views
- **Mobile Navigation**: Bottom navigation bar for mobile devices
- **Desktop Navigation**: Traditional navbar for desktop users
- **MySQL Integration**: Uses AgriSafe database for data storage
- **Form Validation**: Client-side and server-side validation
- **Secure Password Hashing**: Uses Werkzeug security functions
- **Flash Messages**: User feedback for all operations
- **Medicine Recommendation**: Advanced dosage calculation system
- **Poultry-specific Treatment**: ML-based similarity recommendations
- **Treatment Schedule**: Start/end date calculation with total dosage
- **Farmer Management**: Search and registration system
- **WhatsApp Notifications**: Automated treatment alerts and daily reminders for farmers

## WhatsApp Integration

The application uses Tryowbot API to send WhatsApp messages to farmers:

1. **Initial Treatment Notification**: When a new treatment is recommended, farmers automatically receive a WhatsApp message with details including medicine name, dosage, frequency, and treatment duration.

2. **Daily Reminders**: Farmers receive daily reminders for ongoing treatments to improve medication adherence.

3. **Customizable Templates**: Uses the Tryowbot template system with dynamic parameters.

## Database Schema

The application uses the `AgriSafe` database with the following table structure:

### medical_shops Table
- `id` (INT, Primary Key, Auto Increment)
- `shop_name` (VARCHAR(100), NOT NULL)
- `shop_owner` (VARCHAR(100), NOT NULL)
- `mobile_no` (VARCHAR(15), NOT NULL, UNIQUE)
- `pincode` (VARCHAR(10), NOT NULL)
- `address` (TEXT, NOT NULL)
- `map_link` (TEXT, Optional)
- `password_hash` (VARCHAR(128), NOT NULL)
- `created_at` (TIMESTAMP, Default: CURRENT_TIMESTAMP)

### farmers Table
- `id` (INT, Primary Key, Auto Increment)
- `name` (VARCHAR(100), NOT NULL)
- `mobile_no` (VARCHAR(15), NOT NULL, UNIQUE)
- `address` (TEXT, Optional)
- `pincode` (VARCHAR(10), Optional)
- `created_at` (TIMESTAMP, Default: CURRENT_TIMESTAMP)

### medicine_recommendations Table
- `id` (INT, Primary Key, Auto Increment)
- `farmer_id` (INT, Foreign Key to farmers.id)
- `medical_shop_id` (INT, Foreign Key to medical_shops.id)
- `animal_type` (VARCHAR(50), NOT NULL)
- `animal_weight` (FLOAT, NOT NULL)
- `animal_age_days` (INT, NOT NULL)
- `disease` (VARCHAR(100), NOT NULL)
- `antibiotic_name` (VARCHAR(100), NOT NULL)
- `single_dose_ml` (FLOAT, NOT NULL)
- `start_date` (DATE, Default: CURRENT_DATE)
- `end_date` (DATE, Optional)
- `treatment_days` (INT, NOT NULL)
- `daily_frequency` (INT, NOT NULL, Default: 1)
- `total_daily_dosage_ml` (FLOAT, NOT NULL)
- `total_treatment_dosage_ml` (FLOAT, NOT NULL)
- `frequency_description` (VARCHAR(100), Optional)
- `dosage_per_kg` (FLOAT, Optional)
- `age_category` (VARCHAR(50), Optional)
- `confidence` (FLOAT, Optional)
- `calculation_note` (TEXT, Optional)
- `created_at` (TIMESTAMP, Default: CURRENT_TIMESTAMP)
- `updated_at` (TIMESTAMP, Default: CURRENT_TIMESTAMP, ON UPDATE: CURRENT_TIMESTAMP)

## Prerequisites

- Python 3.8 or higher
- MySQL Server 8.0 or higher
- pip (Python package installer)

## Installation & Setup

### 1. Clone or Download the Project
```bash
# Navigate to your project directory
cd d:\Project-Mainfiles\Project-final\SIH\medical-shop-app
```

### 2. Create Virtual Environment (Recommended)
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. MySQL Database Setup

#### Option A: Using MySQL Command Line
1. Open MySQL command line or MySQL Workbench
2. Run the SQL script:
```sql
-- Create database
CREATE DATABASE IF NOT EXISTS AgriSafe;
USE AgriSafe;

-- Run the database_setup.sql file
SOURCE database_setup.sql;
```

#### Option B: Manual Setup
1. Create database named `AgriSafe`
2. Execute the SQL commands from `database_setup.sql`

### 5. Configure Database Connection

Edit the database configuration in `app.py`:
```python
# Update these values according to your MySQL setup
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://username:password@localhost/AgriSafe'
```

Replace:
- `username`: Your MySQL username (default: root)
- `password`: Your MySQL password
- `localhost`: Your MySQL host (if different)

### 6. Run the Application
```bash
python app.py
```

The application will be available at: `http://localhost:5000`

## Application Structure

```
medical-shop-app/
├── app.py                 # Main Flask application (routes & logic)
├── db.py                  # Database models and operations
├── config.py              # Configuration management
├── utils.py               # Utility functions and decorators
├── database_setup.sql     # Database schema
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── ARCHITECTURE.md       # Detailed architecture documentation
├── templates/            # HTML templates
│   ├── base.html         # Base template with navigation
│   ├── login.html        # Login page
│   ├── signup.html       # Registration page
│   ├── signup_enhanced.html # Enhanced registration page
│   └── dashboard.html    # User dashboard
├── static/               # Static files
│   ├── css/
│   │   └── style.css     # Custom styles
│   └── js/
│       └── script.js     # JavaScript functionality
└── tests/               # Test files
    ├── test_separation.py
    ├── test_registration.py
    └── diagnose.py
```

## Responsive Design Features

### Desktop View (≥768px)
- Traditional top navigation bar
- Larger form inputs and buttons
- Multi-column layouts
- No bottom navigation

### Mobile View (<768px)
- Hidden top navigation
- Bottom navigation with icons
- Single-column layouts
- Touch-optimized interface
- Larger touch targets (44px minimum)

## Navigation Structure

### Desktop Navigation (Top Bar)
- Brand logo with medical icon
- Login/Signup links (for unauthenticated users)
- Dashboard/Logout links (for authenticated users)

### Mobile Navigation (Bottom Bar)
- Icon-based navigation
- Login/Signup icons (for unauthenticated users)
- Dashboard/Logout icons (for authenticated users)

## Form Validation

### Client-Side Validation
- Real-time field validation
- Mobile number: 10-digit numeric validation
- Pincode: 6-digit numeric validation
- Password: Minimum 6 characters
- Password confirmation matching
- URL validation for map links

### Server-Side Validation
- Duplicate mobile number check
- Required field validation
- Data sanitization
- Password hashing

## Security Features

- Password hashing using Werkzeug
- Session management
- CSRF protection (Flask secret key)
- Input validation and sanitization
- Secure database queries using SQLAlchemy ORM

## API Endpoints

### Authentication
- `GET /` - Home page
- `GET,POST /login` - User login
- `GET,POST /signup` - User registration
- `GET /dashboard` - User dashboard (authenticated)
- `GET /logout` - User logout

### Farmer Management
- `POST /search-farmer` - Search for a farmer by mobile number
- `POST /add-farmer` - Register a new farmer
- `GET /medicine/<farmer_id>` - Medicine recommendation page for a specific farmer

### Medicine Recommendation
- `POST /api/medicine/recommend` - Get medicine recommendation based on animal details
- `GET /api/medicine/diseases` - Get list of all available diseases
- `POST /api/medicine/antibiotics` - Get available antibiotics for a specific disease

## Medicine Recommendation System

The application includes an advanced medicine recommendation system for livestock and poultry with the following features:

### Livestock Standard Treatment
- Calculates optimal medicine dosage based on animal weight
- Provides recommended treatment periods
- Suggests primary and alternative treatments
- Includes important treatment notes for farmers

### Poultry-Specific Recommendation
- Uses ML-based similarity algorithm to find the best treatment
- Analyzes historical treatment data from the poultry dataset
- Calculates confidence score based on similarity to known cases
- Recommends specific antibiotics and precise dosage amounts

### Treatment Schedule Management
- Calculates treatment start and end dates
- Determines daily dosage requirements
- Computes total medicine required for full treatment period
- Tracks treatment history for each farmer/animal

### Usage
1. Search for a farmer by mobile number
2. Enter animal details (type, weight, age)
3. Select disease from the dropdown
4. Optionally specify preferred antibiotic
5. Set treatment start date
6. Click "Get Recommendation" to receive detailed treatment plan

### Technical Implementation
- Standard veterinary treatments follow established formulas
- Poultry recommendations use nearest-neighbor similarity search
- Calculations consider animal age, weight, and specific disease
- System stores all recommendations for future reference

## Troubleshooting

### Database Connection Issues
1. Verify MySQL server is running
2. Check database credentials in `app.py`
3. Ensure AgriSafe database exists
4. Verify PyMySQL installation

### Port Already in Use
Change the port in `app.py`:
```python
app.run(debug=True, host='0.0.0.0', port=5001)
```

### Mobile View Not Working
1. Check viewport meta tag in templates
2. Verify CSS media queries
3. Test on actual mobile device or browser dev tools

## Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+
- Mobile browsers (iOS Safari, Chrome Mobile)

## Development

### Running in Debug Mode
The application runs in debug mode by default. For production:
```python
app.run(debug=False, host='0.0.0.0', port=5000)
```

### Adding New Features
1. Update database schema if needed
2. Modify Flask routes in `app.py`
3. Create/update HTML templates
4. Add CSS styles
5. Update JavaScript functionality

## License

This project is developed for educational purposes.

## Support

For support or questions, please refer to the project documentation or contact the development team.
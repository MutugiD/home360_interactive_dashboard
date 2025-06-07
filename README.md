# Home360 Analytics Dashboard

A comprehensive data analytics dashboard for Home360, providing insights into user engagement, feature usage, task management, and conversion funnels. Built with Flask, PostgreSQL, and modern web technologies.

## 🚀 Features

### Analytics Pages
- **Main Dashboard** - Overview with key metrics, user engagement data (DAU/WAU/MAU), and interactive charts
- **Signup Funnel** - User acquisition and conversion analysis
- **Drop-Off Analysis** - Step-by-step funnel visualization with improvement recommendations
- **Task Analysis** - Task creation, completion rates, and staff performance metrics
- **Feature Usage** - Meal planning, recipe search, and feature adoption analytics
- **Invite Tracking & Conversion** - Family and staff invite success rates

### Key Capabilities
- **Interactive Filtering** - Date ranges, user roles, homes, and custom filters
- **Real-time Charts** - Chart.js integration with click-to-filter functionality
- **Role-based Security** - Admin, User, and Viewer access levels
- **Responsive Design** - AdminLTE theme with Tailwind CSS enhancements
- **Modular Architecture** - Clean Flask blueprint structure
- **PostgreSQL Integration** - Robust database connectivity with connection pooling

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.8+
- PostgreSQL 12+
- Git

### 1. Clone the Repository
```bash
git clone <repository-url>
cd dashboard/webapp
```

### 2. Set Up Virtual Environment
```bash
python -m venv dash_board
# Windows
dash_board\Scripts\activate
# macOS/Linux
source dash_board/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Environment Configuration
Create a `.env` file in the project root:
```env
# Database Configuration
DB_HOST=your_database_host
DB_PORT=5432
DB_NAME=your_database_name
DB_USER=your_database_user
DB_PASSWORD=your_database_password
DB_SSLMODE=require

# Flask Configuration
FLASK_SECRET_KEY=your_secret_key_here
FLASK_ENV=development
```

### 5. Database Setup
Ensure your PostgreSQL database is accessible and contains the required Home360 tables:
- `public."User"`
- `public."Home"`
- `public."HomeMember"`
- `public."UserSession"`
- `public."Task"`
- `public."Invite"`
- And other Home360 schema tables

### 6. Test Database Connection
```bash
python src/database/database.py
```

### 7. Run the Application
```bash
python app.py
```

The application will be available at `http://localhost:5000`

## 🏗️ Project Structure

```
dashboard/webapp/
├── app.py                     # Main Flask application (streamlined)
├── requirements.txt           # Python dependencies
├── .env                      # Environment configuration
├── .gitignore               # Git ignore rules
│
├── src/                     # Core application modules
│   ├── database/           # Database connection and utilities
│   ├── engagement_retention/ # User engagement analytics
│   ├── invite_flow/        # Invite tracking and conversion
│   ├── meals_feature/      # Meal planning and recipe analytics
│   ├── signup_funnel/      # User acquisition and funnel analysis
│   ├── task_flow_effectiveness/ # Task management analytics
│   ├── security/           # Authentication and authorization
│   ├── scripts/           # Utility scripts
│   └── filters.py         # Filtering logic and SQL generation
│
├── routers/               # Modular Flask blueprints
│   ├── dashboard/         # Main dashboard routes
│   ├── analytics/         # Analytics page routes
│   ├── api/              # API endpoints
│   └── auth.py           # Authentication routes
│
├── templates/            # Jinja2 HTML templates
│   ├── base.html         # Base template with navigation
│   ├── includes/         # Reusable template components
│   ├── login.html        # Authentication page
│   ├── admin_dashboard.html # Admin panel
│   └── [analytics pages] # Individual analytics templates
│
├── static/              # Static assets
│   ├── css/            # Custom stylesheets
│   ├── js/             # JavaScript files
│   └── images/         # Image assets
│
└── TASKS.md            # Project progress and implementation details
```

## 🔐 Authentication & Security

### Demo Credentials
| Role    | Username   | Password    | Access Level |
|---------|------------|-------------|--------------|
| Admin   | `admin`    | `admin123!` | Full system access, user management |
| User    | `demo_user`| `demo123!`  | Analytics access, limited admin |
| Viewer  | `viewer`   | `viewer123!`| Read-only analytics access |

### Security Features
- **Session-based Authentication** - Secure token management
- **Role-based Access Control** - Granular permission system
- **Password Hashing** - SHA-256 with salt
- **Protected Routes** - All analytics pages require authentication
- **Admin Dashboard** - User management and system monitoring

## 📊 API Endpoints

### Analytics Data
- `GET /api/user-metrics` - User engagement metrics (DAU/WAU/MAU)
- `GET /api/growth-data` - User growth trends
- `GET /api/activity-data` - Recent user activity
- `GET /api/user-distribution` - User role distribution

### Filtering Support
All endpoints support query parameters:
- `date_range` - all_time, 7days, 30days, custom
- `start_date` - Custom start date (YYYY-MM-DD)
- `end_date` - Custom end date (YYYY-MM-DD)
- `role_filter` - All, Admin, Family, Staff
- `home_id` - Specific home ID
- `user_id` - Specific user ID

## 🎯 Usage Guide

### Accessing the Dashboard
1. Navigate to `http://localhost:5000`
2. Log in with demo credentials
3. Use the sidebar navigation to explore different analytics pages

### Interactive Features
- **Chart Interactions** - Click on chart elements to filter data
- **Filter Panel** - Use the filter panel at the top of each page
- **Quick Actions** - Click on metric cards for quick filtering
- **Real-time Updates** - Data updates without page refresh

### Admin Functions
- **User Management** - Create, edit, and manage user accounts
- **System Statistics** - Monitor dashboard usage and performance
- **Security Settings** - Configure authentication and access controls

## 🔧 Development

### Running in Development Mode
```bash
export FLASK_ENV=development
export FLASK_DEBUG=1
python app.py
```

### Database Testing
```bash
# Test database connection
python src/database/database.py

# Test individual modules
python src/signup_funnel/SignupFunnel_Drop-OffAnalysis.py
python src/engagement_retention/Engagement_Retention.py
```

### Adding New Analytics Modules
1. Create module in `src/` directory
2. Add `__init__.py` with function exports
3. Create route in appropriate `routers/` blueprint
4. Add template in `templates/`
5. Update navigation in `base.html`

## 🏷️ Technology Stack

- **Backend**: Flask 2.x with Blueprint architecture
- **Database**: PostgreSQL with psycopg2 connection pooling
- **Frontend**: AdminLTE 3.x, Chart.js, Tailwind CSS
- **Authentication**: Session-based with secure token management
- **Charts**: Chart.js with interactive filtering
- **UI Components**: Bootstrap 4, Font Awesome icons

## 📈 Analytics Modules

### Engagement & Retention
- Daily/Weekly/Monthly Active Users (DAU/WAU/MAU)
- Session length analysis
- User retention rates
- Login frequency tracking

### Signup Funnel Analysis
- User acquisition metrics
- Conversion rate analysis
- Drop-off point identification
- Home creation vs abandonment

### Task Management Analytics
- Task creation and assignment tracking
- Completion rate analysis by role
- Staff performance metrics
- Task effectiveness measurement

### Feature Usage Tracking
- Meal planning adoption
- Recipe search analytics
- Feature engagement metrics
- Usage pattern analysis

### Invite Flow Effectiveness
- Family vs Staff invite success rates
- Time-to-signup analysis
- Conversion funnel optimization

## 🤝 Contributing

### Development Guidelines
1. Follow modular architecture patterns
2. Add comprehensive error handling
3. Include tests for new features
4. Update documentation
5. Follow Flask best practices

### Code Structure
- Keep routes in appropriate blueprints
- Use `src/` modules for business logic
- Add filters support for new endpoints
- Maintain security decorators on protected routes

## 📝 License

This project is proprietary to Home360. All rights reserved.

## 🆘 Support

For issues and questions:
1. Check existing documentation in `TASKS.md`
2. Review error logs in Flask console
3. Verify database connectivity
4. Check authentication status

## 🚧 Known Issues & Future Enhancements

### Current Limitations
- User storage is in-memory (planned: database integration)
- Limited admin user management features
- Basic audit logging

### Planned Features
- Database user storage
- Enhanced admin functionality
- Audit logging system
- Email notifications
- Data export capabilities
- Advanced filtering options

---

**Last Updated**: December 2024
**Version**: 1.0.0
**Status**: Production Ready
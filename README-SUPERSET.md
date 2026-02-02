# Apache Superset Dashboard Embedding

This implementation provides Apache Superset dashboard embedding functionality using Django (DRF) backend and React frontend with Superset Guest Token authentication and the official @superset-ui/embedded-sdk.

## Architecture Overview

### Backend (Django DRF)
- **Superset App**: Handles Superset integration and guest token generation
- **API Endpoints**: RESTful endpoints for dashboard management and guest token generation
- **Authentication**: Guest token-based authentication for secure dashboard access

### Frontend (React)
- **SupersetDashboard Component**: Embeds individual dashboards with guest token authentication
- **DashboardList Component**: Displays available dashboards with navigation
- **Service Layer**: Handles API communication with Django backend

## Setup Instructions

### Prerequisites
- Apache Superset running and accessible
- Django backend with DRF
- React frontend with TypeScript

### Backend Setup

1. **Install Dependencies**:
   ```bash
   cd back-end
   pip install djangorestframework drf-yasg django-cors-headers requests cryptography
   ```

2. **Configure Superset Settings**:
   Add to `back-end/config/settings.py`:
   ```python
   # Superset Configuration
   SUPERSET_CONFIG = {
       'SUPERSET_URL': 'http://localhost:8088',  # Your Superset URL
       'SUPERSET_USERNAME': 'admin',  # Your Superset username
       'SUPERSET_PASSWORD': 'admin',  # Your Superset password
       'GUEST_TOKEN_EXPIRY': 300,  # Guest token expiry in seconds
       'EMBEDDABLE_DASHBOARDS': {
           'sample_dashboard': {
               'id': 1,  # Dashboard ID in Superset
               'domain': 'localhost',
               'allowed_roles': ['Public'],
           }
       }
   }
   ```

3. **Run Migrations**:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

4. **Sync Embedded Dashboards**:
   ```bash
   # Use the admin endpoint to sync dashboards from config
   POST /api/superset/sync/
   ```

### Frontend Setup

1. **Install Dependencies**:
   ```bash
   cd front-end/ai-assistant-front
   npm install @superset-ui/embedded-sdk axios
   ```

2. **Configure API Base URL**:
   Update `front-end/ai-assistant-front/src/services/supersetService.ts`:
   ```typescript
   const API_BASE_URL = 'http://localhost:8000/api/superset';  # Your Django backend URL
   ```

3. **Run the Application**:
   ```bash
   npm run dev
   ```

## API Endpoints

### Dashboard Management
- `GET /api/superset/dashboards/` - List all embedded dashboards
- `POST /api/superset/dashboards/` - Create new embedded dashboard (admin)
- `GET /api/superset/dashboards/{id}/` - Get specific dashboard
- `PUT /api/superset/dashboards/{id}/` - Update dashboard (admin)
- `DELETE /api/superset/dashboards/{id}/` - Delete dashboard (admin)

### Guest Token Management
- `POST /api/superset/guest-token/` - Generate guest token for dashboard
- `GET /api/superset/guest-token/{token}/validate/` - Validate guest token

### Dashboard Information
- `GET /api/superset/dashboard/{dashboard_id}/` - Get dashboard info from Superset

### Admin Operations
- `POST /api/superset/sync/` - Sync embedded dashboards with config (admin)

## Component Usage

### SupersetDashboard Component
```typescript
import SupersetDashboard from './components/SupersetDashboard';

<SupersetDashboard
  dashboardId={1}
  userId={1}  // Optional: for user-specific dashboards
  resources={[  // Optional: custom resources
    {
      type: "dashboard",
      id: 1
    }
  ]}
  rls={[]}  // Optional: row level security rules
  width="100%"
  height="600px"
  onDashboardLoad={() => console.log('Dashboard loaded')}
  onDashboardError={(error) => console.error('Dashboard error:', error)}
/>
```

### DashboardList Component
```typescript
import DashboardList from './components/DashboardList';

<DashboardList
  userId={1}  // Optional: for user-specific dashboards
  onDashboardSelect={(dashboard) => console.log('Selected:', dashboard)}
/>
```

## Security Considerations

1. **Guest Token Expiry**: Tokens expire after configured time (default: 5 minutes)
2. **Domain Restrictions**: Dashboards are restricted to configured domains
3. **Role-Based Access**: Dashboards can be restricted to specific user roles
4. **Row Level Security**: Implement RLS rules for data access control

## Configuration Options

### Superset Configuration
- `SUPERSET_URL`: Base URL of your Superset instance
- `SUPERSET_USERNAME`: Admin username for authentication
- `SUPERSET_PASSWORD`: Admin password for authentication
- `GUEST_TOKEN_EXPIRY`: Token expiry time in seconds
- `EMBEDDABLE_DASHBOARDS`: Configuration for embeddable dashboards

### Dashboard Configuration
- `id`: Dashboard ID in Superset
- `domain`: Allowed domain for embedding
- `allowed_roles`: List of roles that can access the dashboard

## Troubleshooting

### Common Issues

1. **CORS Errors**: Ensure Django CORS settings allow your frontend domain
2. **Authentication Failures**: Verify Superset credentials and connectivity
3. **Dashboard Not Loading**: Check dashboard ID and embedding permissions
4. **Token Generation Failures**: Verify Superset API accessibility

### Debug Mode
Enable debug logging in Django settings:
```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'superset': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}
```

## Production Considerations

1. **HTTPS**: Use HTTPS in production for secure token transmission
2. **Environment Variables**: Store sensitive configuration in environment variables
3. **Rate Limiting**: Implement rate limiting for guest token generation
4. **Monitoring**: Monitor dashboard usage and token generation
5. **Caching**: Implement caching for dashboard metadata

## Example Configuration

### Environment Variables
```bash
# .env
SUPERSET_URL=https://superset.yourdomain.com
SUPERSET_USERNAME=admin
SUPERSET_PASSWORD=your_secure_password
GUEST_TOKEN_EXPIRY=300
```

### Nginx Configuration (Optional)
```nginx
server {
    listen 80;
    server_name yourdomain.com;
    
    location /api/superset/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## License

This implementation follows the same license as your project. Please refer to the Apache Superset and React licenses for their respective components.
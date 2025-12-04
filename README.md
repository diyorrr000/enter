# ENTERPRISE ERP SYSTEM 🏢

Full-scale business management solution for large corporations with comprehensive modules for all business operations.

## 🚀 Features

### 📊 **Core Modules**
- **Company Management** - Multi-company, multi-branch support
- **User Management** - Role-based access control with granular permissions
- **HR Management** - Employee records, attendance, leave, payroll
- **Finance & Accounting** - General ledger, invoicing, payments, financial reports
- **Sales & CRM** - Customer management, sales orders, quotations
- **Inventory Management** - Product catalog, stock control, warehouses
- **Purchasing** - Supplier management, purchase orders, receiving
- **Manufacturing** - Production planning, bill of materials, work orders
- **Project Management** - Project planning, task management, time tracking

### 🛠️ **Advanced Features**
- **Real-time Dashboard** - Customizable analytics and KPIs
- **Workflow Automation** - Custom business process automation
- **Document Management** - Secure document storage and sharing
- **Audit Trail** - Complete activity logging and compliance
- **API-First Design** - RESTful APIs for all operations
- **Multi-currency & Multi-language** - Global business support
- **Reporting Engine** - Advanced financial and operational reporting
- **Mobile Responsive** - Full mobile support

## 🏗️ **Tech Stack**

### **Backend**
- **Django 4.2** - Python web framework
- **Django REST Framework** - API development
- **MySQL 8.0** - Primary database
- **Redis** - Caching and message broker
- **Celery** - Asynchronous task processing
- **JWT Authentication** - Secure token-based auth

### **Frontend**
- **React 18** - Frontend library
- **Material-UI** - UI component library
- **Redux Toolkit** - State management
- **React Query** - Server state management
- **Chart.js** - Data visualization
- **React Router** - Navigation

### **DevOps**
- **Docker & Docker Compose** - Containerization
- **Nginx** - Reverse proxy and load balancing
- **GitHub Actions** - CI/CD pipeline
- **Prometheus & Grafana** - Monitoring
- **ELK Stack** - Log management
- **AWS S3** - File storage

## 📦 **Installation**

### **Option 1: Docker Compose (Recommended)**
```bash
# Clone repository
git clone https://github.com/diyorrr000/enter.git
cd enter

# Copy environment variables
cp .env.example .env
# Edit .env with your configuration

# Start all services
docker-compose up -d

# Run migrations
docker-compose exec backend python manage.py migrate

# Create superuser
docker-compose exec backend python manage.py createsuperuser

# Access the application
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000/api
# Admin Panel: http://localhost:8000/admin# enter
Enterprise ERP System

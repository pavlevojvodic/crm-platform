# CRM Platform API

A Django REST API for a **multi-company CRM** with sales pipelines, customer management, affiliate tracking, and automated notifications.

## Tech Stack

- **Django** + **Django REST Framework**
- **PostgreSQL** with `ArrayField` for flexible pipeline configuration
- **XlsxWriter** for Excel report generation
- **SMTP** email integration

## Features

- **Multi-Company** - Each company has isolated data, pipelines, and users
- **Sales Pipelines** - Configurable stages (Lead → Prospect → Customer → Closed)
- **Drag & Drop** - Move customers between stages via API
- **Customer Notes** - Timestamped notes with full CRUD
- **Affiliate Tracking** - Link affiliates to customers
- **Notifications** - Company-wide notification system
- **Excel Reports** - Export customer data as `.xlsx`
- **Email Integration** - Send emails directly from the CRM
- **Role-Based Access** - User roles with JSON permission sets

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/log_in` | Authenticate user |
| GET | `/api/dashboard?company_id=` | Sales pipeline dashboard |
| POST | `/api/change_customer_stage` | Move customer between stages |
| POST | `/api/add_customer` | Create new customer |
| GET | `/api/customer/<id>/` | Full customer profile |
| PUT | `/api/edit_customer` | Update customer |
| POST | `/api/add_customer_note` | Add customer note |
| GET | `/api/contacts/<company_id>/` | List all contacts |
| POST | `/api/add_affiliate` | Add affiliate |
| POST | `/api/send_email` | Send email to customer |
| GET | `/api/excel_report?company_id=` | Download Excel report |
| GET | `/api/notifications?company_id=` | Get notifications |

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py runserver
```

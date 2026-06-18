# Cribsy – Find Your Flatmate

## Overview

Cribsy is a web-based flatmate finding platform developed using Django and SQLite3. The platform helps users discover compatible flatmates, connect through secure communication, and explore available home spaces in a structured and verified environment.

The primary objective of Cribsy is to simplify the process of finding trustworthy flatmates while providing a secure and user-friendly experience.

---

## Problem Statement

Finding a reliable flatmate through social media groups, brokers, or personal contacts is often unorganized, time-consuming, and lacks proper verification.

Cribsy addresses these challenges by providing:

- Verified user profiles
- Flatmate discovery and search
- Request and matching system
- Secure communication
- Home space listings
- Feedback and review system

---

## Key Features

### User Management
- User Registration and Authentication
- Profile Creation and Management
- Profile Verification System
- Secure Login and Logout

### Flatmate Discovery
- Search and Browse Flatmates
- View Verified Profiles
- Area-Based Search
- Budget-Based Preferences

### Match and Request System
- Send Flatmate Requests
- Accept or Reject Requests
- Request Status Tracking

### Communication
- One-to-One Chat System
- Conversation Management
- Messaging Between Connected Users

### Home Space Management
- Add Home Space Listings
- Upload Property Photos
- Manage Personal Listings
- Browse Available Spaces

### Reviews and Feedback
- Submit Reviews
- User Feedback System
- Home Space Reviews

### Administration
- User Verification Management
- Platform Monitoring
- Feedback Management
- Administrative Dashboard

---

## System Architecture

The application follows Django's Model-View-Template (MVT) architecture.

### Model
Responsible for:
- Database Operations
- Data Storage
- Business Entities

### View
Responsible for:
- Application Logic
- Request Handling
- Data Processing

### Template
Responsible for:
- User Interface
- Frontend Rendering
- User Interaction

---

## Technology Stack

### Frontend
- HTML5
- CSS3
- JavaScript

### Backend
- Python
- Django Framework

### Database
- SQLite3

### Version Control
- Git
- GitHub

---

## Project Structure

```text
Cribsy/
│
├── chat/
├── matches/
├── users/
├── static/
│   └── css/
├── media/
├── cribsy_project/
│
├── manage.py
├── requirements.txt
└── .gitignore
```

---

## Installation

### Clone the Repository

```bash
git clone https://github.com/sanika0517/Cribsy.git
```

### Navigate to the Project Directory

```bash
cd Cribsy
```

### Create a Virtual Environment

```bash
python -m venv venv
```

### Activate the Virtual Environment

Windows:

```bash
venv\Scripts\activate
```

Linux/macOS:

```bash
source venv/bin/activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Apply Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### Run the Development Server

```bash
python manage.py runserver
```

### Access the Application

```text
http://127.0.0.1:8000/
```

---

## Application Modules

- User Authentication
- Profile Management
- Flatmate Search
- Match Requests
- Chat System
- Home Space Listings
- Reviews and Feedback
- Administrative Dashboard

---

## Security Features

- Django Authentication Framework
- CSRF Protection
- Session Management
- Access Control Mechanisms
- User Verification Workflow

---

## Future Enhancements

Future versions of Cribsy may include:

- AI-Based Compatibility Recommendations
- Real-Time Notifications
- Video Calling Functionality
- Advanced Search Filters
- Mobile Application Support
- Smart Recommendation System
- Google Maps Integration
- Enhanced Identity Verification

---

## Contributors

- Sanika Rai
- Tanisha Gaikwad

---

## Academic Information

Developed as an MCA Capstone Project at Dnyan Prassarak Mandal's DPU, Pune.

Project Guide:
Ms. Swati Bhat

---

## License

This project is intended for academic and educational purposes.

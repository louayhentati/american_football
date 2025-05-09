# Football Analysis Tool

A web-based football game analysis tool built with *Flask* and *SQLAlchemy*. This tool allows users to log in, manage games, and analyze football plays in real-time.

---

## 1. User Guide

### 1.1 Source Code Link
- [Project Repository](https://gitlab.informatik.fb2.hs-intern.de/projekt-football/f00t2-analysetool)

---

### 1.2 How to Run the System (Terminal Commands & UI Interaction)

To get the system running, follow these steps in your terminal (Python 3.x):

#### Step 1: Initialize the Database
 ⁠bash
python3 init_db.py

⁠ - *What this does:*  
  Deletes the old database, initializes a new one, and adds a test user. After this step, the database is ready for further data interactions.

#### Step 2: Insert Dummy Data
 ⁠bash
python3 init_dummy_data.py

⁠ - *What this does:*  
  Generates a realistic football game, creating random but plausible drives and plays. It includes downs, distances, play types (Run, Pass, Punt, Field Goal), and results (Touchdown, Interception, Fumble, etc.), dynamically updating the game clock and possession.

#### Step 3: Start the Application
 ⁠bash
python3 app.py

⁠ - *What this does:*  
  Starts the web application.

---

## 2. File Structure Overview

Here’s a brief description of the files:

- **init_db.py** – Initializes the database and adds a test user.
- **init_dummy_data.py** – Generates dummy football game data.
- **app.py** – The main entry point to run the application.
- **models.py** – Defines the database models for users, games, and plays.
- **templates/** – Contains HTML templates for rendering web pages.
- **static/** – Stores static files like CSS, JavaScript, and images.

---

## 3. Navigation

- *First-time Login:*  
  - *URL:* /login  
  - *Admin Login:*  
    - *Username:* coach  
    - *Password:* password123  
    *(Initialized in init_db.py, lines 14-16)*

- *Home/Index Page:*  
  - *URL:* /game-options  
  - This is the landing page after logging in.

- *Add New Game:*  
  - *URL:* /add-game  
  - Allows you to add new football games.

- *Settings:*  
  - *URL:* /settings  
  - Configure application settings.

- *Night Mode:*  
  - Toggle *Night Mode* for a dark theme.

---

## 4. Deployment Packages

The application relies on the following deployment packages:

 ⁠python
from flask import Flask, render_template, request, redirect, url_for, flash, abort, jsonify
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from datetime import datetime
import os
from models import db, User, Game, Drive, Play, PlayOption
import csv
import io
from flask import make_response


⁠ ---

## 5. Requirements

### 5.1 Python Dependencies

- *Flask (3.1.0):* A lightweight web framework for building the app.
- *Flask-SQLAlchemy (3.1.1):* ORM for managing database interactions.
- *Flask-Login (0.6.3):* Manages user authentication and session management.
- *SQLAlchemy (2.0.37):* ORM for object-oriented database operations.
- *Jinja2 (3.1.5):* Templating engine for rendering dynamic HTML pages.
- *Werkzeug (3.1.3):* WSGI utility library for Python.
- *itsdangerous (2.2.0):* Cryptographic signing for secure data handling.
- *MarkupSafe (3.0.2):* Ensures auto-escaping of special characters to prevent XSS attacks.
- *Click (8.1.8):* CLI toolkit for managing the app through command-line interfaces.
- *Blinker (1.9.0):* Event-driven programming and signal handling.
- *Typing Extensions (4.12.2):* Support for advanced type hinting in Python.

---

### 5.2 Generating the requirements.txt

To generate the requirements.txt file, run the following command:

 ⁠bash
pip3 freeze > requirements.txt


⁠ This will generate a requirements.txt file listing all the installed packages and their versions. To install the dependencies on another machine, simply run:

 ⁠bash
pip3 install -r requirements.txt


This ensures that all the necessary dependencies are installed with the exact versions, maintaining consistency across different setups.

---

## 6. Additional Setup

Make sure *Python 3* is installed on your machine before setting up the project.
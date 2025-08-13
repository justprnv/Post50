# Post50 - A Modern Blogging Platform
#### Video Demo: <URL HERE>
#### Description:

Post50 is a full-featured, modern blogging platform that allows users to create, share, and interact with blog posts in a beautiful, responsive web interface. Built with Flask, SQLAlchemy, and modern JavaScript, this project demonstrates comprehensive web development skills including user authentication, database design, rich text editing, real-time interactions, and responsive design.

## Prerequisites

Before running Post50, ensure you have the following installed on your system:

### Required Software
- **Python 3.10 or higher** - [Download from python.org](https://www.python.org/downloads/)
- **Git** - [Download from git-scm.com](https://git-scm.com/downloads)
- **Text Editor/IDE** - VS Code, PyCharm, or any code editor of your choice

### System Requirements
- **Operating System**: Windows 10/11, macOS 10.14+, or Linux (Ubuntu 18.04+)
- **RAM**: Minimum 4GB, Recommended 8GB+
- **Storage**: At least 500MB free space
- **Browser**: Modern browser with JavaScript enabled (Chrome, Firefox, Safari, Edge)

## Installation & Setup

### Step 1: Clone the Repository
```bash
# Clone the project to your local machine
git clone https://github.com/yourusername/Post50.git
cd Post50
```

### Step 2: Set Up Python Virtual Environment

#### Windows (PowerShell/Command Prompt)
```powershell
# Create virtual environment
python -m venv .venv

# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Verify activation (should show (.venv) prefix)
(.venv) PS C:\Users\username\Desktop\Post50>
```

#### macOS/Linux (Terminal)
```bash
# Create virtual environment
python3 -m venv .venv

# Activate virtual environment
source .venv/bin/activate

# Verify activation (should show (.venv) prefix)
(.venv) username@machine:~/Post50$
```

### Step 3: Install Dependencies
```bash
# Upgrade pip to latest version
python -m pip install --upgrade pip

# Install all required packages
pip install -r requirements.txt
```

### Step 4: Initialize the Database
```bash
# The database will be created automatically on first run
# No additional setup required
```

### Step 5: Run the Application
```bash
# Start the Flask development server
python app.py
```

### Step 6: Access the Application
Open your web browser and navigate to:
```
http://127.0.0.1:5000
```

## Quick Start Commands

Here's a complete sequence of commands to get Post50 running quickly:

```bash
# 1. Navigate to project directory
cd Post50

# 2. Create and activate virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1  # Windows
# OR
source .venv/bin/activate     # macOS/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the application
python app.py

# 5. Open browser to http://127.0.0.1:5000
```

## Troubleshooting

### Common Issues and Solutions

#### Python Version Issues
```bash
# Check Python version
python --version

# If Python 3.10+ not found, install from python.org
# Or use python3 command instead
python3 --version
```

#### Virtual Environment Issues
```bash
# If activation fails, try:
# Windows
.\.venv\Scripts\activate.bat

# macOS/Linux
source .venv/bin/activate

# Verify activation
which python  # Should show path within .venv folder
```

#### Dependency Installation Issues
```bash
# Clear pip cache
pip cache purge

# Upgrade pip
python -m pip install --upgrade pip

# Install with verbose output
pip install -r requirements.txt -v

# Install packages individually if needed
pip install Flask==3.0.2
pip install Flask-Login==0.6.3
pip install Flask-SQLAlchemy==3.1.1
pip install Werkzeug==3.0.3
pip install Pillow==10.4.0
```

#### Port Already in Use
```bash
# If port 5000 is busy, modify app.py to use different port
# Or kill the process using port 5000
# Windows
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# macOS/Linux
lsof -ti:5000 | xargs kill -9
```

#### Database Issues
```bash
# If database corruption occurs, delete and recreate
# Windows
del post50.db

# macOS/Linux
rm post50.db

# Restart the application - database will be recreated
```

## Development Setup

### For Developers and Contributors

#### Additional Development Tools
```bash
# Install development dependencies
pip install pytest
pip install black
pip install flake8
pip install pre-commit

# Set up pre-commit hooks
pre-commit install
```

#### Code Formatting
```bash
# Format code with Black
black .

# Check code style with flake8
flake8 .

# Run tests
pytest
```

#### Database Management
```bash
# Access SQLite database directly
sqlite3 post50.db

# View tables
.tables

# View schema
.schema

# Exit SQLite
.quit
```

## Production Deployment

### For Production Use

#### Environment Variables
```bash
# Set production environment variables
export FLASK_ENV=production
export FLASK_DEBUG=0
export SECRET_KEY=your-secret-key-here
export DATABASE_URL=postgresql://user:pass@localhost/post50
```

#### WSGI Server
```bash
# Install production WSGI server
pip install gunicorn

# Run with gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

#### Reverse Proxy (Nginx)
```nginx
server {
    listen 80;
    server_name yourdomain.com;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## Project Overview

Post50 solves the problem of creating a modern, feature-rich blogging platform that combines the simplicity of traditional blogs with advanced features like real-time interactions, rich text editing, and social features. The platform is designed to be both user-friendly for casual bloggers and powerful enough for serious content creators.

## Key Features

### User Management
- **User Registration & Authentication**: Secure user registration with live validation feedback
- **Profile Management**: User profiles with customizable avatars and theme preferences
- **Session Management**: Secure login/logout with Flask-Login integration

### Content Creation
- **Rich Text Editor**: Advanced content editor with formatting tools (bold, italic, underline)
- **Title Formatting**: Rich text editing for post titles with toolbar controls
- **Image Upload**: Support for post images with automatic resizing and optimization
- **Tag System**: Hashtag-based categorization with automatic extraction from content
- **Auto-save**: Draft saving functionality to prevent content loss

### Social Features
- **Voting System**: Upvote/downvote functionality for posts
- **Comments**: Real-time commenting system with user attribution
- **Author Profiles**: Clickable author names linking to user profiles
- **Search Functionality**: Advanced search across titles, content, tags, and authors

### User Experience
- **Dark/Light Mode**: Theme toggle with persistent user preferences
- **Responsive Design**: Mobile-friendly interface using modern CSS
- **Infinite Scroll**: Smooth content loading with "Load More" functionality
- **Modern UI**: Beautiful interface inspired by modern design systems

## Technical Implementation

### Backend Architecture
The application is built using Flask, a lightweight Python web framework that provides excellent flexibility and extensibility. The backend handles:

- **Database Management**: SQLAlchemy ORM with SQLite database
- **User Authentication**: Secure password hashing with Werkzeug
- **File Handling**: Image upload processing with Pillow (PIL)
- **API Endpoints**: RESTful API design for dynamic interactions
- **Data Validation**: Input sanitization and validation

### Database Design
The database schema is designed with proper relationships and normalization:

- **User Model**: Stores user credentials, preferences, and metadata
- **Post Model**: Contains post content, metadata, and relationships
- **Tag Model**: Manages hashtags and categorization
- **Comment Model**: Handles user comments and threading
- **Vote Model**: Tracks user voting interactions

### Frontend Technologies
The frontend utilizes modern web technologies for an engaging user experience:

- **HTML5**: Semantic markup with Jinja2 templating
- **CSS3**: Advanced styling with CSS variables, flexbox, and animations
- **JavaScript ES6+**: Modern JavaScript with async/await and DOM manipulation
- **Responsive Design**: Mobile-first approach with CSS Grid and Flexbox

### Key Technical Challenges Solved

1. **Rich Text Editing**: Implemented contenteditable-based rich text editor with formatting controls
2. **Theme Persistence**: Created robust theme system that persists across sessions and page reloads
3. **Real-time Interactions**: Built dynamic voting and commenting system with AJAX
4. **Image Processing**: Integrated automatic image resizing and optimization
5. **Search Functionality**: Implemented comprehensive search across multiple data types
6. **Tag Management**: Created intelligent hashtag extraction and deduplication system

## File Structure and Organization

### Core Application Files
- **`app.py`**: Main Flask application with routes, models, and business logic
- **`requirements.txt`**: Python dependencies and version specifications
- **`static/`**: Frontend assets including CSS, JavaScript, and uploaded files
- **`templates/`**: Jinja2 HTML templates for all application views

### Frontend Assets
- **`static/css/style.css`**: Comprehensive styling with CSS variables and responsive design
- **`static/js/main.js`**: Client-side functionality including theme management and AJAX calls
- **`static/uploads/`**: User-uploaded images and avatars

### Template Files
- **`base.html`**: Base template with navigation and common elements
- **`index.html`**: Main page displaying posts with infinite scroll
- **`post_form.html`**: Rich text editor for creating and editing posts
- **`profile.html`**: User profile pages with post history
- **`settings.html`**: User preferences and account management

## Design Decisions and Trade-offs

### Technology Choices
I chose Flask over Django because it provides the right balance of simplicity and power for this project. Flask's lightweight nature allowed me to focus on implementing features rather than fighting framework conventions.

### Database Selection
SQLite was chosen for its simplicity and zero-configuration setup, making it perfect for development and demonstration. The application could easily be migrated to PostgreSQL or MySQL for production use.

### Frontend Architecture
The decision to use vanilla JavaScript instead of a framework like React was made to demonstrate fundamental web development skills and keep the project focused on core functionality rather than framework complexity.

### Theme System Design
The theme toggle system was designed with multiple layers of persistence (localStorage, database, and immediate application) to ensure a consistent user experience across all scenarios.

## Learning Outcomes

This project significantly enhanced my understanding of:

- **Full-Stack Development**: Integrating frontend and backend systems
- **Database Design**: Creating efficient schemas with proper relationships
- **User Experience**: Designing intuitive interfaces with modern CSS
- **Security**: Implementing proper authentication and input validation
- **Performance**: Optimizing database queries and frontend interactions
- **Responsive Design**: Creating mobile-friendly web applications

## Future Enhancements

While the current implementation is feature-complete, several enhancements could be added:

- **Real-time Notifications**: WebSocket integration for live updates
- **Advanced Search**: Elasticsearch integration for better search capabilities
- **Social Sharing**: Integration with social media platforms
- **Analytics**: User engagement metrics and post performance tracking
- **Moderation Tools**: Content moderation and user management features

## Conclusion

Post50 represents a comprehensive web application that demonstrates mastery of modern web development concepts. The project successfully combines backend logic, database management, and frontend interactivity to create a fully functional blogging platform. The codebase is well-structured, documented, and follows best practices for maintainability and scalability.

This project showcases the ability to build complex, real-world applications using the skills learned in CS50x, from basic programming concepts to advanced web development techniques. The result is a professional-grade application that could serve as a foundation for a production blogging platform.

# Kaalapani E-football Tournament Management System

A comprehensive Django-based web application for managing e-football tournaments, featuring automated standings points calculation, bracket generation, and a dynamic match management system.

## 🚀 Features

### Public Frontend
*   **Points Table**: Automated standings with live updates for Played, Wins, Draws, Losses, GD, and Points.
*   **Bracket View**: Visual knockout bracket (R16, QF, SF, Final) showing tournament progression.
*   **Top Scorers**: Automatic top scorer tracking based on match results.
*   **Upcoming Matches**: Display of scheduled matches with dates and times.
*   **Match Generator**: Random match pairing tool for tournament draws.
*   **Interactive UI**: Modern, responsive design using TailwindCSS with glassmorphism effects.

### Admin & Management
*   **Match Management**: Dedicated admin interface for managing matches.
    *   Support for **Upcoming** and **Finished** match statuses.
    *   Automatic recalculation of standings and top scorers upon result entry.
*   **Fixture Logic**: Handles two-legged fixtures and single-leg finals.
*   **Team Management**: Manage teams, logos, and details.

## 🛠️ Tech Stack

*   **Backend**: Django (Python)
*   **Frontend**: HTML5, TailwindCSS, JavaScript, HTMX (for dynamic updates)
*   **Database**: SQLite (Development) / PostgreSQL (Production)

## 📦 Installation & Setup

1.  **Clone the repository**
    ```bash
    git clone https://github.com/irshadmuhammed/kaalapani_efootball.git
    cd kaalapani_efootball
    ```

2.  **Create and activate a virtual environment**
    ```bash
    python -m venv venv
    # Windows
    venv\Scripts\activate
    # Linux/Mac
    source venv/bin/activate
    ```

3.  **Install dependencies**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Apply database migrations**
    ```bash
    python manage.py migrate
    ```

5.  **Create a superuser (for admin access)**
    ```bash
    python manage.py createsuperuser
    ```

6.  **Run the development server**
    ```bash
    python manage.py runserver
    ```

    Visit `http://127.0.0.1:8000` to view the site.
    Visit `http://127.0.0.1:8000/custom-admin/matches/` for match management.

## 🔄 Deployment Updates

To update the live server after pushing changes:

1.  Pull the latest code:
    ```bash
    git pull origin main
    ```
2.  Run migrations (if models changed):
    ```bash
    python manage.py migrate
    ```
3.  Restart the application server.

## 📝 Utility Scripts

*   `populate_data.py`: Resets and populates the database with initial tournament data (Teams, Bracket fixture structure).
*   `populate_singlematch.py`: Migrates fixture data to the new SingleMatch format (useful for existing databases).

## 📄 License

This project is open-source and available under the [MIT License](LICENSE).
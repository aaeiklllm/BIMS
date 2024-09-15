## Prerequisites
* Install Python3 and Django and PostgreSQL
* Any Editor (Preferably VS Code or Sublime Text)
* Any web browser with latest version

## Languages and Technologies used
* HTML5/CSS3
* JavaScript (to create dynamically updating content)
* Bootstrap (An HTML, CSS, and JS library)
* PostgreSQL (An RDBMS that uses SQL)
* Python and Django

## Installation

To get started with BIMS, follow these installation steps:

1. Clone the repository to your local machine:

    ```bash
    git clone https://github.com/yourusername/BIMS.git
    ```

2. Create a virtual environment and activate it:

    ```bash
    python3 -m venv venv 
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3. Install project dependencies:

    ```bash
    pip3 install -r requirements.txt
    ```

4. Configure your database settings in the `settings.py` file.

5. Apply database migrations:

    ```bash
    python3 manage.py makemigrations
    python3 manage.py migrate
    ```

6. Create a superuser account:

    ```bash    
    python3 manage.py createsuperuser
    ```

7. Inside the accounts_userrolemap insert data for the admin you created:
```
INSERT INTO public.accounts_userrolemap  (user_id_id,role_id_id)
VALUES
    (1,3);
```

8. Start the development server:

    ```bash
    python3 manage.py runserver
    ```


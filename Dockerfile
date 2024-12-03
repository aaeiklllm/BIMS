FROM python:3.12.0-slim

ENV HOST=0.0.0.0

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory inside the container
WORKDIR /BIMS

# Install system dependencies (for psycopg2, libpq-dev, build-essential, etc.)
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    libjpeg-dev \
    zlib1g-dev \
    libssl-dev \
    libfreetype6-dev \
    libpng-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements.txt first to leverage Docker's cache mechanism
COPY requirements.txt /BIMS/

# Install Python dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy the entire Django project to the container
COPY . /BIMS/

# Collect static files for production
RUN python manage.py collectstatic --noinput

# Expose the port that Django will run on
EXPOSE 8080

# Run the application using Gunicorn, binding it to port 8080 (Cloud Run's port)
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "Hackfest.wsgi:application"]

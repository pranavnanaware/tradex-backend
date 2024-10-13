# Use a base image with Python installed
FROM python:3.9

# Set the working directory in the container
WORKDIR /app

RUN pip3 install --upgrade pip setuptools

# Copy requirements.txt file
COPY requirements.txt requirements.txt

# Install dependencies
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose the port your Flask app runs on
EXPOSE 5000

# Set the command to run your Flask app
CMD ["flask", "run", "--host=0.0.0.0"]
# Stocks Backend

## Overview

Stocks Backend is a Flask-based API service designed to manage and provide stock-related data. This backend serves as the foundation for applications that require real-time stock information, user portfolios, and other financial functionalities.

## Getting Started

Follow the instructions below to set up and run the Stocks Backend on your local machine.

### Prerequisites

- **Python 3.x**: Ensure Python 3 is installed on your system. You can download it from [python.org](https://www.python.org/downloads/).
- **Git**: Required for cloning the repository. Download it from [git-scm.com](https://git-scm.com/downloads).

### Installation

1. **Clone the Repository**

   Open your terminal and clone the repository:

   ```bash
   git clone https://github.com/pranavnanaware/tradex-backend.git
   ```

   Navigate to the project directory:

   ```bash
   cd stocks-backend
   ```

2. **Create a Virtual Environment**

   It's best practice to use a virtual environment to manage project dependencies. Create one using Python's `venv` module:

   ```bash
   python3 -m venv env
   ```

3. **Activate the Virtual Environment**

   - **On macOS and Linux:**

     ```bash
     source env/bin/activate
     ```

   - **On Windows:**

     ```bash
     env\Scripts\activate
     ```

   After activation, your terminal prompt will indicate that you're working within the virtual environment.

4. **Install Dependencies**

   With the virtual environment activated, install the required packages:

   ```bash
   pip install -r requirements.txt
   ```

### Running the Application

Start the Flask development server in debug mode:

```bash
flask run --debug
```

The application will be accessible at `http://127.0.0.1:5000/`. You can interact with the API endpoints using tools like [Postman](https://www.postman.com/) or [cURL](https://curl.se/).

## License

This project is licensed under the [MIT License](LICENSE).

---

_Feel free to reach out if you encounter any issues or have suggestions for improvements._

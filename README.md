# Cometa Test Project

This project demonstrates a FastAPI-based application for managing beer orders and integrating with the New York Times (NYT) Books API. It is structured with clean architecture principles and includes background tasks, logging, and retry policies.

## Features

1. **Beer Orders Management**:
   - Add items to stock.
   - Place beer orders.
   - Split payments equally or individually among friends.
   - Retrieve current order details and payment status.

2. **NYT Integration**:
   - Fetch books by genre from the NYT API.
   - Cache books in memory.
   - Reset the cached books.
   - Retrieve available genres from the NYT API.

3. **Clean Architecture**:
   - Separate layers for models, services, routers, and background tasks.
   - Logging for all critical operations.

## Installation

### Prerequisites
- Python 3.12+
- Virtual environment tool (`venv` or `virtualenv`)

### Steps
1. Clone the repository:
   ```
   git clone <repository_url>
   cd cometa-test
   ```
2. Create and activate a virtual environment:
   ```
   python3 -m venv venv
   source venv/bin/activate  # For Linux/MacOS
   venv\Scripts\activate     # For Windows
   ```
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Set up environment variables:
   Create a `.env` file in the root directory with the following content:
   ```
   NYT_API_KEY=<your_nyt_api_key>
   ```
5. Run the application:
   ```
   uvicorn main:app --reload
   ```

The application will be available at [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).


## Running Tests

To run the test suite:
1. Ensure the virtual environment is activated.
2. Run the following command:
   ```
   pytest
   ```

## Directory Structure
```
├── main.py
├── models
│   ├── nyt.py
│   └── orders.py
├── README.md
├── requirements.txt
├── routers
│   ├── nyt.py
│   └── orders.py
├── services
│   ├── logs.py
│   ├── nyt_service.py
│   └── orders_service.py
├── tasks
│   └── background_tasks.py
├── test_main.py
└── tests
    ├── test_nyt.py
    └── test_orders.py
```
## Logging

All application logs are stored in `execution.log`. Critical operations such as API requests and background task processing are logged for auditing and debugging purposes.

## Notes

- Ensure you have a valid NYT API key in the `.env` file.
- For simplicity, all data (e.g., stock, orders, friends) is stored in memory and reset upon restarting the application.

Enjoy using Cometa Test Project!
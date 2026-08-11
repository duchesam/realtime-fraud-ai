# 🚨 Real-Time Fraud Detection Platform

A real-time fraud detection system built with **Python**, **FastAPI**, **Streamlit**, **Scikit-Learn**, and **SQLite**.

The platform demonstrates an end-to-end machine learning workflow for processing transactions, generating fraud risk scores, storing prediction results, and monitoring system performance through an interactive dashboard.

## Features

- Real-time fraud scoring
- Machine learning prediction model
- REST API using FastAPI
- Interactive Streamlit monitoring dashboard
- Transaction feature processing
- Fraud risk prediction
- Prediction result storage using SQLite
- API latency monitoring
- Fraud rate analytics
- Prediction score distribution
- Simulated real-time transaction producer

## Technology Stack

- Python
- FastAPI
- Streamlit
- Scikit-Learn
- SQLite
- Pandas
- NumPy
- Uvicorn
- Joblib

## System Architecture

The platform simulates a real-time fraud detection pipeline where transactions are processed through a REST API, transformed into model features, scored by a machine learning model, stored for analysis, and visualized through an interactive monitoring dashboard.

```text
Transaction
    |
    v
FastAPI REST API
    |
    v
Feature Processing
    |
    v
Machine Learning Model
    |
    v
Fraud Risk Score
    |
    +-------------------+
    |                   |
    v                   v
SQLite Storage     API Response
    |
    v
Streamlit Dashboard
    |
    v
Fraud & Latency Monitoring
```

## Project Structure

```text
realtime-fraud-ai/
├── models/
│   ├── model.joblib
│   └── model_meta.json
│
├── src/
│   ├── api.py
│   ├── dashboard.py
│   ├── db.py
│   ├── features.py
│   ├── producer.py
│   └── train.py
│
├── .gitignore
├── LICENSE
├── README.md
└── requirements.txt
```

## How It Works

1. A transaction is submitted to the FastAPI REST API.
2. Transaction data is transformed into features required by the machine learning model.
3. The trained Scikit-Learn model generates a fraud risk score.
4. The API returns the prediction result.
5. Prediction information and performance metrics are stored in SQLite.
6. Streamlit reads the stored results and presents fraud and latency analytics through the monitoring dashboard.

## API

The FastAPI application provides a REST endpoint for fraud scoring.

### Start the API

```bash
python -m uvicorn src.api:app --reload --host 127.0.0.1 --port 8000
```

After startup, the API runs locally at:

```text
http://127.0.0.1:8000
```

A successful scoring request returns an HTTP `200 OK` response through the `/score` endpoint.

## Dashboard

The interactive Streamlit dashboard provides visibility into:

- Total predictions
- Fraud rate
- Average API latency
- Latency distribution
- Prediction score distribution
- Real-time fraud monitoring

## Dashboard Preview

![Real-Time Fraud Monitoring Dashboard](fraud-monitoring-dashboard.png)

## Installation

Clone the repository:

```bash
git clone https://github.com/duchesam/realtime-fraud-ai.git
```

Move into the project directory:

```bash
cd realtime-fraud-ai
```

Create a Python virtual environment:

```bash
python -m venv .venv
```

Activate the environment on macOS/Linux:

```bash
source .venv/bin/activate
```

Install the required packages:

```bash
pip install -r requirements.txt
```

## Running the Project

The application uses three main processes: the API, transaction producer, and monitoring dashboard.

### 1. Run the API

```bash
python -m uvicorn src.api:app --reload --host 127.0.0.1 --port 8000
```

### 2. Run the Transaction Producer

Open another Terminal window and run:

```bash
python src/producer.py
```

The producer simulates transactions and sends them to the fraud-scoring API.

### 3. Run the Dashboard

Open another Terminal window and run:

```bash
python -m streamlit run src/dashboard.py
```

Streamlit will provide a local URL that can be opened in a browser to view the fraud monitoring dashboard.

## Machine Learning Pipeline

The project demonstrates a simplified production-style machine learning workflow:

```text
Transaction Data
       |
       v
Feature Engineering
       |
       v
Scikit-Learn Model
       |
       v
Fraud Probability / Risk Score
       |
       v
FastAPI Response
       |
       v
SQLite Analytics Storage
       |
       v
Streamlit Monitoring Dashboard
```

## Project Purpose

This project demonstrates practical experience integrating **machine learning, REST APIs, data processing, application monitoring, and backend services** into a single working application.

It is designed as a portfolio project demonstrating concepts commonly used in AI engineering, machine learning engineering, API development, and software integration environments.

## Author

**Ermias Seyoum**

Software Engineer | API Integration | AI / Machine Learning

GitHub: https://github.com/duchesam

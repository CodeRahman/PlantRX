# PlantRX

PlantRX is a web application that uses machine learning to detect and classify plant diseases from images, enabling early disease identification and helping users monitor plant health.

The application is built with **Flask** for the web interface and backend, and **TensorFlow** for the deep learning image classification model. User authentication and data storage are handled through **Supabase**.

## Features

- User account registration and login
- Secure user authentication
- Upload images of plant leaves
- AI-powered plant disease classification
- View prediction confidence scores
- Access a history of previous classifications

## Technologies Used

- Python
- Flask
- TensorFlow
- Supabase
- HTML/CSS/JavaScript

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd PlantRX
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure your environment variables (e.g., Supabase URL and API key) in a `.env` file.

4. Run the application:
   ```bash
   python run.py
   ```

5. Open your browser and navigate to:
   ```
   http://127.0.0.1:5000
   ```

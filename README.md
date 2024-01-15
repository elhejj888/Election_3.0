# iElect

## Table of Contents

- [Introduction](#introduction)
- [Features](#features)
- [Installation](#installation)
- [Configuration](#configuration)
- [Contributing](#contributing)
- [License](#license)

## Introduction

iElect is a web-based voting platform designed to facilitate fair and secure elections. It provides an accessible and efficient way for users to cast their votes and engage in the democratic process.

## Features

- User-friendly voting interface
- Eligibility verification
- Secure and anonymous voting
- Real-time results tracking

## Installation

1. Clone the repository:
 ```bash
   git clone https://github.com/ADNAN-an/iElect.git
 ```
2. Navigate to the project directory:
 ```bash
   cd ielect
 ```
3. Create a virtual environment (recommended):
```bash
  python -m venv venv
 ```
4. Activate the virtual environment:
```bash
  .\venv\Scripts\activate
 ```
5. Install dependencies:
```bash
  pip install -r requirements.txt
 ```
6. Apply database migrations:
```bash
  python manage.py migrate
 ```
7. Create a superuser (for admin access):
```bash
  python manage.py createsuperuser
 ```
8. Run the development server:
```bash
  python manage.py runserver
 ```
9. Visit http://localhost:8000 in your web browser to access the application.

## Configuration
iElect requires minimal configuration. However, you can customize certain settings in the settings.py file.

## Contributing

Pull requests are welcome. For major changes, please open an issue first
to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License
iElect is licensed under the [MIT](https://github.com/ADNAN-an/iElect.git)
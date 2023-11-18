# Research Plant Growth AI

Research Plant Growth AI is an automated plant monitoring and analysis system designed to help you monitor the growth and health of your plants effectively. It allows you to capture images of your plants at regular intervals, timestamp them, perform growth analysis, generate reports, and more.

![Plant Growth Image](readme__image.jpg)

## Features

- **Image Capture:** Capture images of your plants at regular intervals to monitor their growth over time.

- **Timestamping:** Automatically timestamp images, providing accurate temporal tracking of plant growth.

- **Automated Schedule:** Set up automated schedules for image capturing at predetermined intervals to consistently monitor your plants.

- **Growth Analysis:** Track essential plant growth parameters, including height, leaf area, or number, based on the captured images.

- **Report Generation:** Generate growth reports with interactive graphs to facilitate data analysis and visualize plant growth trends.

- **User Management:** Support multiple user accounts with varying access levels and permissions to ensure privacy and collaboration.

- **Notifications:** Receive alerts about important events, such as abnormalities or issues with plant health, keeping you informed about your plants' well-being.

- **Disease Detection:** Utilize advanced analysis techniques to identify potential plant diseases or infections based on various factors, including leaf discoloration and the presence of pests.

## Getting Started

Follow these steps to get started with Research Plant Growth AI:

1. **Clone the Repository:**
   ```shell
   git clone https://github.com/bckyrd/research-plant-growth-ai.git

2. **Create sql db:**
   ```shell
   db_python

3. **install python:**
   ```shell
   pip install --upgrade pip

4. **pip install pip requirements:**
   ```shell
   pip install -r requirements.txt

5. **or install direct without requirements:**
   ```shell
  python -m pip install --upgrade pip && pip install fastapi sqlalchemy passlib pydantic uvicorn Pillow python-jose enum34 uuid mysql-connector-python python-multipart psycopg2-binary bcrypt tensorflow

6. **cd into api folder:**
   ```shell
   cd python__api

7. **run the api:**
   ```shell
   uvicorn --reload main:app

8. **start using from this page:**
   ```shell
   index.html
 

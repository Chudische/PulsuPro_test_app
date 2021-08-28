FROM python:3.6
WORKDIR /PulsuPro_test_app
COPY requirements.txt /PulsuPro_test_app
RUN pip install -r requirements.txt --ignore-installed 
COPY . /PulsuPro_test_app
EXPOSE 5000
FROM python:3.6
WORKDIR /PulsuPro_test_app
COPY req.txt /PulsuPro_test_app
RUN pip install -r req.txt --ignore-installed 
COPY . /PulsuPro_test_app
EXPOSE 5000
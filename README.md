# Test application 

### Task

За допомогою flask-admin (flask-admin.readthedocs.io) зробити каталог товару з характеристиками колір, вага, ціна та окремо адреси доставки товару з фільтрами як мінімум по країні, місту, вулиці.
Авторизацію в адмінці зробити за допомогою flask-security (flask-security-too.readthedocs.io).
Код тестового завдання викласти в гіт.
Буде плюсом завернути це все в Docker та/чи покрити тестами.

## Installation

1. Clone the repository::

     git clone https://github.com/Chudische/test_app.git
     cd test_app

2. Create and activate a virtual environment::

     virtualenv env
     source env/bin/activate

3. Install requirements::

     pip install -r 'requirements.txt'

4. Run the application::

     python app.py
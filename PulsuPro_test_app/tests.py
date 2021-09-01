import unittest

from flask.wrappers import Response
from flask_security import current_user
from flask_security.utils import login_user, encrypt_password
from app import app, Role, db, user_datastore

class appTestCase(unittest.TestCase):

    def setUp(self):               
        self.app = app
        self.app.config['LOGIN_DISABLED'] = True
        self.app.config['SQLALCHEMY_ECHO'] = False
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.client = self.app.test_client()
        self._ctx = self.app.test_request_context()
        self._ctx.push()
        db.drop_all()        
        db.create_all()
        with self.app.app_context():
            user_role = Role(name='user')
            super_user_role = Role(name='superuser')
            db.session.add(user_role)
            db.session.add(super_user_role)
            db.session.commit()

            self.test_admin = user_datastore.create_user(            
                email='admin@admin.com',
                password=encrypt_password('admin'),
                roles=[user_role, super_user_role]
            )
            self.test_user = user_datastore.create_user(            
                email='user@admin.com',
                password=encrypt_password('admin'),
                roles=[user_role, ]
            )
            db.session.commit()                    

    def tearDown(self):
        if self._ctx is not None:
            self._ctx.pop()

        db.session.remove()
        db.drop_all()

    def test_index_page(self):
        response = self.client.get('/')
        self.assertIn(b'<a href="/admin/">Click me to get to Admin!</a>', response.data)
    
    def test_user_authentication(self):
        """
        Check user authentication and roles
        """
        user = self.test_user
        db.session.add(user)
        login_user(user)        
        self.assertTrue(current_user.is_active and
                current_user.is_authenticated and not
                current_user.has_role('superuser')
        )

    def test_admin_authentication(self):
        """
        Check admin authentication and roles
        """
        user = self.test_admin
        db.session.add(user)
        login_user(user)        
        self.assertTrue(current_user.is_active and
                current_user.is_authenticated and 
                current_user.has_role('superuser')
        )

    def login(self, username, password):
        return self.client.post('/admin/login/', data=dict(
            email=username,
            password=password
        ), follow_redirects=True)

    def logout(self):   
        return self.client.get('/admin/logout/', follow_redirects=True)


    def test_visible_admin_tabs(self):
        """
        Check is Catalog tab and Delivery tab is visible for admin and not visible for user
        """
        # Test admin login with valid password
        response = self.login('admin@admin.com', 'admin')        
        self.assertIn(b'href="/admin/catalog_unit/"', response.data)
        res = self.logout()
        self.assertIn(b'href="/admin/login/"' , res.data)
        # Test user login with valid password
        response = self.login('user@admin.com', 'admin')        
        self.assertNotIn(b'href="/admin/catalog_unit/"', response.data)
        res = self.logout()
        self.assertIn(b'href="/admin/login/"', res.data)

    def test_accessible_admin_tabs(self):
        """
        Check is Catalog tab and Delivery tab is accessible for admin and not accessible for user
        """ 
        # Test admin login with valid password
        self.login('admin@admin.com', 'admin')
        url = '/admin/catalog_unit/'
        response = self.client.get(url)
        self.assertTrue(response.status, '200')
        self.assertEqual(response.request.path, url)
        self.logout()
        # Test user login with valid password
        self.login('user@admin.com', 'admin')
        url = '/admin/catalog_unit/'
        response = self.client.get(url)
        self.assertTrue(response.status, '403')



    def test_login_logout(self):
        # Test admin login with valid password
        response = self.login('admin@admin.com', 'admin')
        self.assertEqual(response.request.path, '/admin/')        
        self.assertIn(b'href="/admin/catalog_unit/"', response.data)
        res = self.logout()
        self.assertIn(b'href="/admin/login/"', res.data)
        # Test admin login with invalid password
        response = self.login('admin@admin.com', 'other')
        self.assertEqual(response.request.path, '/admin/login/')
        self.assertIn(b'Invalid password', response.data)
        

if __name__ == '__main__':
    unittest.main()
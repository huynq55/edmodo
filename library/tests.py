from django.test import TestCase
from django.contrib.auth.models import User

class LibraryTest(TestCase):
    def test_register_page(self):
        data={
            'username':'admin',
            'email':'email@gmail.com',
            'password1':'123456',
            'password2':'123456',
        }
        response = self.client.post('/register/',data)
        self.assertContains(response,"Register")
    def test_login(self):
        response = self.client.post('/accounts/login/',{
            'usename' : 'admin',
            'password' : 'admin',
        })
        self.assertEqual(response.status_code, 200)

    def test_upload_book(self):
        response = self.client.post('/accounts/login/',{
            'usename' : 'admin',
            'password' : 'admin',
            })
        self.assertEqual(response.status_code, 200)
        self.client.post('/upload/book/',{
            'title': 'Test',
            'up_file':'E:\RELAX\hehe.pdf',
            'description':'test',
        })
        self.assertEqual(response.status_code, 200)
    def test_upload_image(self):
        response = self.client.post('/accounts/login/',{
            'usename' : 'admin',
            'password' : 'admin',
            })
        self.assertEqual(response.status_code, 200)
        self.client.post('/upload/image/',{
            'title': 'Test',
            'up_file':'E:\RELAX\hehe.jpg',
            'description':'test',
            })
        self.assertEqual(response.status_code, 200)
    def test_add_image_link(self):
        response = self.client.post('/accounts/login/',{
            'usename' : 'admin',
            'password' : 'admin',
            })
        self.assertEqual(response.status_code, 200)
        self.client.post('/upload/image_link/',{
            'title': 'Test',
            'link':'http://cyears.files.wordpress.com/2011/04/image4.jpg',
            'description':'test',
            })
        self.assertEqual(response.status_code, 200)

    def test_add_video_link(self):
        response = self.client.post('/accounts/login/',{
            'usename' : 'admin',
            'password' : 'admin',
            })
        self.assertEqual(response.status_code, 200)
        self.client.post('/upload/video_link/',{
            'title': 'Test',
            'link':'http://youtu.be/IQJXFSAn-es',
            'description':'test',
            })
        self.assertEqual(response.status_code, 200)


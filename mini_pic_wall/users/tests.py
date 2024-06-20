from django.urls import resolve
from django.contrib.auth.models import User
from rest_framework import test
from rest_framework.reverse import reverse
from collages.models import Collage
from pictures.tests import make_image_bytes, make_picture


class UserViewAPITestCase(test.APITestCase):
    def setUp(self):
        self.factory = test.APIRequestFactory()

    def test_list_users(self):
        user1 = User.objects.create(username='user_name_1')
        user2 = User.objects.create(username='user_name_2')

        url = reverse('user-list')
        request = self.factory.get(url)
        response = resolve(url).func(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 2)
        self.assertEqual(response.data['results'][0]['url'],
                         reverse('user-detail', request=request, args=[user1.username]))
        self.assertEqual(response.data['results'][0]['username'], user1.username)
        self.assertEqual(response.data['results'][1]['url'],
                         reverse('user-detail', request=request, args=[user2.username]))
        self.assertEqual(response.data['results'][1]['username'], user2.username)

    def test_create_user(self):
        data = {
            'username': 'user',
            'email': 'user@example.com',
            'password': 'password',
        }

        url = reverse('user-list')
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(User.objects.count(), 1)
        user = User.objects.get()
        self.assertEqual(user.username, data['username'])
        self.assertEqual(user.email, data['email'])
        self.assertTrue(user.check_password(data['password']))

    def test_create_user_with_invalid_username(self):
        data = {
            'username': 'invalid username',
            'email': 'user@example.com',
            'password': 'password',
        }

        url = reverse('user-list')
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(User.objects.count(), 0)

    def test_retrieve_user(self):
        user = User.objects.create(username='user_name')

        url = reverse('user-detail', args=[user.username])
        request = self.factory.get(url)
        response = resolve(url).func(request, username=user.username)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['username'], user.username)
        self.assertEqual(response.data['change'],
                         reverse('user-change', request=request, args=[user.username]))
        self.assertEqual(response.data['deactivate'],
                         reverse('user-deactivate', request=request, args=[user.username]))
        self.assertEqual(response.data['pictures'],
                         reverse('user-pictures', request=request, args=[user.username]))
        self.assertEqual(response.data['collages'],
                         reverse('user-collages', request=request, args=[user.username]))

    def test_deactivate_user(self):
        data = {'password': 'test password'}
        user = User.objects.create_user('user_name', password=data['password'])

        url = reverse('user-deactivate', args=[user.username])
        self.client.force_authenticate(user=user)
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, 200)
        user.refresh_from_db()
        self.assertFalse(user.is_active)

    def test_deactivate_user_with_no_auth(self):
        data = {'password': 'test password'}
        user = User.objects.create_user('user_name', password=data['password'])

        url = reverse('user-deactivate', args=[user.username])
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, 403)
        user.refresh_from_db()
        self.assertTrue(user.is_active)

    def test_deactivate_user_using_wrong_user(self):
        wrong_user = User.objects.create(username='wrong_user')
        data = {'password': 'test password'}
        user = User.objects.create_user('user_name', password=data['password'])

        url = reverse('user-deactivate', args=[user.username])
        self.client.force_authenticate(user=wrong_user)
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, 403)
        user.refresh_from_db()
        self.assertTrue(user.is_active)

    def test_deactivate_user_using_no_password(self):
        user = User.objects.create_user('user_name', password='strong password')

        url = reverse('user-deactivate', args=[user.username])
        self.client.force_authenticate(user=user)
        response = self.client.post(url)

        self.assertEqual(response.status_code, 400)
        user.refresh_from_db()
        self.assertTrue(user.is_active)

    def test_deactivate_user_using_wrong_password(self):
        data = {'password': 'wrong password'}
        user = User.objects.create_user('user_name', password='correct password')

        url = reverse('user-deactivate', args=[user.username])
        self.client.force_authenticate(user=user)
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, 400)
        user.refresh_from_db()
        self.assertTrue(user.is_active)

    def test_change_user(self):
        data = {
            'username': 'new_username',
            'email': 'new_email@example.com',
            'password': 'new password',
            'old_password': 'old password'
        }
        user = User.objects.create_user('user_name', password=data['old_password'])

        url = reverse('user-change', args=[user.username])
        self.client.force_authenticate(user=user)
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, 200)
        user.refresh_from_db()
        self.assertEqual(user.username, data['username'])
        self.assertEqual(user.email, data['email'])
        self.assertTrue(user.check_password(data['password']))

    def test_change_user_with_no_auth(self):
        data = {
            'username': 'new_username',
            'email': 'new_email@example.com',
            'password': 'new password',
            'old_password': 'old password'
        }
        user = User.objects.create_user('user_name', password=data['old_password'])

        url = reverse('user-change', args=[user.username])
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, 403)
        user.refresh_from_db()
        self.assertNotEqual(user.username, data['username'])
        self.assertNotEqual(user.email, data['email'])
        self.assertFalse(user.check_password(data['password']))

    def test_change_user_using_wrong_user(self):
        data = {
            'username': 'new_username',
            'email': 'new_email@example.com',
            'password': 'new password',
            'old_password': 'old password'
        }
        wrong_user = User.objects.create(username='wrong user')
        user = User.objects.create_user('user_name', password=data['old_password'])

        url = reverse('user-change', args=[user.username])
        self.client.force_authenticate(user=wrong_user)
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, 403)
        user.refresh_from_db()
        self.assertNotEqual(user.username, data['username'])
        self.assertNotEqual(user.email, data['email'])
        self.assertFalse(user.check_password(data['password']))

    def test_change_user_using_no_password(self):
        data = {
            'username': 'new_username',
            'email': 'new_email@example.com',
            'password': 'new password',
        }
        user = User.objects.create(username='user_name')

        url = reverse('user-change', args=[user.username])
        self.client.force_authenticate(user=user)
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, 400)
        user.refresh_from_db()
        self.assertNotEqual(user.username, data['username'])
        self.assertNotEqual(user.email, data['email'])
        self.assertFalse(user.check_password(data['password']))

    def test_change_user_using_wrong_password(self):
        data = {
            'username': 'new_username',
            'email': 'new_email@example.com',
            'password': 'new password',
            'old_password': 'wrong password'
        }
        user = User.objects.create_user('user_name', password='correct password')

        url = reverse('user-change', args=[user.username])
        self.client.force_authenticate(user=user)
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, 400)
        user.refresh_from_db()
        self.assertNotEqual(user.username, data['username'])
        self.assertNotEqual(user.email, data['email'])
        self.assertFalse(user.check_password(data['password']))

    def test_change_username_to_invalid(self):
        data = {
            'username': 'invalid username',
            'email': 'new_email@example.com',
            'password': 'new password',
            'old_password': 'old password'
        }
        user = User.objects.create_user('user_name', password=data['old_password'])

        url = reverse('user-change', args=[user.username])
        self.client.force_authenticate(user=user)
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, 400)
        user.refresh_from_db()
        self.assertNotEqual(user.username, data['username'])
        self.assertNotEqual(user.email, data['email'])
        self.assertFalse(user.check_password(data['password']))

    def test_list_user_pictures(self):
        user = User.objects.create(username='user')
        picture1 = make_picture(name='name 1', owner=user)
        picture2 = make_picture(name='name 2', owner=user)

        url = reverse('user-pictures', args=[user.username])
        request = self.factory.get(url)
        response = resolve(url).func(request, username=user.username)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 2)

        self.assertEqual(response.data['results'][0]['url'],
                         reverse('picture-detail', request=request, args=[picture1.pk]))
        self.assertEqual(response.data['results'][0]['name'], picture1.name)
        self.assertIn('thumbnail', response.data['results'][0])

        self.assertEqual(response.data['results'][1]['url'],
                         reverse('picture-detail', request=request, args=[picture2.pk]))
        self.assertEqual(response.data['results'][1]['name'], picture2.name)
        self.assertIn('thumbnail', response.data['results'][1])

    def test_upload_picture(self):
        data = {
            'name': 'name for picture',
            'image': make_image_bytes()
        }
        user = User.objects.create(username='user')

        url = reverse('user-pictures', args=[user.username])
        self.client.force_authenticate(user=user)
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(user.pictures.count(), 1)

    def test_upload_picture_with_no_auth(self):
        data = {
            'name': 'name for picture',
            'image': make_image_bytes()
        }
        user = User.objects.create(username='user')

        url = reverse('user-pictures', args=[user.username])
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, 403)
        self.assertEqual(user.pictures.count(), 0)

    def test_upload_picture_using_wrong_user(self):
        data = {
            'name': 'name for picture',
            'image': make_image_bytes()
        }
        user = User.objects.create(username='user')
        wrong_user = User.objects.create(username='wrong_user')

        url = reverse('user-pictures', args=[user.username])
        self.client.force_authenticate(user=wrong_user)
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, 403)
        self.assertEqual(user.pictures.count(), 0)

    def test_list_user_collages(self):
        user = User.objects.create(username='user')
        collage1 = Collage.objects.create(name='collage1', owner=user)
        collage2 = Collage.objects.create(name='collage2', owner=user)

        url = reverse('user-collages', args=[user.username])
        request = self.factory.get(url)
        response = resolve(url).func(request, username=user.username)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 2)
        self.assertEqual(response.data['results'][0]['url'],
                         reverse('collage-detail', request=request, args=[collage1.pk]))
        self.assertEqual(response.data['results'][0]['name'], collage1.name)
        self.assertEqual(response.data['results'][1]['url'],
                         reverse('collage-detail', request=request, args=[collage2.pk]))
        self.assertEqual(response.data['results'][1]['name'], collage2.name)

    def test_create_collage(self):
        user = User.objects.create(username='user')
        data = {'name': 'name of collage'}

        url = reverse('user-collages', args=[user.username])
        self.client.force_authenticate(user=user)
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, 201)
        collage = Collage.objects.get()
        self.assertEqual(collage.name, data['name'])
        self.assertEqual(collage.owner, user)

    def test_create_collage_with_no_auth(self):
        user = User.objects.create(username='user')
        data = {'name': 'name of collage'}

        url = reverse('user-collages', args=[user.username])
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, 403)
        self.assertEqual(Collage.objects.all().count(), 0)

    def test_create_collage_using_wrong_user(self):
        wrong_user = User.objects.create(username='wrong_user')
        user = User.objects.create(username='user')
        data = {'name': 'name of collage'}

        url = reverse('user-collages', args=[user.username])
        self.client.force_authenticate(user=wrong_user)
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, 403)
        self.assertEqual(Collage.objects.all().count(), 0)

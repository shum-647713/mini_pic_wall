from rest_framework.reverse import reverse
from rest_framework import test
from django.urls import resolve
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from .models import Picture, Collage
from PIL import Image
import io


class UserViewAPITestCase(test.APITestCase):
    def setUp(self):
        self.factory = test.APIRequestFactory()

    @staticmethod
    def make_user_with_password(password='strong password', username='user_name'):
        user = User.objects.create(username=username)
        user.set_password(password)
        user.save()
        return user

    @staticmethod
    def make_image():
        image_bytes = io.BytesIO()
        image = Image.new('RGBA', size=(16, 16), color=(95, 0, 0))
        image.save(image_bytes, 'png')
        image_bytes.name = 'test.png'
        image_bytes.seek(0)
        return image_bytes

    @staticmethod
    def make_picture(owner=None):
        if owner is None:
            owner = User.objects.create(username='user_name')
        image = PictureViewAPITestCase.make_image().read()
        image = SimpleUploadedFile(name='test_image.png', content=image, content_type='image/png')
        return Picture.objects.create(image=image, owner=owner)

    def test_list_users(self):
        user1 = User.objects.create(username='user1')
        user2 = User.objects.create(username='user2')

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
        self.assertEqual(User.objects.all().count(), 1)
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
        self.assertEqual(User.objects.all().count(), 0)

    def test_retrieve_user(self):
        user = User.objects.create(username='user')

        url = reverse('user-detail', args=[user.username])
        request = self.factory.get(url)
        response = resolve(url).func(request, username=user.username)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['username'], user.username)
        self.assertEqual(response.data['deactivate'],
                         reverse('user-deactivate', request=request, args=[user.username]))
        self.assertEqual(response.data['pictures'],
                         reverse('user-pictures', request=request, args=[user.username]))
        self.assertEqual(response.data['collages'],
                         reverse('user-collages', request=request, args=[user.username]))

    def test_deactivate_user(self):
        data = {'password': 'test password'}
        user = self.make_user_with_password(data['password'])

        url = reverse('user-deactivate', args=[user.username])
        self.client.force_authenticate(user=user)
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, 200)
        user.refresh_from_db()
        self.assertFalse(user.is_active)

    def test_deactivate_user_with_no_auth(self):
        data = {'password': 'test password'}
        user = self.make_user_with_password(data['password'])

        url = reverse('user-deactivate', args=[user.username])
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, 403)
        user.refresh_from_db()
        self.assertTrue(user.is_active)

    def test_deactivate_user_using_wrong_user(self):
        wrong_user = User.objects.create(username='wrong_user')
        data = {'password': 'test password'}
        user = self.make_user_with_password(data['password'])

        url = reverse('user-deactivate', args=[user.username])
        self.client.force_authenticate(user=wrong_user)
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, 403)
        user.refresh_from_db()
        self.assertTrue(user.is_active)

    def test_deactivate_user_using_no_password(self):
        user = self.make_user_with_password()

        url = reverse('user-deactivate', args=[user.username])
        self.client.force_authenticate(user=user)
        response = self.client.post(url)

        self.assertEqual(response.status_code, 400)
        user.refresh_from_db()
        self.assertTrue(user.is_active)

    def test_deactivate_user_using_wrong_password(self):
        data = {'password': 'wrong password'}
        user = self.make_user_with_password('correct password')
        user.save()

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
        user = self.make_user_with_password(data['old_password'])

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
        user = self.make_user_with_password(data['old_password'])

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
        user = self.make_user_with_password(data['old_password'])

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
        user = self.make_user_with_password()

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
        user = self.make_user_with_password('correct password')

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
        user = self.make_user_with_password(data['old_password'])

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
        picture1 = self.make_picture(owner=user)
        picture2 = self.make_picture(owner=user)

        url = reverse('user-pictures', args=[user.username])
        request = self.factory.get(url)
        response = resolve(url).func(request, username=user.username)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 2)
        self.assertEqual(response.data['results'][0]['url'],
                         reverse('picture-detail', request=request, args=[picture1.pk]))
        self.assertEqual(response.data['results'][0]['image'],
                         request.build_absolute_uri(picture1.image.url))
        self.assertEqual(response.data['results'][1]['url'],
                         reverse('picture-detail', request=request, args=[picture2.pk]))
        self.assertEqual(response.data['results'][1]['image'],
                         request.build_absolute_uri(picture2.image.url))

    def test_upload_picture(self):
        data = {'image': self.make_image()}
        user = User.objects.create(username='user')

        url = reverse('user-pictures', args=[user.username])
        self.client.force_authenticate(user=user)
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(user.pictures.count(), 1)

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


class PictureViewAPITestCase(test.APITestCase):
    def setUp(self):
        self.factory = test.APIRequestFactory()

    @staticmethod
    def make_image():
        image_bytes = io.BytesIO()
        image = Image.new('RGBA', size=(16, 16), color=(95, 0, 0))
        image.save(image_bytes, 'png')
        image_bytes.name = 'test.png'
        image_bytes.seek(0)
        return image_bytes

    @staticmethod
    def make_picture(owner=None):
        if owner is None:
            owner = User.objects.create(username='user_name')
        image = PictureViewAPITestCase.make_image().read()
        image = SimpleUploadedFile(name='test_image.png', content=image, content_type='image/png')
        return Picture.objects.create(image=image, owner=owner)

    def test_list_pictures(self):
        user1 = User.objects.create(username='user_name_1')
        picture1 = self.make_picture(user1)
        user2 = User.objects.create(username='user_name_2')
        picture2 = self.make_picture(user2)

        url = reverse('picture-list')
        request = self.factory.get(url)
        response = resolve(url).func(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 2)
        self.assertEqual(response.data['results'][0]['url'],
                         reverse('picture-detail', request=request, args=[picture1.pk]))
        self.assertEqual(response.data['results'][0]['image'],
                         request.build_absolute_uri(picture1.image.url))
        self.assertEqual(response.data['results'][1]['url'],
                         reverse('picture-detail', request=request, args=[picture2.pk]))
        self.assertEqual(response.data['results'][1]['image'],
                         request.build_absolute_uri(picture2.image.url))

    def test_retrieve_picture(self):
        picture = self.make_picture()

        url = reverse('picture-detail', args=[picture.pk])
        request = self.factory.get(url)
        response = resolve(url).func(request, pk=picture.pk)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['image'],
                         request.build_absolute_uri(picture.image.url))
        self.assertEqual(response.data['collages'],
                         reverse('picture-collages', request=request, args=[picture.pk]))
        self.assertEqual(response.data['attach'],
                         reverse('picture-attach', request=request, args=[picture.pk]))
        self.assertEqual(response.data['detach'],
                         reverse('picture-detach', request=request, args=[picture.pk]))
        self.assertEqual(response.data['owner']['url'],
                         reverse('user-detail', request=request, args=[picture.owner.username]))
        self.assertEqual(response.data['owner']['username'], picture.owner.username)

    def test_list_picture_collages(self):
        picture = self.make_picture()
        collage1 = Collage.objects.create(name='collage1', owner=picture.owner)
        collage2 = Collage.objects.create(name='collage2', owner=picture.owner)
        picture.collages.add(collage1, collage2)

        url = reverse('picture-collages', args=[picture.pk])
        request = self.factory.get(url)
        response = resolve(url).func(request, pk=picture.pk)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 2)
        self.assertEqual(response.data['results'][0]['url'],
                         reverse('collage-detail', request=request, args=[collage1.pk]))
        self.assertEqual(response.data['results'][0]['name'], collage1.name)
        self.assertEqual(response.data['results'][1]['url'],
                         reverse('collage-detail', request=request, args=[collage2.pk]))
        self.assertEqual(response.data['results'][1]['name'], collage2.name)

    def test_list_collages_to_attach(self):
        picture = self.make_picture()
        collage1 = Collage.objects.create(name='collage1', owner=picture.owner)
        collage2 = Collage.objects.create(name='collage2', owner=picture.owner)
        another_user = User.objects.create(username='another_user')
        another_collage = Collage.objects.create(owner=another_user)

        url = reverse('picture-attach', args=[picture.pk])
        request = self.factory.get(url)
        response = resolve(url).func(request, pk=picture.pk)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 2)
        self.assertEqual(response.data['results'][0]['url'],
                         reverse('collage-detail', request=request, args=[collage1.pk]))
        self.assertEqual(response.data['results'][0]['name'], collage1.name)
        self.assertEqual(response.data['results'][0]['attach'],
                         reverse('picture-attach-collage', request=request, args=[picture.pk, collage1.pk]))
        self.assertEqual(response.data['results'][1]['url'],
                         reverse('collage-detail', request=request, args=[collage2.pk]))
        self.assertEqual(response.data['results'][1]['name'], collage2.name)
        self.assertEqual(response.data['results'][1]['attach'],
                         reverse('picture-attach-collage', request=request, args=[picture.pk, collage2.pk]))

    def test_attach_to_collage(self):
        picture = self.make_picture()
        collage = Collage.objects.create(owner=picture.owner)

        url = reverse('picture-attach-collage', args=[picture.pk, collage.pk])
        self.client.force_authenticate(user=picture.owner)
        response = self.client.post(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(picture.collages.count(), 1)
        self.assertEqual(picture.collages.get().name, collage.name)

    def test_attach_to_collage_with_no_auth(self):
        picture = self.make_picture()
        collage = Collage.objects.create(owner=picture.owner)

        url = reverse('picture-attach-collage', args=[picture.pk, collage.pk])
        response = self.client.post(url)

        self.assertEqual(response.status_code, 403)
        self.assertEqual(picture.collages.count(), 0)

    def test_attach_to_collage_using_wrong_user(self):
        picture = self.make_picture()
        collage = Collage.objects.create(owner=picture.owner)
        wrong_user = User.objects.create(username='wrong_user')

        url = reverse('picture-attach-collage', args=[picture.pk, collage.pk])
        self.client.force_authenticate(user=wrong_user)
        response = self.client.post(url)

        self.assertEqual(response.status_code, 403)
        self.assertEqual(picture.collages.count(), 0)

    def test_attach_to_collage_while_not_owning_picture(self):
        picture = self.make_picture()
        wrong_user = User.objects.create(username='wrong_user')
        collage = Collage.objects.create(owner=wrong_user)

        url = reverse('picture-attach-collage', args=[picture.pk, collage.pk])
        self.client.force_authenticate(user=wrong_user)
        response = self.client.post(url)

        self.assertEqual(response.status_code, 403)
        self.assertEqual(picture.collages.count(), 0)

    def test_attach_to_collage_while_not_owning_collage(self):
        picture = self.make_picture()
        collage_owner = User.objects.create(username='collage_owner')
        collage = Collage.objects.create(owner=collage_owner)

        url = reverse('picture-attach-collage', args=[picture.pk, collage.pk])
        self.client.force_authenticate(user=picture.owner)
        response = self.client.post(url)

        self.assertEqual(response.status_code, 403)
        self.assertEqual(picture.collages.count(), 0)

    def test_list_collages_to_detach(self):
        picture = self.make_picture()
        collage1 = Collage.objects.create(name='collage1', owner=picture.owner)
        collage2 = Collage.objects.create(name='collage2', owner=picture.owner)
        collage3 = Collage.objects.create(name='collage3', owner=picture.owner)
        picture.collages.add(collage1, collage3)
        another_user = User.objects.create(username='another_user')
        another_collage = Collage.objects.create(owner=another_user)

        url = reverse('picture-detach', args=[picture.pk])
        request = self.factory.get(url)
        response = resolve(url).func(request, pk=picture.pk)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 2)
        self.assertEqual(response.data['results'][0]['url'],
                         reverse('collage-detail', request=request, args=[collage1.pk]))
        self.assertEqual(response.data['results'][0]['name'], collage1.name)
        self.assertEqual(response.data['results'][0]['detach'],
                         reverse('picture-detach-collage', request=request, args=[picture.pk, collage1.pk]))
        self.assertEqual(response.data['results'][1]['url'],
                         reverse('collage-detail', request=request, args=[collage3.pk]))
        self.assertEqual(response.data['results'][1]['name'], collage3.name)
        self.assertEqual(response.data['results'][1]['detach'],
                         reverse('picture-detach-collage', request=request, args=[picture.pk, collage3.pk]))

    def test_detach_from_collage(self):
        picture = self.make_picture()
        collage = Collage.objects.create(owner=picture.owner)
        picture.collages.add(collage)

        url = reverse('picture-detach-collage', args=[picture.pk, collage.pk])
        self.client.force_authenticate(user=picture.owner)
        response = self.client.post(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(picture.collages.all().count(), 0)

    def test_detach_from_collage_with_no_auth(self):
        picture = self.make_picture()
        collage = Collage.objects.create(owner=picture.owner)
        picture.collages.add(collage)

        url = reverse('picture-detach-collage', args=[picture.pk, collage.pk])
        response = self.client.post(url)

        self.assertEqual(response.status_code, 403)
        self.assertEqual(picture.collages.all().count(), 1)

    def test_detach_from_collage_using_wrong_user(self):
        picture = self.make_picture()
        collage = Collage.objects.create(owner=picture.owner)
        picture.collages.add(collage)
        wrong_user = User.objects.create(username='wrong_user')

        url = reverse('picture-detach-collage', args=[picture.pk, collage.pk])
        self.client.force_authenticate(user=wrong_user)
        response = self.client.post(url)

        self.assertEqual(response.status_code, 403)
        self.assertEqual(picture.collages.all().count(), 1)


class CollageViewAPITestCase(test.APITestCase):
    def setUp(self):
        self.factory = test.APIRequestFactory()

    @staticmethod
    def make_image():
        image_bytes = io.BytesIO()
        image = Image.new('RGBA', size=(16, 16), color=(95, 0, 0))
        image.save(image_bytes, 'png')
        image_bytes.name = 'test.png'
        image_bytes.seek(0)
        return image_bytes

    @staticmethod
    def make_picture(owner=None):
        if owner is None:
            owner = User.objects.create(username='user_name')
        image = PictureViewAPITestCase.make_image().read()
        image = SimpleUploadedFile(name='test_image.png', content=image, content_type='image/png')
        return Picture.objects.create(image=image, owner=owner)

    def test_list_collages(self):
        user = User.objects.create(username='user_name')
        collage1 = Collage.objects.create(name='collage1', owner=user)
        collage2 = Collage.objects.create(name='collage2', owner=user)

        url = reverse('collage-list')
        request = self.factory.get(url)
        response = resolve(url).func(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 2)
        self.assertEqual(response.data['results'][0]['url'],
                         reverse('collage-detail', request=request, args=[collage1.pk]))
        self.assertEqual(response.data['results'][0]['name'], collage1.name)
        self.assertEqual(response.data['results'][1]['url'],
                         reverse('collage-detail', request=request, args=[collage2.pk]))
        self.assertEqual(response.data['results'][1]['name'], collage2.name)

    def test_retrieve_collage(self):
        user = User.objects.create(username='user_name')
        collage = Collage.objects.create(name='name of collage', owner=user)

        url = reverse('collage-detail', args=[collage.pk])
        request = self.factory.get(url)
        response = resolve(url).func(request, pk=collage.pk)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['name'], collage.name)
        self.assertEqual(response.data['pictures'],
                         reverse('collage-pictures', request=request, args=[collage.pk]))
        self.assertEqual(response.data['attach'],
                         reverse('collage-attach', request=request, args=[collage.pk]))
        self.assertEqual(response.data['detach'],
                         reverse('collage-detach', request=request, args=[collage.pk]))
        self.assertEqual(response.data['owner']['url'],
                         reverse('user-detail', request=request, args=[user.username]))
        self.assertEqual(response.data['owner']['username'], user.username)

    def test_list_collage_pictures(self):
        user = User.objects.create(username='user_name')
        collage = Collage.objects.create(name='name of collage', owner=user)
        picture1 = self.make_picture(owner=user)
        picture2 = self.make_picture(owner=user)
        collage.pictures.add(picture1, picture2)
        another_user = User.objects.create(username='another_user')
        another_picture = self.make_picture(owner=another_user)

        url = reverse('collage-pictures', args=[collage.pk])
        request = self.factory.get(url)
        response = resolve(url).func(request, pk=collage.pk)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 2)
        self.assertEqual(response.data['results'][0]['url'],
                         reverse('picture-detail', request=request, args=[picture1.pk]))
        self.assertEqual(response.data['results'][0]['image'],
                         request.build_absolute_uri(picture1.image.url))
        self.assertEqual(response.data['results'][1]['url'],
                         reverse('picture-detail', request=request, args=[picture2.pk]))
        self.assertEqual(response.data['results'][1]['image'],
                         request.build_absolute_uri(picture2.image.url))

    def test_list_pictures_to_attach(self):
        user = User.objects.create(username='user_name')
        collage = Collage.objects.create(name='name of collage', owner=user)
        picture1 = self.make_picture(owner=user)
        picture2 = self.make_picture(owner=user)
        another_user = User.objects.create(username='another_user')
        another_picture = self.make_picture(owner=another_user)

        url = reverse('collage-attach', args=[collage.pk])
        request = self.factory.get(url)
        response = resolve(url).func(request, pk=collage.pk)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 2)
        self.assertEqual(response.data['results'][0]['url'],
                         reverse('picture-detail', request=request, args=[picture1.pk]))
        self.assertEqual(response.data['results'][0]['attach'],
                         reverse('collage-attach-picture', request=request, args=[collage.pk, picture1.pk]))
        self.assertEqual(response.data['results'][1]['url'],
                         reverse('picture-detail', request=request, args=[picture2.pk]))
        self.assertEqual(response.data['results'][1]['attach'],
                         reverse('collage-attach-picture', request=request, args=[collage.pk, picture2.pk]))

    def test_attach_picture(self):
        user = User.objects.create(username='user_name')
        collage = Collage.objects.create(name='name of collage', owner=user)
        picture = self.make_picture(owner=user)

        url = reverse('collage-attach-picture', args=[collage.pk, picture.pk])
        self.client.force_authenticate(user=user)
        response = self.client.post(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(collage.pictures.count(), 1)
        self.assertEqual(collage.pictures.get(), picture)

    def test_attach_picture_with_no_auth(self):
        user = User.objects.create(username='user_name')
        collage = Collage.objects.create(name='name of collage', owner=user)
        picture = self.make_picture(owner=user)

        url = reverse('collage-attach-picture', args=[collage.pk, picture.pk])
        response = self.client.post(url)

        self.assertEqual(response.status_code, 403)
        self.assertEqual(collage.pictures.count(), 0)

    def test_attach_picture_using_wrong_user(self):
        user = User.objects.create(username='user_name')
        collage = Collage.objects.create(name='name of collage', owner=user)
        picture = self.make_picture(owner=user)
        wrong_user = User.objects.create(username='wrong_user')

        url = reverse('collage-attach-picture', args=[collage.pk, picture.pk])
        self.client.force_authenticate(user=wrong_user)
        response = self.client.post(url)

        self.assertEqual(response.status_code, 403)
        self.assertEqual(collage.pictures.count(), 0)

    def test_attach_picture_while_not_owning_collage(self):
        user = User.objects.create(username='user')
        collage = Collage.objects.create(name='name of collage', owner=user)
        picture = self.make_picture()

        url = reverse('collage-attach-picture', args=[collage.pk, picture.pk])
        self.client.force_authenticate(user=picture.owner)
        response = self.client.post(url)

        self.assertEqual(response.status_code, 403)
        self.assertEqual(collage.pictures.count(), 0)

    def test_attach_picture_while_not_owning_picture(self):
        user = User.objects.create(username='user')
        collage = Collage.objects.create(name='name of collage', owner=user)
        picture = self.make_picture()

        url = reverse('collage-attach-picture', args=[collage.pk, picture.pk])
        self.client.force_authenticate(user=user)
        response = self.client.post(url)

        self.assertEqual(response.status_code, 403)
        self.assertEqual(collage.pictures.count(), 0)

    def test_list_pictures_to_detach(self):
        user = User.objects.create(username='user_name')
        collage = Collage.objects.create(name='name of collage', owner=user)
        picture1 = self.make_picture(owner=user)
        picture2 = self.make_picture(owner=user)
        picture3 = self.make_picture(owner=user)
        collage.pictures.add(picture1, picture3)
        another_user = User.objects.create(username='another_user')
        another_picture = self.make_picture(owner=another_user)

        url = reverse('collage-detach', args=[collage.pk])
        request = self.factory.get(url)
        response = resolve(url).func(request, pk=collage.pk)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 2)
        self.assertEqual(response.data['results'][0]['url'],
                         reverse('picture-detail', request=request, args=[picture1.pk]))
        self.assertEqual(response.data['results'][0]['detach'],
                         reverse('collage-detach-picture', request=request, args=[collage.pk, picture1.pk]))
        self.assertEqual(response.data['results'][1]['url'],
                         reverse('picture-detail', request=request, args=[picture3.pk]))
        self.assertEqual(response.data['results'][1]['detach'],
                         reverse('collage-detach-picture', request=request, args=[collage.pk, picture3.pk]))

    def test_detach_picture(self):
        user = User.objects.create(username='user_name')
        collage = Collage.objects.create(name='name of collage', owner=user)
        picture = self.make_picture(owner=user)
        collage.pictures.add(picture)

        url = reverse('collage-detach-picture', args=[collage.pk, picture.pk])
        self.client.force_authenticate(user=user)
        response = self.client.post(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(collage.pictures.count(), 0)

    def test_detach_picture_with_no_auth(self):
        user = User.objects.create(username='user_name')
        collage = Collage.objects.create(name='name of collage', owner=user)
        picture = self.make_picture(owner=user)
        collage.pictures.add(picture)

        url = reverse('collage-detach-picture', args=[collage.pk, picture.pk])
        response = self.client.post(url)

        self.assertEqual(response.status_code, 403)
        self.assertEqual(collage.pictures.count(), 1)

    def test_detach_picture_using_wrong_user(self):
        user = User.objects.create(username='user_name')
        collage = Collage.objects.create(name='name of collage', owner=user)
        picture = self.make_picture(owner=user)
        collage.pictures.add(picture)
        wrong_user = User.objects.create(username='wrong_user')

        url = reverse('collage-detach-picture', args=[collage.pk, picture.pk])
        self.client.force_authenticate(user=wrong_user)
        response = self.client.post(url)

        self.assertEqual(response.status_code, 403)
        self.assertEqual(collage.pictures.count(), 1)

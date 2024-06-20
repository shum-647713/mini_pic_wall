from django.urls import resolve
from django.contrib.auth.models import User
from rest_framework import test
from rest_framework.reverse import reverse
from pictures.tests import make_picture
from .models import Collage


class CollageViewAPITestCase(test.APITestCase):
    def setUp(self):
        self.factory = test.APIRequestFactory()

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
        picture1 = make_picture(owner=user)
        picture2 = make_picture(owner=user)
        collage.pictures.add(picture1, picture2)
        another_user = User.objects.create(username='another_user')
        another_picture = make_picture(owner=another_user)

        url = reverse('collage-pictures', args=[collage.pk])
        request = self.factory.get(url)
        response = resolve(url).func(request, pk=collage.pk)

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

    def test_list_pictures_to_attach(self):
        user = User.objects.create(username='user_name')
        collage = Collage.objects.create(name='name of collage', owner=user)
        picture1 = make_picture(owner=user)
        picture2 = make_picture(owner=user)
        another_user = User.objects.create(username='another_user')
        another_picture = make_picture(owner=another_user)

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
        picture = make_picture(owner=user)

        url = reverse('collage-attach-picture', args=[collage.pk, picture.pk])
        self.client.force_authenticate(user=user)
        response = self.client.post(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(collage.pictures.count(), 1)
        self.assertEqual(collage.pictures.get(), picture)

    def test_attach_picture_with_no_auth(self):
        user = User.objects.create(username='user_name')
        collage = Collage.objects.create(name='name of collage', owner=user)
        picture = make_picture(owner=user)

        url = reverse('collage-attach-picture', args=[collage.pk, picture.pk])
        response = self.client.post(url)

        self.assertEqual(response.status_code, 403)
        self.assertEqual(collage.pictures.count(), 0)

    def test_attach_picture_using_wrong_user(self):
        user = User.objects.create(username='user_name')
        collage = Collage.objects.create(name='name of collage', owner=user)
        picture = make_picture(owner=user)
        wrong_user = User.objects.create(username='wrong_user')

        url = reverse('collage-attach-picture', args=[collage.pk, picture.pk])
        self.client.force_authenticate(user=wrong_user)
        response = self.client.post(url)

        self.assertEqual(response.status_code, 403)
        self.assertEqual(collage.pictures.count(), 0)

    def test_attach_picture_while_not_owning_collage(self):
        user = User.objects.create(username='user')
        collage = Collage.objects.create(name='name of collage', owner=user)
        picture = make_picture()

        url = reverse('collage-attach-picture', args=[collage.pk, picture.pk])
        self.client.force_authenticate(user=picture.owner)
        response = self.client.post(url)

        self.assertEqual(response.status_code, 403)
        self.assertEqual(collage.pictures.count(), 0)

    def test_attach_picture_while_not_owning_picture(self):
        user = User.objects.create(username='user')
        collage = Collage.objects.create(name='name of collage', owner=user)
        picture = make_picture()

        url = reverse('collage-attach-picture', args=[collage.pk, picture.pk])
        self.client.force_authenticate(user=user)
        response = self.client.post(url)

        self.assertEqual(response.status_code, 403)
        self.assertEqual(collage.pictures.count(), 0)

    def test_list_pictures_to_detach(self):
        user = User.objects.create(username='user_name')
        collage = Collage.objects.create(name='name of collage', owner=user)
        picture1 = make_picture(owner=user)
        picture2 = make_picture(owner=user)
        picture3 = make_picture(owner=user)
        collage.pictures.add(picture1, picture3)
        another_user = User.objects.create(username='another_user')
        another_picture = make_picture(owner=another_user)

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
        picture = make_picture(owner=user)
        collage.pictures.add(picture)

        url = reverse('collage-detach-picture', args=[collage.pk, picture.pk])
        self.client.force_authenticate(user=user)
        response = self.client.post(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(collage.pictures.count(), 0)

    def test_detach_picture_with_no_auth(self):
        user = User.objects.create(username='user_name')
        collage = Collage.objects.create(name='name of collage', owner=user)
        picture = make_picture(owner=user)
        collage.pictures.add(picture)

        url = reverse('collage-detach-picture', args=[collage.pk, picture.pk])
        response = self.client.post(url)

        self.assertEqual(response.status_code, 403)
        self.assertEqual(collage.pictures.count(), 1)

    def test_detach_picture_using_wrong_user(self):
        user = User.objects.create(username='user_name')
        collage = Collage.objects.create(name='name of collage', owner=user)
        picture = make_picture(owner=user)
        collage.pictures.add(picture)
        wrong_user = User.objects.create(username='wrong_user')

        url = reverse('collage-detach-picture', args=[collage.pk, picture.pk])
        self.client.force_authenticate(user=wrong_user)
        response = self.client.post(url)

        self.assertEqual(response.status_code, 403)
        self.assertEqual(collage.pictures.count(), 1)

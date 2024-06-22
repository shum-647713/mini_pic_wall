from django.db import models
from django.urls import resolve
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.reverse import reverse
from rest_framework import test
from collages.models import Collage
from .models import Image, Picture
import PIL
import io


def make_image_bytes():
    image_bytes = io.BytesIO()
    image = PIL.Image.new('RGBA', size=(16, 16), color=(95, 0, 0))
    image.save(image_bytes, 'png')
    image_bytes.name = 'test.png'
    image_bytes.seek(0)
    return image_bytes

def make_picture(name='picture name', owner=None):
    if owner is None:
        owner = User.objects.create(username='user_name')

    image = SimpleUploadedFile(name='test_image.png', content=make_image_bytes().read(),
                               content_type='image/png')
    image = models.Manager.create(Image.objects, uploaded_image=image)

    return Picture.objects.create(name=name, image=image, owner=owner)


class PictureViewAPITestCase(test.APITestCase):
    def setUp(self):
        self.factory = test.APIRequestFactory()

    def test_list_pictures(self):
        user1 = User.objects.create(username='user_name_1')
        picture1 = make_picture('pic1', owner=user1)
        user2 = User.objects.create(username='user_name_2')
        picture2 = make_picture('pic2', owner=user2)

        url = reverse('picture-list')
        request = self.factory.get(url)
        response = resolve(url).func(request)

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

    def test_retrieve_picture(self):
        picture = make_picture()

        url = reverse('picture-detail', args=[picture.pk])
        request = self.factory.get(url)
        response = resolve(url).func(request, pk=picture.pk)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['name'], picture.name)
        self.assertEqual(response.data['image'],
                         request.build_absolute_uri(picture.image.uploaded_image.url))
        self.assertIn('thumbnail', response.data)
        self.assertEqual(response.data['collages'],
                         reverse('picture-collages', request=request, args=[picture.pk]))
        self.assertEqual(response.data['owner']['url'],
                         reverse('user-detail', request=request, args=[picture.owner.username]))
        self.assertEqual(response.data['owner']['username'], picture.owner.username)

    def test_list_picture_collages(self):
        picture = make_picture()
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

    def test_delete_picture(self):
        user = User.objects.create(username='user_name')
        picture = make_picture(owner=user)
        image = picture.image
        image.thumbnail.name = image.uploaded_image.name
        image.save()

        url = reverse('picture-detail', args=[picture.pk])
        self.client.force_authenticate(user=user)
        response = self.client.delete(url)

        self.assertEqual(response.status_code, 204)
        self.assertEqual(Picture.objects.count(), 0)

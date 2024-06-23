from django.contrib import auth
from django.db.models import Subquery
from pictures.models import Picture
from collages.models import Collage


class UserManager(auth.models.UserManager):
    def get_pictures_by_username(self, username):
        user = User.objects.filter(username=username)
        return Picture.objects.filter(owner=Subquery(user.values('pk')))

    def get_collages_by_username(self, username):
        user = User.objects.filter(username=username)
        return Collage.objects.filter(owner=Subquery(user.values('pk')))


class User(auth.models.User):
    objects = UserManager()

    class Meta:
        proxy = True
        ordering = ['pk']

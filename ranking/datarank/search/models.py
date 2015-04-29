from django.db import models
from django import forms
from django.forms.formsets import formset_factory
from django.contrib.auth.models import User

# Create your models here.
class Dataset(models.Model):
    ID = models.CharField(max_length=200)
    Count = models.IntegerField(default=0)
    Features = models.TextField(default="NOPE")
    Url = models.TextField(default="#")
    def __unicode__(self):              # __unicode__ on Python 2
        return self.ID

class SearchForm(forms.Form):
    search_words = forms.CharField(max_length=100)

class RankForm(forms.Form):
    rank_info = forms.CharField(widget=forms.Textarea)
    is_tmp = forms.BooleanField(required=False)

class MusicTrack(models.Model):
    name = models.TextField()
    release = models.IntegerField(default=0)
    tempo = models.FloatField(default=0)
    artist_name = models.TextField()
    track_id = models.CharField(max_length=200)
    duration = models.FloatField(default=0)

class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ('username', 'email', 'password')

class SearchRate(models.Model):
    username = models.CharField(max_length=200)
    keywords = models.TextField()
    ratings = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    sessioncreated = models.TextField(default="-1")

class RawComment(models.Model):
    user = models.CharField(max_length=200)
    dataset_id = models.CharField(max_length=200)
    keyword = models.TextField()
    comment = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

class CommentForm(forms.ModelForm):
    class Meta:
        model = RawComment
        fields = ('user', 'dataset_id', 'keyword', 'comment')


from django.db import models
from django.contrib.auth.models import User

# Create your models here.
#database in django is created as an python object
#each instaces of that object is our row
class Topic(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name

class Room(models.Model):
# class model_name(models.Model)
# on_delete is a parameter which is used to define what will happen to the foreign key when the parent object is deleted
    #on_delete=models.CASCADE will delete the child object when the parent object is deleted
    #on_delete=models.SET_NULL will set the foreign key to null when the parent object is deleted
    #on_delete=models.PROTECT will raise an error when the parent object is deleted
    #on_delete=models.SET_DEFAULT will set the foreign key to the default value when the parent object is deleted
    #on_delete=models.RESTRICT will restrict the deletion of the parent object if there are child objects
    #on_delete=models.DO_NOTHING will do nothing when the parent object is deleted
    
    host = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    topic = models.ForeignKey(Topic, on_delete=models.SET_NULL, null=True)
    #each of this represents a column with contrain
    name = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    participants = models.ManyToManyField(User, related_name='participants', blank=True)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-updated', '-created']

    def __str__(self):
        return self.name
    

class Message(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    #establish relationship with the parent table
    #if room deleted all massage will also be deleted
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    body = models.TextField()
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-updated', '-created']
    
    def __str__(self):
        return self.body[0:50]

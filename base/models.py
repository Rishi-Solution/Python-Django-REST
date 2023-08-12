from django.db import models
from django.contrib.auth.models import User

# Create your models here.

# a room is going to be a child of topic 
class Topic(models.Model):
    name=models.CharField(max_length=200)
    
    def __str__(self) -> str:
        return self.name

class Room(models.Model):
    # since one user can host multiple Room and when user is deleted it doesnot mean that room is also deleted but istead set to null via null=True
    host=models.ForeignKey(User,on_delete=models.SET_NULL,null=True)
    #Room is a child of Topic but same topic can have multiple room but room can have only one topic
    topic=models.ForeignKey(Topic,on_delete=models.SET_NULL,null=True)
    name=models.CharField(max_length=200)
    # null=True -- says that database can be submitted empty, blank=true --says that when form field can be saved null
    description=models.TextField(null=True,blank=True)
    updated=models.DateTimeField(auto_now=True)
    created=models.DateTimeField(auto_now_add=True)
    
    #since we already have a User below in host so to make a relationship again we need unique related_name specified
    participants=models.ManyToManyField(User,related_name='participants',blank=True) # we are making blank =True so that the already created table of room the new column of participants(instance of the room model can be blank) can be set to blank
    
    def __str__(self) -> str:
        return self.name
    class Meta:
        ordering=['-updated','-created']
    
    
    
#each room must have messages that room is one and messages can be many 
#so the relationship is one to many or many to one kind ---that is done 
#using foreignkey as shown below

class Message(models.Model):
    #we first need to specify User that is sending the message and that is done by using
    # django inbuild default User profile
    
    # a user can have many messages there for one to many relationship-foreignkey
    # when user is deleted all the messages should also be deleted therefore on_delete=models.SET_NULL
    #there can be many messages form single user therefore one to many relationship --foreignkey
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    # relationship -- one to many
    #below is the relationship between messages and Room and shows that messages in the child of Room 
    room=models.ForeignKey(Room,on_delete=models.CASCADE)
    body=models.TextField()
    updated=models.DateTimeField(auto_now=True)
    created=models.DateTimeField(auto_now_add=True)
    
    def __str__(self) -> str:
        return self.body[0:50]
    
    class Meta:
        ordering=['-updated','-created']
    
    
    
    
    
    
    
    
    
from django.shortcuts import render

from django.http import HttpResponse
from django.contrib.auth.models import User
from .models import Room,Topic,Message
from .forms import RoomForm
from django.http import HttpResponse
from django.shortcuts import redirect
from django.db.models import Q
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
# Create your views here.
'''
rooms=[
    {'id':1,'name':'start learning Python'},
     {'id':2,'name':'start learning Django'},
      {'id':3,'name':'start learning AWS'}
]
'''
def logoutUser(request):
    logout(request)
    return redirect('home')

def registerUser(request):
    #page='register'
    form=UserCreationForm()
    if request.method=='POST':
        # request.POST is used to get the information via post method similarly request.GET
        form=UserCreationForm(request.POST)
        if form.is_valid():
            user=form.save(commit=False)
            # commit=False is used to not instantaneously save the data into database but infact firstg do some modification before saving the data
            user.username=user.username.lower()
            user.save()
            login(request,user)
            return redirect('home')
        else:
            messages.error(request,'An error occcured during registration process')
    
    return render(request,'base/login_register.html',{'form':form})

def loginPage(request):
    page='login'
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method=="POST":
        username=request.POST.get('username').lower()
        password=request.POST.get('password')
        try:
            user=User.objects.get(username=username)
        except:
            messages.error(request, "User does't exists")
        
        user=authenticate(request,username=username,password=password)
        if user is not None:
            login(request,user)
            return redirect('home')
        else:
            messages.error(request, "Username or password doesnot exists")
    context={'page':page}
    return render(request,'base/login_register.html',context)

@login_required(login_url='login')
def updateRoom(request,pk):
    room1=Room.objects.get(id=pk)
     #if instance is passed in form initialization it will render with already filled information
    
    form=RoomForm(instance=room1)
    if request.user!=room1.host:
        return HttpResponse("You are not the owner of the room therefore you can't update")
    if request.method=='POST':
        form=RoomForm(request.POST,instance=room1)
        if form.is_valid():
            form.save()
            return redirect('home')
            
    context={"form":form}
    print(pk)
    return render(request,'base/room_form.html',context)

def home(request):
    #getting information from url(query string value=q?) by accessing request method
    q_para=request.GET.get('para') if request.GET.get('para')!=None else ''
    print(q_para)
    #---- Q look method is provided by django to filter or search based on different parameters and conditions as used below
    # modelname.modelmanager.function formmat is used to query database. model manager is objects
    rooms=Room.objects.filter(
        Q(topic__name__icontains=q_para) |
        Q(name__icontains=q_para) |
        Q(description__icontains=q_para)
        ) # __ is used when we have to travel upwards ie we are going form room model topic to Topic model and accessing name from there related to perticular topic
    #__icontains is used to get the matching parameters query and "" empty string matches with everything
    # one to many relationship because ak topic k kai room ho sakte hai.
    # so ham query kar rahe hai us topic se related kitane room hai
    room_count=rooms.count()
    topic=Topic.objects.all()
    recent_messages=Message.objects.filter(Q(room__topic__name__icontains=q_para))
    context={"rooms":rooms,'topics':topic,'room_count':room_count,
             "recent_messages":recent_messages} 
    return render(request,'base/home.html',context)


def room(request,pk):
# modelname.modelmanager.function formmat is used to query database. model manager is objects
    room=Room.objects.get(id=pk)
    context=None
   
    if request.method=='POST':
        new_message=Message.objects.create(
            user=request.user,
            room=room,
            body=request.POST.get("body"),            
        )
        room.participants.add(request.user)
        return redirect('room',pk=room.id)
        
     # we are below extracting/querying all the messages that are related to a room
    # and this done by accessing perticular model form room object(in this case Message model(.message_set--model name written in lower case) from from room) and calling .all to get all messages
    messages_room=room.message_set.all().order_by('-created')
    participants=room.participants.all()
    context={"room":room,'messages_room':messages_room,'participants':participants}
    return render(request,'base/room.html',context)        
    #return render(request,'base/room.html')

def userProfile(request,pk):
    user=User.objects.get(id=pk)
    #for accessing rooms attached to User
    rooms=user.room_set.all()
    # Get the Room instances where the user is the host same as above
    #rooms_hosted_by_user = Room.objects.filter(host=user)
    # Initialize a list to store topic names
    topic_names = []

    # Iterate through the Room instances and get the related topic names
    for room in rooms:
        if room.topic:
            topic_names.append(room.topic)
            
    recent_messages=user.message_set.all()
    print(topic_names,rooms)
    
    context={'user':user,'rooms':rooms,'topics':topic_names,
             'recent_messages':recent_messages}    
    return render(request,'base/profile.html',context)
#we use decorator to restrict what users can and can't see when they are not authenticateed or logged in
#and redirect to page if not logged in by specifying login_url='login'
@login_required(login_url='login')
def createRoom(request):
    form=RoomForm()
    #initialize the instance of the form needed to be created and render it out in the template 
    if request.method=="POST":
        print(request.POST)
        
        # in order to save the data entered in form, we need to initialize the form with incoming data
        # the initialized class will know which data is of which attribte inside the model
        # then after validating the form we just need to call the save on form
        form=RoomForm(request.POST)
        if form.is_valid():
            room=form.save(commit=False)
            room.host=request.user
            room.save()
            return redirect('home')
                
    context={"form":form}
    return render(request,'base/room_form.html',context)


    
    #room=Room.objects.get(id=pk)
    #if instance is passed in form initialization it will render with already filled information
    #form=RoomForm(instance=room)
    #context={"form":form}
    #render(request,'base/room_form.html',context)
@login_required(login_url='login')
def deleteRoom(request,pk):
    room=Room.objects.get(id=pk) 
    if request.user!=room.host:
       return HttpResponse("You are not the owner of the room therefore you can't update")
    
    if request.method=='POST':
        room.delete()
        return redirect('home')
    return render(request,'base/delete.html',{
        'obj':room
    })
    

@login_required(login_url='login')
def deleteMessage(request,pk):
    message=Message.objects.get(id=pk) 
    if request.user!=message.user:
       return HttpResponse("You are not the owner of the message therefore you can't update")
    
    if request.method=='POST':
        message.delete()
        return redirect('home')
    return render(request,'base/delete.html',{
        'obj':message
    })
from django.shortcuts import render, redirect
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from .models import Room, Topic, Message
from .forms import RoomForm, UserForm
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponse

def loginPage(request):
    page='login'

    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        #name attribute from html
        username = request.POST.get('username')
        password = request.POST.get('password')
    
    
        try:
            user = User.objects.get(username=username) 
        except:
            messages.error(request, 'User does not exists')
        
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Username or password does not exists')


    context={'page' : page}
    return render(request, 'base/login_register.html', context)

def logoutUser(request):
    logout(request)
    return redirect('login')

def registerPage(request):
    form = UserCreationForm()

    if request.method == 'POST':
        form = UserCreationForm(request.POST)

        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request, user)
            return redirect('home')
        else: 
            messages.error(request, 'An error occured during registrarion')

    return render(request, 'base/register.html', {'form' : form})

# Create your views here.
def home(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    # this will get all the rooms from the database and pass it to the template
    # this is a query set which is a list of objects of the model
    # ModelName.objects.all() will get all the objects of the model
    rooms = Room.objects.filter(Q(topic__name__icontains=q) |
        Q(host__username__icontains=q) |
        Q(name__icontains=q) |
        Q(description__icontains=q))
                                
    topics = Topic.objects.all()
    room_count = rooms.count()
    room_messages = Message.objects.filter(Q(room__topic__name__icontains=q))
    context = {'rooms': rooms, 'topics': topics, 'room_count':room_count, 'room_messages': room_messages}
    return render(request,'base/home.html', context)

def userProfile(request, pk):
    user = User.objects.get(id=pk)
    rooms = user.room_set.all()
    room_messages = user.message_set.all()
    topics = Topic.objects.all()
    context = {'user': user, 'room_messages': room_messages, 'topics': topics, 'rooms': rooms}
    return render(request, 'base/profile.html', context)

def room(request, pk):
    # this will get the room with the given id from the database and pass it to the template
    room = Room.objects.get(id=pk)
    # comments = room.message_set.all()
    room_messages = Message.objects.filter(room_id = pk).order_by('-created')
    participants = room.participants.all()
    context = {'room': room, 'room_messages': room_messages, 'participants': participants}

    if request.method == 'POST':
        message = Message.objects.create(
            user=request.user,
            room=room,
            body=request.POST.get('body')
        )
        room.participants.add(request.user)
        return redirect('room', pk=room.id)

    return render(request,'base/room.html', context)

@login_required(login_url='login')
def createRoom(request):
    form = RoomForm()
    topics = Topic.objects.all()
    
    if request.method == "POST":
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)

        Room.objects.create(
            host=request.user,
            topic=topic,
            name=request.POST.get('name'),
            description=request.POST.get('description'),
        )

        return redirect('home')
        
    context = {'form': form, 'topics': topics}
    return render(request, 'base/room_form.html', context)

@login_required(login_url='login')
def updateRoom(request, pk):
    #get specific room with following id
    room = Room.objects.get(id=pk)
    #populate form with room instance value
    form = RoomForm(instance=room)
    #grab all topic from Topic model
    topics = Topic.objects.all()

    #only person hosted the room can delete/update the room
    if request.user != room.host:
        return HttpResponse('You are not allowed here!!')
    
    #check method in order to create or update
    if request.method == "POST":
        #don't accully know what does following do
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        room.name = request.POST.get('name')
        room.topic = topic
        room.description = request.POST.get('description')
        room.save()
        return redirect('home')

    context = {'form' : form, 'topics': topics}
    return render(request, 'base/room_form.html', context)
    
def deleteRoom(request, pk):
    room = Room.objects.get(id=pk)

    if request.user != room.host:
        return HttpResponse('You are not allowed here!!')

    if request.method == "POST":
        room.delete()
        return redirect('home')
    context = {'obj' : room.name}
    return render(request, 'base/delete.html', context)

@login_required(login_url='login')
def deleteMessage(request, pk):
    message = Message.objects.get(id=pk)

    if request.user != message.user:
        return HttpResponse('You are not allowed here!!')

    if request.method == "POST":
        message.delete()
        return redirect('room', pk=message.room.id)
    return render(request, 'base/delete.html', {'obj': message})


@login_required(login_url ='login')
def updateUser(request):
    #get information about the logged in user
    user = request.user

    #we can pass any model form in a context, render out in template and modify if required
    #instance populate the form with the value we are instantiating with
    form = UserForm(instance=user)

    if request.method == 'POST':
        form = UserForm(request.POST, instance=user)
    # validate form before saving
        if form.is_valid():
            form.save()
            return redirect('profile', pk=user.id)

    return render(request, 'base/update_user.html', {'form': form})

def topics(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    topics = Topic.objects.filter(name__icontains = q)
    context = {'topics' : topics}
    return render(request,'base/topics.html', context)



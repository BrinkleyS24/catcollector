from django.shortcuts import render, redirect
from main_app.forms import FeedingForm
from .models import Cat, Toy, Photo
from django.views.generic.edit import CreateView, UpdateView, DeleteView
import uuid
import boto3
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin

S3_BASE_URL = 'https://s3-us-east-2.amazonaws.com/'
BUCKET = 'my-catcollector-bucket'

def signup(request):
  error_message = ''
  if request.method == 'POST':
    # This is how to create a 'user' form object
    # that includes the data from the browser
    form = UserCreationForm(request.POST)
    if form.is_valid():
      # This will add the user to the database
      user = form.save()
      # This is how we log a user in via code
      login(request, user)
      return redirect('index')
    else:
      error_message = 'Invalid sign up - try again'
  # A bad POST or a GET request, so render signup.html with an empty form
  form = UserCreationForm()
  context = {'form': form, 'error_message': error_message}
  return render(request, 'registration/signup.html', context)


# Create your views here.
def home(request):
    return render(request, 'home.html')

def about(request):
    return render(request, 'about.html')


# Cats
@login_required
def cats_index(request):
    cats = Cat.objects.filter(user=request.user)
    return render(request, 'cats/index.html', { 'cats': cats })

@login_required
def cats_detail(request, cat_id):
  cat = Cat.objects.get(id=cat_id)
  if cat.user_id != request.user.id:
      return redirect('home')
  toys_cat_doesnt_have = Toy.objects.exclude(id__in = cat.toys.all().values_list('id'))
  feeding_form = FeedingForm()
  return render(request, 'cats/detail.html', { 'cat': cat, 'feeding_form': feeding_form, 'toys': toys_cat_doesnt_have })

@login_required
def add_feeding(request, cat_id):
  # create the ModelForm using the data in request.POST
  form = FeedingForm(request.POST)
  # validate the form
  if form.is_valid():
    # don't save the form to the db until it
    # has the cat_id assigned
    new_feeding = form.save(commit=False)
    new_feeding.cat_id = cat_id
    new_feeding.save()
  return redirect('detail', cat_id=cat_id)

@login_required
def assoc_toy(request, cat_id, toy_id):
    Cat.objects.get(id=cat_id).toys.add(toy_id)
    return redirect('detail', cat_id=cat_id)

@login_required
def unassoc_toy(request, cat_id, toy_id):
    Cat.objects.get(id=cat_id).toys.remove(toy_id)
    return redirect('detail', cat_id=cat_id)

class CatCreate(LoginRequiredMixin, CreateView):
    model = Cat
    fields = ('name', 'age', 'breed', 'description')
    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

class CatUpdate(LoginRequiredMixin, UpdateView):
    model = Cat
    fields = ('breed', 'description', 'age')
    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.user != self.request.user:
            return redirect('index')
        return super(CatUpdate, self).dispatch(request, *args, **kwargs)


class CatDelete(LoginRequiredMixin, DeleteView):
    model = Cat
    success_url = '/cats/'
    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.user != self.request.user:
            return redirect('index')
        return super(CatDelete, self).dispatch(request, *args, **kwargs)

#Photo
@login_required
def add_photo(request, cat_id):
    # collect the file asset from the request
    photo_file = request.FILES.get('photo-file', None)
    # check if file is present
    if photo_file:
        # create a reference to the s3 service from boto3
        s3 = boto3.client('s3')
        # create a unique identifier for each photo asset
        key = uuid.uuid4().hex[:6] + photo_file.name[photo_file.name.rfind('.'):]
        # cute_cat.png => 3g3egg.png
        try:
            # attempt to upload image to aws
            s3.upload_fileobj(photo_file, BUCKET, key)
            # dynamically generate photo url
            url = f"{S3_BASE_URL}{BUCKET}/{key}"
            # create an in-memory reference to a photo model instance
            photo = Photo(url=url, cat_id=cat_id)
            # save the instance to the database
            photo.save()

        except Exception as error:
            print('*****************')
            print('An error has occurred with s3:')
            print(error)
            print('*****************')
    
    return redirect('detail', cat_id=cat_id)

# Toys

def toys_index(request):
    toys = Toy.objects.all()
    return render(request, 'toys/index.html', { 'toys': toys })

def toys_detail(request, toy_id):
  toy = Toy.objects.get(id=toy_id)
  return render(request, 'toys/detail.html', { 'toy': toy })

class ToyCreate(LoginRequiredMixin, CreateView):
    model = Toy
    fields = '__all__'
    # success_url = '/toys/' redirects to 'view all my toys' page

class ToyUpdate(LoginRequiredMixin, UpdateView):
    model = Toy
    fields = ['color']


class ToyDelete(LoginRequiredMixin, DeleteView):
    model = Toy
    success_url = '/toys/'
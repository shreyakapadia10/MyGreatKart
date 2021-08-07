from .models import Category

# Getting all categories list and converting them into dictinary so that we can access it via loop in home page that is index.html in All Category dropdown function. Also it can be used in store.html and everywhere 
def get_categories(request):
    categories = Category.objects.all()
    return dict(categories=categories)
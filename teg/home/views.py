
from django.dispatch import receiver
from django.shortcuts import render,redirect
from django.test import TransactionTestCase

from .models import Article, Category, Favorit, Panier, ArticleInPanier,Command
from django.contrib.auth.decorators import login_required
from django.views.generic import FormView, TemplateView
from django.urls import reverse
from paypal.standard.forms import PayPalPaymentsForm
from paypal.standard.models import ST_PP_COMPLETED
from paypal.standard.ipn.signals import valid_ipn_received
#import numpy as np

# Create your views here.

def home(request):
    all_articles = Article.objects.all()
    all_categories = Category.objects.all()
    my_panier=''
    my_favorit=''
    my_articles_in_panier=[0]
    if request.user.is_authenticated :
        my_panier = Panier.objects.get(user=request.user)
        my_articles_in_panier = ArticleInPanier.objects.filter(panier=my_panier)
        my_favorit = Favorit.objects.get(user=request.user)

    context = {
        'panier' : my_articles_in_panier,
        'articles': all_articles,
        'categories': all_categories,
        'favorit': my_favorit
    }
    return render(request, 'home.html', context)

def category(request, category_id):
    this_category = Category.objects.get(id=category_id)
    articles_in_category = Article.objects.filter(category=this_category)
    my_panier = Panier.objects.get(user=request.user)
    my_favorit = Favorit.objects.get(user=request.user)
    all_categories = Category.objects.all()
    my_articles_in_panier = ArticleInPanier.objects.filter(panier=my_panier)
    
    #print(this_category.c_name)
    context = {
        'this_category' : this_category,
        'articles' : articles_in_category,
        'panier' : my_articles_in_panier,
        'categories': all_categories,
        'favorit': my_favorit
    }
    return render(request, 'category.html', context)

def details(request, article_id):
    this_article = Article.objects.get(id=article_id)
    all_categories = Category.objects.all()
    my_panier=''
    my_favorit=''
    if request.user.is_authenticated :
        my_panier = Panier.objects.get(user=request.user)
        my_favorit = Favorit.objects.get(user=request.user)
        my_articles_in_panier = ArticleInPanier.objects.filter(panier=my_panier)

    context = {
        'article' : this_article,
        'panier' : my_articles_in_panier,
        'favorit': my_favorit,
        'categories': all_categories
        
    }
    return render(request, 'details.html', context)

@login_required
def add_panier(request, article_id):
    selected_article = Article.objects.get(id=article_id)
    if request.method == 'POST':
        taille = request.POST.get('taille')
        test = Panier.objects.get(user=request.user)
        quantity = request.POST.get('quantity')
        if test:
            x = ArticleInPanier.objects.create(article=selected_article, panier=test, taille=taille, quantity=quantity)
        else:
            new_inpanier = Panier.objects.create(user=request.user)
            x = ArticleInPanier.objects.create(article=selected_article, panier=new_inpanier, taille=taille, quantity=quantity)
        return redirect('home')

def delete(request, article_id):
    selected_article = Article.objects.get(id=article_id)
    my_panier = Panier.objects.get(user=request.user)
    article_in_paniertodelete = ArticleInPanier.objects.filter(panier=my_panier, article=selected_article).first()
    print(article_in_paniertodelete)
    article_in_paniertodelete.delete()
    return redirect('voir_panier')

@login_required
def panier(request):
    my_panier = Panier.objects.get(user=request.user)
    my_articles_in_panier = ArticleInPanier.objects.filter(panier=my_panier)
    my_favorit = Favorit.objects.get(user=request.user)

    total_price = 0
    #articleInPanier[0].prix + articleInPanier[1].prix
    for object in my_articles_in_panier:
        total_price += (object.article.prix * object.quantity)
        
        
    context = {
        'panier' : my_articles_in_panier,
        'total_price' : total_price,
        'favorit': my_favorit,
    }
    return render(request, 'panier.html', context)

@login_required
def add_favorite(request, article_id):
    selected_article = Article.objects.get(id=article_id)
    test=''
    try:
        test = Favorit.objects.get(user=request.user)
    except:
        print("Favorit matching query does not exist.")
    if test:
        test.article.add(selected_article)
        test.save()
    else:
        new_infavorit = Favorit.objects.create(user=request.user)
        new_infavorit.article.add(selected_article)
        new_infavorit.save()
    return redirect('home')

@login_required
def favorit(request):
    my_favorit = Favorit.objects.get(user=request.user)

    context = {
        'favorit' : my_favorit 
    }

    return render(request, 'favorit.html', context)

def about(request):
    return render(request, 'about.html')


def command(request, payement):
    my_panier = Panier.objects.get(user=request.user)
    my_articles_in_panier = ArticleInPanier.objects.filter(panier=my_panier)
    my_favorit = Favorit.objects.get(user=request.user)

    total_price = 0
    #articleInPanier[0].prix + articleInPanier[1].prix
    for object in my_articles_in_panier:
        total_price += (object.article.prix * object.quantity)
        
    x= Command.objects.create(type_of_payement=payement, price=total_price,panier=my_panier)
    my_articles_in_panier.delete()
    return render(request, 'command.html')

class PaypalFormView(FormView):
    template_name = 'paypal_form.html'
    form_class = PayPalPaymentsForm

    def get_initial(self):
        my_articles_in_panier = ArticleInPanier.objects.filter(panier=Panier.objects.get(user=self.request.user))

        total_price = 0
        articles=[]
        #articleInPanier[0].prix + articleInPanier[1].prix
        for object in my_articles_in_panier:
            articles.append(object.article.name)
            total_price += (object.article.prix * object.quantity)

        return {
            "business": 'your-paypal-business-address@example.com',
            "amount": total_price ,
            "currency_code": "XAF",
            "item_name": articles,
            "invoice": 1234,
            "notify_url": self.request.build_absolute_uri(reverse('paypal-ipn')),
            "return_url": self.request.build_absolute_uri(reverse('paypal-return')),
            "cancel_return": self.request.build_absolute_uri(reverse('paypal-cancel')),
            "lc": 'EN',
            "no_shipping": '1',
        }
    def get_context_data(self, **kwargs):
        my_articles_in_panier = ArticleInPanier.objects.filter(panier=Panier.objects.get(user=self.request.user))

        total_price = 0
        #articleInPanier[0].prix + articleInPanier[1].prix
        for object in my_articles_in_panier:
            total_price += (object.article.prix * object.quantity)
        
        context = super().get_context_data(**kwargs)
        context['panier']=  my_articles_in_panier
        context['total_price']= total_price
        context['favorit']= Favorit.objects.get(user=self.request.user)
        
        return super().get_context_data(**kwargs)  
    
  
    

class PaypalReturnView(TemplateView):
    template_name = 'paypal_success.html'

class PaypalCancelView(TemplateView):
    template_name = 'paypal_cancel.html'

@receiver(valid_ipn_received)
def paypal_payment_received(sender, **kwargs):
    ipn_obj = sender
    if ipn_obj.payment_status == ST_PP_COMPLETED:
        if ipn_obj.receiver_email != 'your-paypal-business-address@example.com':
            return
        
        try:
            assert ipn_obj.mc_gross == mytransaction.amount and ipn_obj.mc_currency == 'EUR'
        except Exception:
            Logger.exception('Paypal ipn_obj data not valid!')
        else:
            TransactionTestCase.paid = True
            mytransaction.save()
    else:
        logger.debug('Paypal payment status not completed: %s' % ipn_obj.payment_status)
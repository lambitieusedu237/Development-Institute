from asyncio.log import logger
from logging import Logger
from django.dispatch import receiver
from django.shortcuts import render,redirect
from django.test import TransactionTestCase

from .models import Article, Category, Favorit, Panier
from django.contrib.auth.decorators import login_required
from django.views.generic import FormView, View
from django.urls import reverse
from paypal.standard.forms import PayPalPaymentsForm
from django.views.generic import TemplateView
from paypal.standard.models import ST_PP_COMPLETED
from paypal.standard.ipn.signals import valid_ipn_received

# Create your views here.

def home(request):
    all_articles = Article.objects.all()
    all_categories = Category.objects.all()
    my_panier=''
    my_favorit=''
    if request.user.is_authenticated :
        my_panier = Panier.objects.get(user=request.user)
        my_favorit = Favorit.objects.get(user=request.user)

    context = {
        'panier' : my_panier,
        'articles': all_articles,
        'categories': all_categories,
        'favorit': my_favorit
    }
    return render(request, 'home.html', context)

def category(request, category_id):
    this_category = Category.objects.get(id=category_id)
    articles_in_category = Article.objects.filter(category=this_category)
    #print(this_category.c_name)
    context = {
        'this_category' : this_category,
        'articles' : articles_in_category,
    }
    return render(request, 'category.html', context)

def details(request, article_id):
    this_article = Article.objects.get(id=article_id)
    my_panier=''
    my_favorit=''
    if request.user.is_authenticated :
        my_panier = Panier.objects.get(user=request.user)
        my_favorit = Favorit.objects.get(user=request.user)

    context = {
        'article' : this_article,
        'panier' : my_panier,
        'favorit': my_favorit
        
    }
    return render(request, 'details.html', context)

@login_required
def add_panier(request, article_id):
    selected_article = Article.objects.get(id=article_id)
    test = Panier.objects.get(user=request.user)
    if test:
        test.article.add(selected_article)
        test.save()
    else:
        new_inpanier = Panier.objects.create(user=request.user)
        new_inpanier.article.add(selected_article)
        new_inpanier.save()
    return redirect('home')

def delete(request, article_id):
    selected_article = Article.objects.get(id=article_id)
    test = Panier.objects.get(user=request.user)
    test.article.remove(selected_article)
    return redirect('voir_panier')

@login_required
def panier(request):
    my_panier = Panier.objects.get(user=request.user)
    articleInPanier = my_panier.article.all()
    my_favorit = Favorit.objects.get(user=request.user)
    total_price = 0
    #articleInPanier[0].prix + articleInPanier[1].prix
    for article in articleInPanier:
        total_price += article.prix
    form_class = PayPalPaymentsForm

    def get_initial():
        return {
            "business": 'your-paypal-business-address@example.com',
            "amount": total_price,
            "currency_code": "USD",
            "item_name": articleInPanier,
            "invoice": 1234,
            "notify_url": request.build_absolute_uri(reverse('paypal-ipn')),
            "return_url": request.build_absolute_uri(reverse('paypal-return')),
            "cancel_return": request.build_absolute_uri(reverse('paypal-cancel')),
            "lc": 'EN',
            "no_shipping": '1',
        }
    if request.method == 'POST':
        get_initial()
        
    context = {
        'panier' : my_panier,
        'total_price' : total_price,
        'favorit': my_favorit,
        'form':form_class
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


def command(request):
    return render(request, 'command.html')

'''class PaypalFormView(FormView):
    template_name = 'paypal_form.html'
    form_class = PayPalPaymentsForm

    def get_initial(self):
        return {
            "business": 'your-paypal-business-address@example.com',
            "amount": 20,
            "currency_code": "EUR",
            "item_name": 'Example item',
            "invoice": 1234,
            "notify_url": self.request.build_absolute_uri(reverse('paypal-ipn')),
            "return_url": self.request.build_absolute_uri(reverse('paypal-return')),
            "cancel_return": self.request.build_absolute_uri(reverse('paypal-cancel')),
            "lc": 'EN',
            "no_shipping": '1',
        }
'''
class PanierView(GenericView):
    template_name = 'panier.html'
    form_class = PayPalPaymentsForm

    def get_context_data(self, **kwargs):
        total_price = 0
        #articleInPanier[0].prix + articleInPanier[1].prix
        my_panier= Panier.objects.get(user=self.request.user)
        articleInPanier = my_panier.article.all()

        for article in articleInPanier:
            total_price += article.prix
        context = super().get_context_data(**kwargs)
        context['panier']=  Panier.objects.get(user=self.request.user)
        context['total_price']= total_price
        context['articles']= articleInPanier,
        context['favorit']= Favorit.objects.get(user=self.request.user)
        context['form']=PayPalPaymentsForm
        
        return super().get_context_data(**kwargs)    
    
    def get_initial(self):
        context = super().get_context_data()
        return {
            "business": 'your-paypal-business-address@example.com',
            "amount": context['total_price'],
            "currency_code": "USD",
            "item_name": context['articles'],
            "invoice": 1234,
            "notify_url": self.request.build_absolute_uri(reverse('paypal-ipn')),
            "return_url": self.request.build_absolute_uri(reverse('paypal-return')),
            "cancel_return": self.request.build_absolute_uri(reverse('paypal-cancel')),
            "lc": 'EN',
            "no_shipping": '1',
        }
    

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
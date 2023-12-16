from datetime import datetime
from django.http import request
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views.generic import DetailView, FormView, ListView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Receipt
from .forms import ReceiptForm
from django.db.models import Sum, Value, DecimalField, Q
from django.db.models.functions import Coalesce
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_GET
from django.http import JsonResponse
from django.utils import timezone
@require_GET
@login_required
#get the names of all the stores from the available user receipts
def get_store_names(request):
    user = request.user
    names = user.receipts.values_list('store_name', flat=True)
    return JsonResponse(list(names), safe=False)

#handling listing the user's receipts 
class ReceiptListView(LoginRequiredMixin, ListView):
    model = Receipt
    template_name = "user_receipts.html"
    context_object_name = "receipts"
    paginate_by = 10

    def get_queryset(self):
        request_data = self.request.GET
        #filters to be used in the query
        filters = Q(user=self.request.user)
        #search by a specific store name
        store_name = request_data.get('store_name', None)
        if store_name:
            filters.add(Q(store_name=store_name), Q.AND)
        #to find specific receipts that fall within this range(start_date, end_date)
        start_date = timezone.make_aware(datetime.combine(request_data.get('min_date', datetime.min.date()), datetime.min.time()))
        end_date = timezone.make_aware(datetime.combine(request_data.get('max_date', datetime.now().date()), datetime.max.time()))
        filters.add(Q(purchase_date__range=(start_date, end_date)), Q.AND)
        receipts = Receipt.objects.filter(filters).order_by('-purchase_date')

        return receipts

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        #get the total ammount of money of all the displayed receipts
        total_ammount = context['receipts'].aggregate(
            total=Coalesce(Sum('total_ammount'), Value(0), output_field = DecimalField())
        )['total']
        context['total_ammount'] = total_ammount
        paginator = Paginator(context['receipts'], self.paginate_by)
        page = self.request.GET.get("page", '1')
        try:
            receipts_page = paginator.page(page)
        except PageNotAnInteger:
            receipts_page = paginator.page(1)
        except EmptyPage:
            receipts_page = paginator.page(paginator.num_pages)
        context['receipts'] = receipts_page
        return context

#handling viewing the details of a specifi user's receipt
class ReceiptDetailView(LoginRequiredMixin, DetailView):
    model = Receipt
    template_name = "receipt_details.html"
    context_object_name = "receipt"


    def get_object(self, queryset=None):
        receipt_id = self.kwargs.get("receipt_id")
        receipt = get_object_or_404(Receipt, pk=receipt_id, user=self.request.user)
        return receipt

#handling receipt creation and editing as well as form rendering 
class ReceiptFormView(LoginRequiredMixin,FormView):
    form_class = ReceiptForm
    template_name = "receipt_form.html"


    def get_form_kwargs(self): 
        kwargs = super().get_form_kwargs()
        receipt_id = self.kwargs.get('receipt_id', None)
        #in the case of editing an existing receipt
        if receipt_id:
            receipt = get_object_or_404(Receipt, pk=receipt_id)
            #initiate the form with the specified receipt
            kwargs['instance'] = receipt
        return kwargs


    def form_valid(self, form):
        receipt_id = self.kwargs.get('receipt_id', None)
        receipt = receipt_id
        #if it's an editing process, get the target receipt
        if receipt_id:
            receipt = get_object_or_404(Receipt, pk=receipt_id, user=self.request.user)
        form = ReceiptForm(instance=receipt, data=self.request.POST)
        user = self.request.user
        form.instance.user = user
        #update the receipt object if it's editing process otherwise create the new receipt
        receipt = form.save() 
        #redirect the user to the details page of this receipt
        receipt_url = reverse_lazy("receipt_details", kwargs={"receipt_id":receipt.pk})
        return redirect(receipt_url)


@login_required
#delete a specific user's receipt
def delete_receipt(request, receipt_id):
    user = request.user
    receipt = get_object_or_404(Receipt, pk=receipt_id, user=user)
    print(receipt)
    receipt.delete()
    return redirect('user_receipts')



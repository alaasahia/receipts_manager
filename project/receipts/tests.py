from django.db import IntegrityError
from django.http import response
from django.shortcuts import reverse
from django.test import TestCase
from django.contrib.auth.models import User
from .models import Receipt
from copy import deepcopy
#test data to create a test receipt object
test_receipt = {
    'store_name': 'test_store',
    'items': 'item1, item2, item3',
    'purchase_date': '2023-12-13 16:36:29',
    'total_ammount': '50.00'
}



#a common basecase to initiate common attributes for all the test cases
class BaseTestCase(TestCase):
    def setUp(self) -> None:
        self.username = 'testuser'
        self.password = 'testpass'
        self.user = User.objects.create_user(username=self.username, password=self.password)

#tests for the receipt model
class ReceiptModelTestCase(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.receipt = Receipt.objects.create(**test_receipt, user=self.user)

    def test_receipt_creation(self):
        receipt = Receipt.objects.latest('id')
        self.assertEqual(self.receipt.id, receipt.id)
        self.assertEqual(self.receipt.user, self.user)


    def test_receipt_constraints(self):
        #create a copy of the receipt
        second_receipt = deepcopy(self.receipt)
        second_receipt.pk=None
        #Check for a unique constraint violation when creating a similar object 
        #with the same user, store_name, and purchase_date."""
        with self.assertRaises(IntegrityError):
            second_receipt.save()
        


class ReceiptCreateViewTest(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.view_url = reverse('create_receipt')

    def test_receipt_form_view_submission(self):
        self.client.login(username=self.username, password=self.password)
        response = self.client.post(
            self.view_url,
            data = test_receipt
        )
        #get the receipt object that has been created
        receipt = Receipt.objects.latest('id')
        #check if the user is redirected to the details page of the receipt successfully 
        self.assertRedirects(response, reverse('receipt_details', kwargs={'receipt_id': receipt.id}))

    #test if the view won't allow anauthenticated users to access it
    def test_view_authentication(self):
        self.client.logout()
        response = self.client.post(self.view_url,data=test_receipt)
        expected_url = reverse('login') + f'?next={reverse("create_receipt")}'
        #check if the anauthorized access is redirected to the login page
        self.assertRedirects(response, expected_url, status_code=302)


        

class TestReceiptListView(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.view_url = reverse('user_receipts')

    def test_list_view_success(self):
        self.client.login(username=self.username, password=self.password)
        response = self.client.get(self.view_url)
        self.assertEqual(response.status_code, 200)

    #test if the view won't allow anonymouse users to access it
    def test_view_authentication(self):
        self.client.logout()
        response = self.client.get(self.view_url)
        #check if the anauthenticated user is redirected to login page
        expected_url = reverse('login') + f'?next={reverse("user_receipts")}'
        self.assertRedirects(response, expected_url, status_code=302)





class TestReceiptDetailView(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.test_receipt = Receipt.objects.create(**test_receipt, user=self.user)
        self.view_url = reverse('receipt_details', kwargs={'receipt_id': self.test_receipt.id})

    #check if the view succeed in providing the details
    def test_receipt_details_success(self):
        self.client.login(username=self.username, password=self.password)
        response = self.client.get(self.view_url)
        self.assertEqual(response.status_code, 200)
    

    #test if the view won't allow anonymouse users to access it
    def test_view_authentication(self):
        self.client.logout()
        response = self.client.get(self.view_url)

    #test if the view won't allow the anauthorized user to access it
    def test_view_authorization(self):
        test_user = User.objects.create_user(username='fake', password='fake')
        self.client.login(username=test_user.username, password=test_user.password)
        response = self.client.get(self.view_url)
        #check if the user is redirected to 404 page
        self.assertEqual(response.status_code, 302)


class DeleteViewTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.receipt = Receipt.objects.create(**test_receipt, user=self.user)
        self.view_url = reverse('delete_receipt', kwargs={'receipt_id':self.receipt.id})

    #test the successfull deletion of a receipt
    def test_receipt_deletion(self):
        response = self.client.get(self.view_url, follow=True)
        self.assertEqual(response.status_code, 200)

    #test if the view won't allow unauthenticated user to access it
    def test_view_authentication(self):
        self.client.logout()
        response = self.client.get(self.view_url)
        self.assertEqual(response.status_code, 302)

    #test if the view won't allow anauthorized to access it
    def test_view_authorization(self):
        username = 'fakeuser'
        password = 'pass'
        test_user = User.objects.create_user(username, password)
        #login using the test user
        self.client.login(username=username, password=password)
        response = self.client.get(self.view_url)
        #test if the receipt didn't get deleted
        receipt = Receipt.objects.filter(pk=self.receipt.pk)[0]
        self.assertEqual(receipt.pk, self.receipt.pk)


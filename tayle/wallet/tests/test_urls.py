from django.test import TestCase, Client
from http import HTTPStatus

from ..models import Transfer, User, Wallet


class WalletUrlTest(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.src_user = User.objects.create_user(username='src_user')
        cls.dst_user = User.objects.create_user(username='dst_user')
        cls.src_wallet = Wallet.objects.create(
            balance=50.0,
            user=cls.src_user,
            name='src_test_wallet'
        )
        cls.dst_wallet = Wallet.objects.create(
            balance=50.0,
            user=cls.dst_user,
            name='dst_test_wallet'
        )
        cls.transfer = Transfer(
            user=cls.src_user,
            dst_wallet=cls.dst_wallet,
            score=30
        )
        cls.transfer.save()
        cls.transfer.src_wallet.add(cls.src_wallet)
        cls.public_urls = {
            '/': 'wallet/index.html',
            f'/transfer/{cls.transfer.pk}/detail': 'wallet/transfer_detail.html'
        }
        cls.private_urls = {
            '/transfer': 'wallet/transfer.html',
            '/transfer-list': 'wallet/transfer_list.html'
        }

    def setUp(self) -> None:
        self.guest_client = Client()
        self.auth_client = Client()
        self.auth_client.force_login(WalletUrlTest.src_user)

    def test_public_urls(self):
        for url in WalletUrlTest.public_urls.keys():
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_private_for_auth_urls(self):
        for url in WalletUrlTest.private_urls.keys():
            with self.subTest(url=url):
                response = self.auth_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_private_for_guest_urls(self):
        for url in WalletUrlTest.private_urls.keys():
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_templates_public_urls(self):
        for url, template in WalletUrlTest.public_urls.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertTemplateUsed(response, template)

    def test_templates_private_urls(self):
        for url, template in WalletUrlTest.private_urls.items():
            with self.subTest(url=url):
                response = self.auth_client.get(url)
                self.assertTemplateUsed(response, template)

    def test_not_found_url(self):
        url = '/unexpected-url'
        response = self.auth_client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)


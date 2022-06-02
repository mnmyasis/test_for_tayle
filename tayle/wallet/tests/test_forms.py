from django.test import TestCase, Client
from django.urls import reverse
from http import HTTPStatus

from ..models import User, Wallet, Transfer


class WalletFormsTest(TestCase):
    WALLET_BALANCE = 50.0
    EXPECTED_COUNT_TRANSFER = 1
    TRANSFER_SCORE = 10.0
    EXPECTED_SCORE_FOR_ONE_WALLET = 40.0
    EXPECTED_SCORE_FOR_TWO_WALLET = 45.0

    SRC_WALLET_NAME_1 = 'src_test_wallet1'
    SRC_WALLET_NAME_2 = 'src_test_wallet2'
    DST_WALLET_NAME = 'dst_test_wallet'

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.src_user = User.objects.create_user(username='src_user')
        cls.dst_user = User.objects.create_user(username='dst_user')

    def setUp(self) -> None:
        self.auth_client = Client()
        self.auth_client.force_login(WalletFormsTest.src_user)
        self.src_wallet_1 = Wallet.objects.create(
            balance=self.WALLET_BALANCE,
            user=self.src_user,
            name=self.SRC_WALLET_NAME_1
        )
        self.src_wallet_2 = Wallet.objects.create(
            balance=self.WALLET_BALANCE,
            user=self.src_user,
            name=self.SRC_WALLET_NAME_2
        )
        self.dst_wallet = Wallet.objects.create(
            balance=self.WALLET_BALANCE,
            user=self.dst_user,
            name=self.DST_WALLET_NAME
        )

    def test_create_transfer(self):
        data = {
            'src_wallet': [self.src_wallet_1.pk],
            'dst_wallet': self.dst_wallet.pk,
            'score': self.TRANSFER_SCORE,
        }
        response = self.auth_client.post(
            reverse('wallet:transfer'),
            data=data
        )
        transfer_count = Transfer.objects.count()
        self.assertEqual(transfer_count,
                         self.EXPECTED_COUNT_TRANSFER,
                         msg='Не создался перевод')
        self.assertEqual(response.status_code,
                         HTTPStatus.FOUND,
                         msg=f'После перевода ожидается редирект '
                             f'{response.status_code} != 302')

    def test_debit_from_two_wallets(self):
        data = {
            'src_wallet': [self.src_wallet_1.pk,
                           self.src_wallet_2.pk],
            'dst_wallet': self.dst_wallet.pk,
            'score': self.TRANSFER_SCORE,
        }
        self.auth_client.post(
            reverse('wallet:transfer'),
            data=data
        )
        wallets = Wallet.objects.filter(user=self.src_user)
        for wallet in wallets:
            with self.subTest(wallet_name=wallet.name):
                self.assertEqual(wallet.balance,
                                 self.EXPECTED_SCORE_FOR_TWO_WALLET,
                                 msg=('Некорретно проходит списание с '
                                      'нескольких кошельков'))

    def test_debit_from_one_wallet(self):
        data = {
            'src_wallet': [self.src_wallet_1.pk],
            'dst_wallet': self.dst_wallet.pk,
            'score': self.TRANSFER_SCORE,
        }
        self.auth_client.post(
            reverse('wallet:transfer'),
            data=data
        )
        wallet_balance = Wallet.objects.get(
            name=self.SRC_WALLET_NAME_1).balance
        self.assertEqual(wallet_balance,
                         self.EXPECTED_SCORE_FOR_ONE_WALLET,
                         msg=('Некорретно проходит списание с одного '
                              'кошелька'))

    def test_accrual_on_wallet(self):
        data = {
            'src_wallet': [self.src_wallet_1.pk],
            'dst_wallet': self.dst_wallet.pk,
            'score': self.TRANSFER_SCORE,
        }
        self.auth_client.post(
            reverse('wallet:transfer'),
            data=data
        )
        wallet_balance = Wallet.objects.get(name=self.DST_WALLET_NAME).balance
        expected_balance = self.WALLET_BALANCE + self.TRANSFER_SCORE
        self.assertEqual(wallet_balance,
                         expected_balance,
                         msg='Некорректно начисляются средства при переводе '
                             'с одного кошелька')

    def test_accrual_on_wallet_from_two_wallet(self):
        data = {
            'src_wallet': [self.src_wallet_1.pk,
                           self.src_wallet_2.pk],
            'dst_wallet': self.dst_wallet.pk,
            'score': self.TRANSFER_SCORE,
        }
        self.auth_client.post(
            reverse('wallet:transfer'),
            data=data
        )
        wallet_balance = Wallet.objects.get(name=self.DST_WALLET_NAME).balance
        expected_balance = self.WALLET_BALANCE + self.TRANSFER_SCORE
        self.assertEqual(wallet_balance,
                         expected_balance,
                         msg='Некорректно начисляются средства при переводе '
                             'с нескольких кошельков'
                         )

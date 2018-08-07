# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from .service import WebpayService


class WebpayPatpass(WebpayService):
    WSDL_INTEGRACION = 'https://webpay3gint.transbank.cl/WSWebpayTransaction/cxf/WSWebpayService?wsdl'
    WSDL_CERTIFICATION = 'https://webpay3gint.transbank.cl/WSWebpayTransaction/cxf/WSWebpayService?wsdl'
    WSDL_PRODUCCION = 'https://webpay3g.transbank.cl/WSWebpayTransaction/cxf/WSWebpayService?wsdl'

    def init_transaction(self, amount, buy_order, return_url, final_url, service_id, expiration_date, commerce_email, card_holder=None, use_uf=False, session_id=None):
        """
        Extended function to use Patpass
        Arguments for init_transaction:
            service_id -- string:30 id of the provided service for suscription
            expiration_date -- string:10 contains a date in YYYY-MM-DD format
            commerce_email -- string:50
            card_holder -- dictionary containing:
                cardHolderId -- string:12 contains chilean rut on format: nn.nnn.nnn-n
                cardHolderName -- string:50
                cardHolderLastName1 -- string:30
                cardHolderLastName2 -- string:30
                cardHolderMail -- string:30
                cellPhoneNumber -- string
        """
        
        arguments = {
            'wSTransactionType': 'TR_NORMAL_WS_WPM',
            'commerceId': self.commerce.commerce_code,
            'buyOrder': buy_order,
            'sessionId': session_id,
            'returnURL': return_url,
            'finalURL': final_url,
            'transactionDetails': [
                (
                    'wsTransactionDetail',
                    {
                        'amount': amount,
                        'commerceCode': self.commerce.commerce_code,
                        'buyOrder': buy_order
                    }
                )
            ],
            'wPMDetail': [
                (
                    'wpmDetailInput',
                    {
                        'serviceId': service_id,
                        'cardHolderId': card_holder['cardHolderId'],
                        'cardHolderName': card_holder['cardHolderName'],
                        'cardHolderLastName1': card_holder['cardHolderLastName1'],
                        'cardHolderLastName2': card_holder['cardHolderLastName2'],
                        'cardHolderMail': card_holder['cardHolderMail'],
                        'cellPhoneNumber': card_holder['cellPhoneNumber'],
                        'expirationDate': expiration_date,
                        'commerceMail': commerce_email,
                        'amount': amount,
                        'ufFlag': use_uf,
                    }
                )
            ]
        }
        init_transaction_input = self.soap_client.create_input(
            'wsInitTransactionInput', arguments)
        return self.soap_client.request('initTransaction', init_transaction_input)

    def get_transaction_result(self, token):
        return self.soap_client.request('getTransactionResult', token)

    def acknowledge_transaction(self, token):
        return self.soap_client.request('acknowledgeTransaction', token)

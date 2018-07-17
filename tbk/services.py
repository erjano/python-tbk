
import logging

from .soap import SoapRequestor, create_soap_client


class TBKWebService(object):

    def __init__(self, commerce, soap_requestor):
        self.commerce = commerce
        self.soap_requestor = soap_requestor
        self.logger = logging.getLogger('tbk.services.{}'.format(self.__class__.__name__))

    @classmethod
    def init_for_commerce(cls, commerce, soap_client_class=None):
        soap_client = create_soap_client(
            wsdl_url=cls.get_wsdl_url_for_environent(commerce.environment),
            key_data=commerce.key_data,
            cert_data=commerce.cert_data,
            tbk_cert_data=commerce.tbk_cert_data,
            client_class=soap_client_class
        )
        soap_requestor = SoapRequestor(soap_client)
        return cls(commerce, soap_requestor)

    @classmethod
    def get_wsdl_url_for_environent(cls, environment):
        try:
            return getattr(cls, 'WSDL_{}'.format(environment))
        except AttributeError:
            raise ValueError("Invalid environment {}".format(environment))


class OneClickPaymentService(TBKWebService):

    WSDL_INTEGRACION = 'https://webpay3gint.transbank.cl/webpayserver/wswebpay/OneClickPaymentService?wsdl'
    WSDL_CERTIFICACION = 'https://webpay3gint.transbank.cl/webpayserver/wswebpay/OneClickPaymentService?wsdl'
    WSDL_PRODUCCION = 'https://webpay3g.transbank.cl/webpayserver/wswebpay/OneClickPaymentService?wsdl'

    def init_inscription(self, username, email, response_url):
        arguments = {
            'username': username,
            'email': email,
            'responseURL': response_url
        }
        one_click_inscription_input = self.soap_requestor.create_object('oneClickInscriptionInput', **arguments)
        return self.soap_requestor.request('initInscription', one_click_inscription_input)

    def finish_inscription(self, token):
        finish_inscription_input = self.soap_requestor.create_object('oneClickFinishInscriptionInput', token=token)
        return self.soap_requestor.request('finishInscription', finish_inscription_input)

    def authorize(self, buy_order, tbk_user, username, amount):
        arguments = {
            'buyOrder': buy_order,
            'tbkUser': tbk_user,
            'username': username,
            'amount': amount
        }
        pay_input = self.soap_requestor.create_object('oneClickPayInput', **arguments)
        return self.soap_requestor.request('authorize', pay_input)

    def code_reverse_oneclick(self, buyorder):
        reverse_input = self.soap_requestor.create_object('oneClickReverseInput', buyorder=buyorder)
        return self.soap_requestor.request('codeReverseOneClick', reverse_input)

    def remove_user(self, tbk_user, username):
        arguments = {
            'tbkUser': tbk_user,
            'username': username
        }
        one_click_remove_user_input = self.soap_requestor.create_object('oneClickRemoveUserInput', **arguments)
        return self.soap_requestor.request('oneClickRemoveUser', one_click_remove_user_input)


class WebpayService(TBKWebService):

    WSDL_INTEGRACION = 'https://webpay3gint.transbank.cl/WSWebpayTransaction/cxf/WSWebpayService?wsdl'
    WSDL_CERTIFICATION = 'https://webpay3gint.transbank.cl/WSWebpayTransaction/cxf/WSWebpayService?wsdl'
    WSDL_PRODUCCION = 'https://webpay3g.transbank.cl/WSWebpayTransaction/cxf/WSWebpayService?wsdl'

    def init_transaction(self, amount, buy_order, return_url, final_url, session_id=None):
        transaction_type = self.soap_requestor.get_enum_value('wsTransactionType', 'TR_NORMAL_WS')
        arguments = {
            'wSTransactionType': transaction_type,
            'commerceId': self.commerce.commerce_code,
            'buyOrder': buy_order,
            'sessionId': session_id,
            'returnURL': return_url,
            'finalURL': final_url,
            'transactionDetails': [
                self.soap_requestor.create_object(
                    'wsTransactionDetail',
                    amount=amount,
                    commerceCode=self.commerce.commerce_code,
                    buyOrder=buy_order
                )
            ],
            'wPMDetail': self.soap_requestor.create_object('wpmDetailInput')
        }
        init_transaction_input = self.soap_requestor.create_object('wsInitTransactionInput', **arguments)
        return self.soap_requestor.request('initTransaction', init_transaction_input)

    def get_transaction_result(self, token):
        return self.soap_requestor.request('getTransactionResult', token)

    def acknowledge_transaction(self, token):
        return self.soap_requestor.request('acknowledgeTransaction', token)


class CommerceIntegrationService(TBKWebService):

    WSDL_INTEGRACION = 'https://webpay3gint.transbank.cl/WSWebpayTransaction/cxf/WSCommerceIntegrationService?wsdl'
    WSDL_CERTIFICACION = 'https://webpay3gint.transbank.cl/WSWebpayTransaction/cxf/WSCommerceIntegrationService?wsdl'
    WSDL_PRODUCCION = 'https://webpay3g.transbank.cl/WSWebpayTransaction/cxf/WSCommerceIntegrationService?wsdl'

    def nullify(self, authorization_code, authorized_amount, buy_order, nullify_amount):
        arguments = {
            'authorizationCode': authorization_code,
            'authorizedAmount': authorized_amount,
            'buyOrder': buy_order,
            'commerceId': self.commerce.commerce_code,
            'nullifyAmount': nullify_amount
        }
        nullification_input = self.soap_requestor.create_object('nullificationInput', **arguments)
        return self.soap_requestor.request('nullify', nullification_input)

    def capture(self, authorization_code, capture_amount, buy_order):
        arguments = {
            'commerceId': self.commerce.commerce_code,
            'authorizationCode': authorization_code,
            'buyOrder': buy_order,
            'captureAmount': capture_amount
        }
        capture_input = self.soap_requestor.create_object('captureInput', **arguments)
        return self.soap_requestor.request('capture', capture_input)


class CompleteWebpayService(TBKWebService):

    WSDL_INTEGRACION = 'https://webpay3gint.transbank.cl/WSWebpayTransaction/cxf/WSCompleteWebpayService?wsdl'
    WSDL_CERTIFICACION = 'https://webpay3gint.transbank.cl/WSWebpayTransaction/cxf/WSCompleteWebpayService?wsdl'
    WSDL_PRODUCCION = 'https://webpay3g.transbank.cl/WSWebpayTransaction/cxf/WSCompleteWebpayService?wsdl'

    def init_complete_transaction(self, amount, buy_order, card_expiration_date, cvv, card_number, session_id=None):
        transaction_type = self.soap_requestor.get_enum_value('wsCompleteTransactionType', 'TR_COMPLETA_WS')

        card_detail_arguments = {
            'cardExpirationDate': card_expiration_date,
            'cvv': cvv,
            'cardNumber': card_number
        }
        card_detail = self.soap_requestor.create_object(
            'completeCardDetail', **card_detail_arguments)

        transaction_details_arguments = {
            'amount': amount,
            'buyOrder': buy_order,
            'commerceCode': self.commerce.commerce_code
        }
        transaction_details = self.soap_requestor.create_object(
            'wsCompleteTransactionDetail', **transaction_details_arguments)

        transaction_input_arguments = {
            'transactionType': transaction_type,
            'sessionId': session_id,
            'cardDetail': card_detail,
            'transactionDetails': transaction_details
        }

        transaction_input = self.soap_requestor.create_object(
            'wsCompleteInitTransactionInput', **transaction_input_arguments)

        return self.soap_requestor.request('initCompleteTransaction', transaction_input)

    def queryshare(self, token, buy_order, share_number):
        arguments = {
            'token': token,
            'buyOrder': buy_order,
            'shareNumber': share_number
        }
        queryshare_input = self.soap_requestor.create_object(
            'wsCompleteQueryShareInput', **arguments)

        return self.soap_requestor.request('queryShare', queryshare_input)

    def authorize(self, token, buy_order, grace_period, id_query_share, deferred_period_index):
        query_share_input_arguments = {
            'idQueryShare': id_query_share,
            'deferredPeriodIndex': deferred_period_index
        }
        query_share_input = self.soap_requestor.create_object(
            'wsCompleteQueryShareInput', **query_share_input_arguments)

        payment_type_input_arguments = {
            'buyOrder': buy_order,
            'commerceCode': self.commerce.commerce_code,
            'gracePeriod': grace_period,
            'queryShareInput': query_share_input
        }
        payment_type_input = self.soap_requestor.create_object(
            'wsCompletePaymentTypeInput', **payment_type_input_arguments)

        authorize_arguments = {
            'token': token,
            'paymentTypeList': payment_type_input
        }
        authorize_input = self.soap_requestor.create_object('authorize', **authorize_arguments)

        return self.soap_requestor.request('authorize', authorize_input)

    def acknowledge_transaction(self, token):
        return self.soap_requestor.request('acknowledgeTransaction', token)
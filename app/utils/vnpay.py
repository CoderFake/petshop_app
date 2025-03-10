import hashlib
import hmac
import urllib.parse
import datetime
import os
from flask import url_for, request, current_app


class VNPay:
    def __init__(self):
        self.vnp_Version = "2.1.0"
        self.vnp_TmnCode = os.environ.get('VNPAY_TMN_CODE', '')
        self.vnp_HashSecret = os.environ.get('VNPAY_HASH_SECRET', '')
        self.vnp_Url = os.environ.get('VNPAY_URL', 'https://sandbox.vnpayment.vn/paymentv2/vpcpay.html')
        self.vnp_ReturnUrl = ''

    def get_payment_url(self, order_id, amount, order_desc, bank_code=None):
        if not self.vnp_ReturnUrl:
            self.vnp_ReturnUrl = url_for('payment.vnpay_return', _external=True)

        vnp_Params = {}
        vnp_Params['vnp_Version'] = self.vnp_Version
        vnp_Params['vnp_Command'] = 'pay'
        vnp_Params['vnp_TmnCode'] = self.vnp_TmnCode
        vnp_Params['vnp_Amount'] = int(amount) * 100
        vnp_Params['vnp_CurrCode'] = 'VND'
        vnp_Params['vnp_BankCode'] = bank_code if bank_code else ''
        vnp_Params['vnp_TxnRef'] = str(order_id)
        vnp_Params['vnp_OrderInfo'] = order_desc
        vnp_Params['vnp_OrderType'] = 'billpayment'
        vnp_Params['vnp_Locale'] = 'vn'
        vnp_Params['vnp_ReturnUrl'] = self.vnp_ReturnUrl
        vnp_Params['vnp_IpAddr'] = request.remote_addr

        now = datetime.datetime.now()
        vnp_Params['vnp_CreateDate'] = now.strftime('%Y%m%d%H%M%S')

        vnp_data = self.process_params(vnp_Params)

        query = '&'.join([f"{k}={v}" for k, v in vnp_data.items()])
        signed_query = f"{query}&vnp_SecureHash={self.create_secure_hash(vnp_data)}"

        return f"{self.vnp_Url}?{signed_query}"

    def validate_response(self, response_data):
        vnp_data = response_data.copy()

        vnp_secure_hash = vnp_data.get('vnp_SecureHash', '')

        if not vnp_secure_hash:
            return False, None, None, None

        if 'vnp_SecureHash' in vnp_data:
            vnp_data.pop('vnp_SecureHash')

        if 'vnp_SecureHashType' in vnp_data:
            vnp_data.pop('vnp_SecureHashType')

        calculated_hash = self.create_secure_hash(vnp_data)

        if vnp_secure_hash != calculated_hash:
            return False, None, None, None

        order_id = vnp_data.get('vnp_TxnRef')
        amount = int(vnp_data.get('vnp_Amount', 0)) / 100
        response_code = vnp_data.get('vnp_ResponseCode', '')

        return True, order_id, amount, response_code

    def process_params(self, params):
        sorted_params = sorted(params.items())

        processed_params = {}
        for key, value in sorted_params:
            processed_params[key] = urllib.parse.quote_plus(str(value))

        return processed_params

    def create_secure_hash(self, data):
        sorted_data = sorted(data.items())

        hash_data = '&'.join([f"{k}={v}" for k, v in sorted_data])

        h = hmac.new(
            self.vnp_HashSecret.encode('utf-8'),
            hash_data.encode('utf-8'),
            hashlib.sha512
        )

        return h.hexdigest()
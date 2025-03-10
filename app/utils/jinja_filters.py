from app.utils.datetime_helpers import format_datetime, utc_to_local

def register_filters(app):

    @app.template_filter('format_datetime')
    def _format_datetime(dt, format='%d/%m/%Y %H:%M'):
        return format_datetime(dt, format)

    @app.template_filter('local_datetime')
    def _local_datetime(dt):
        return utc_to_local(dt)

    @app.template_filter('format_currency')
    def _format_currency(value):
        if value is None:
            return "0đ"
        return "{:,.0f}đ".format(float(value))

    @app.template_filter('status_class')
    def _status_class(status):
        classes = {
            'pending': 'warning',
            'processing': 'info',
            'shipped': 'primary',
            'delivered': 'success',
            'cancelled': 'danger',
            'paid': 'success',
            'refunded': 'info',
            'failed': 'danger',
        }
        return classes.get(status, 'secondary')

    @app.template_filter('status_text')
    def _status_text(status):
        texts = {
            'pending': 'Chờ xác nhận',
            'processing': 'Đang xử lý',
            'shipped': 'Đang giao hàng',
            'delivered': 'Đã giao hàng',
            'cancelled': 'Đã hủy',
            'paid': 'Đã thanh toán',
            'refunded': 'Đã hoàn tiền',
            'failed': 'Thanh toán thất bại',
        }
        return texts.get(status, status)

    @app.template_filter('payment_method_text')
    def _payment_method_text(method):
        methods = {
            'cod': 'Thanh toán khi nhận hàng (COD)',
            'vnpay': 'Thanh toán qua VNPay',
        }
        return methods.get(method, method)
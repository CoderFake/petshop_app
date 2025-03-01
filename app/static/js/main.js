
$(document).ready(function() {
    'use strict';

    $('[data-toggle="tooltip"]').tooltip();
    $('[data-toggle="popover"]').popover();

    const backToTopButton = $('#backToTop');

    $(window).scroll(function() {
        if ($(this).scrollTop() > 300) {
            backToTopButton.fadeIn();
        } else {
            backToTopButton.fadeOut();
        }
    });

    backToTopButton.click(function(e) {
        e.preventDefault();
        $('html, body').animate({scrollTop: 0}, 800);
    });

    $('.navbar-toggler').click(function() {
        $(this).toggleClass('active');
    });

    if (window.innerWidth > 992) {
        $('.navbar .dropdown').hover(
            function() {
                $(this).find('.dropdown-menu').first().stop(true, true).delay(250).slideDown();
            },
            function() {
                $(this).find('.dropdown-menu').first().stop(true, true).delay(100).slideUp();
            }
        );
    }

    $('.quantity-select .btn').click(function(e) {
        e.preventDefault();

        const input = $(this).closest('.quantity-select').find('input');
        const value = parseInt(input.val());

        if ($(this).hasClass('btn-minus')) {
            if (value > 1) {
                input.val(value - 1);
            }
        } else {
            input.val(value + 1);
        }
    });

    $('.add-to-cart').click(function(e) {
        e.preventDefault();

        const productCard = $(this).closest('.product-card');
        const productImg = productCard.find('img').eq(0);
        const productTitle = productCard.find('.product-title a').text();
        const cartIcon = $('.navbar .fa-shopping-cart');

        if (productImg.length) {
            const imgClone = productImg.clone()
                .offset({
                    top: productImg.offset().top,
                    left: productImg.offset().left
                })
                .css({
                    'opacity': '0.8',
                    'position': 'absolute',
                    'height': productImg.height(),
                    'width': productImg.width(),
                    'z-index': '2000'
                })
                .appendTo($('body'))
                .animate({
                    'top': cartIcon.offset().top + 10,
                    'left': cartIcon.offset().left + 10,
                    'width': 75,
                    'height': 75
                }, 1000, 'easeInOutExpo');

            setTimeout(function() {
                imgClone.remove();

                let cartCount = parseInt($('.navbar .badge').text());
                $('.navbar .badge').text(cartCount + 1);

                showNotification('success', 'Đã thêm ' + productTitle + ' vào giỏ hàng!');
            }, 1000);
        } else {
            let cartCount = parseInt($('.navbar .badge').text());
            $('.navbar .badge').text(cartCount + 1);

            showNotification('success', 'Đã thêm ' + productTitle + ' vào giỏ hàng!');
        }
    });

    // Newsletter subscription
    $('#newsletterForm').submit(function(e) {
        e.preventDefault();
        const email = $(this).find('input[type="email"]').val();

        // Mock AJAX call - in real app, this would submit to your backend
        setTimeout(function() {
            showNotification('success', 'Cảm ơn bạn đã đăng ký nhận tin với email: ' + email);
            $('#newsletterForm')[0].reset();
        }, 500);
    });

    // Search form validation
    $('.navbar form').submit(function(e) {
        const searchTerm = $(this).find('input').val().trim();
        if (searchTerm === '') {
            e.preventDefault();
            showNotification('warning', 'Vui lòng nhập từ khóa tìm kiếm!');
        }
    });

    function showNotification(type, message) {
        $('.custom-notification').remove();
        const notification = $('<div class="custom-notification ' + type + '">' +
                               '<span class="notification-icon">' +
                               (type === 'success' ? '<i class="fas fa-check-circle"></i>' :
                                type === 'warning' ? '<i class="fas fa-exclamation-triangle"></i>' :
                                '<i class="fas fa-info-circle"></i>') +
                               '</span>' +
                               '<span class="notification-message">' + message + '</span>' +
                               '<button type="button" class="close">&times;</button>' +
                               '</div>');

        $('body').append(notification);
        setTimeout(function() {
            notification.addClass('show');
        }, 50);

        notification.find('.close').click(function() {
            notification.removeClass('show');
            setTimeout(function() {
                notification.remove();
            }, 300);
        });

        // Auto-hide after 5 seconds
        setTimeout(function() {
            notification.removeClass('show');
            setTimeout(function() {
                notification.remove();
            }, 300);
        }, 5000);
    }

    const notificationStyles = `
        .custom-notification {
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 15px 20px;
            border-radius: 4px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            display: flex;
            align-items: center;
            transform: translateX(120%);
            transition: transform 0.3s ease-out;
            z-index: 9999;
            background-color: white;
            min-width: 300px;
            max-width: 400px;
        }
        .custom-notification.show {
            transform: translateX(0);
        }
        .custom-notification.success {
            border-left: 4px solid #2ecc71;
        }
        .custom-notification.warning {
            border-left: 4px solid #f39c12;
        }
        .custom-notification.error {
            border-left: 4px solid #e74c3c;
        }
        .custom-notification .notification-icon {
            margin-right: 15px;
            font-size: 24px;
        }
        .custom-notification.success .notification-icon {
            color: #2ecc71;
        }
        .custom-notification.warning .notification-icon {
            color: #f39c12;
        }
        .custom-notification.error .notification-icon {
            color: #e74c3c;
        }
        .custom-notification .notification-message {
            flex: 1;
        }
        .custom-notification .close {
            background: none;
            border: none;
            color: #999;
            font-size: 20px;
            cursor: pointer;
            padding: 0;
            margin-left: 10px;
        }
    `;

    $('<style>').html(notificationStyles).appendTo('head');
});

if (typeof $.easing.easeInOutExpo !== 'function') {
    $.easing.easeInOutExpo = function(x, t, b, c, d) {
        if (t==0) return b;
        if (t==d) return b+c;
        if ((t/=d/2) < 1) return c/2 * Math.pow(2, 10 * (t - 1)) + b;
        return c/2 * (-Math.pow(2, -10 * --t) + 2) + b;
    };
}
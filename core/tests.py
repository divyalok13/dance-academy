from types import SimpleNamespace
from unittest.mock import patch, MagicMock

from django.contrib.auth.models import AnonymousUser
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.test import RequestFactory, SimpleTestCase, override_settings
from django.urls import reverse

from . import views
from .models import DandiyaRegistration


@override_settings(STORAGES={"staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"}})
class RedesignRegressionTests(SimpleTestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_home_with_empty_content(self):
        html = render_to_string('home.html', {}, request=self.factory.get('/'))
        for marker in ['primary-navigation', 'aria-expanded="false"', 'gallery-lightbox',
                       'Merry Christmas', 'wsdc-offerings-track', '/book-trial/']:
            self.assertIn(marker, html)

    def test_gallery_keeps_full_image_link_and_testimonial_controls(self):
        image = SimpleNamespace(image=SimpleNamespace(url='/media/dance.jpg'), title='Dance night')
        testimonial = SimpleNamespace(rating=5, message='Wonderful class', name='Student')
        html = render_to_string('home.html', {'gallery_images': [image], 'testimonials': [testimonial]})
        self.assertIn('href="/media/dance.jpg"', html)
        self.assertIn('data-testimonial-step="1"', html)
        self.assertIn('Wonderful class', html)

    @patch('core.views.get_object_or_404')
    @patch('core.views.render', return_value=HttpResponse())
    def test_pending_coupon_is_not_valid(self, render, lookup):
        lookup.return_value = SimpleNamespace(payment_status=DandiyaRegistration.PaymentStatus.PENDING)
        views.dandiya_coupon(self.factory.get('/'), 'token')
        self.assertFalse(render.call_args.args[2]['coupon_valid'])

    @patch('core.views.get_object_or_404')
    @patch('core.views.render', return_value=HttpResponse())
    def test_pending_pdf_is_denied(self, render, lookup):
        lookup.return_value = SimpleNamespace(payment_status=DandiyaRegistration.PaymentStatus.PENDING)
        response = views.dandiya_coupon_pdf(self.factory.get('/'), 'token')
        self.assertFalse(render.call_args.args[2]['coupon_valid'])
        self.assertNotEqual(response.get('Content-Type'), 'application/pdf')

    def test_checkin_requires_staff(self):
        request = self.factory.get(reverse('dandiya_checkin'))
        request.user = AnonymousUser()
        self.assertEqual(views.dandiya_checkin(request).status_code, 302)

    @patch('core.views.transaction.atomic')
    @patch('core.views.DandiyaRegistration.objects')
    @patch('core.views.render', return_value=HttpResponse())
    def test_checkin_payment_gate_and_duplicate_entry(self, render, manager, atomic):
        registration = SimpleNamespace(checked_in=False, payment_status='Pending', save=MagicMock())
        manager.select_for_update.return_value.select_related.return_value.filter.return_value.first.return_value = registration
        request = self.factory.post('/', {'entry_code': 'WSDC-1-ABC12345'})
        request.user = SimpleNamespace(is_active=True, is_staff=True)
        views.dandiya_checkin(request)
        self.assertEqual(render.call_args.args[2]['checkin_result'], 'payment_pending')
        registration.save.assert_not_called()
        registration.payment_status = 'Paid'
        views.dandiya_checkin(request)
        self.assertEqual(render.call_args.args[2]['checkin_result'], 'approved')
        registration.save.assert_called_once()
        views.dandiya_checkin(request)
        self.assertEqual(render.call_args.args[2]['checkin_result'], 'already_used')
        registration.save.assert_called_once()

    @patch('core.views.get_object_or_404')
    def test_paid_coupon_generates_pdf_with_qr(self, lookup):
        from datetime import date
        from decimal import Decimal
        from .models import DandiyaEvent, DandiyaPass
        event = DandiyaEvent(name='Dandiya night', event_date=date(2026, 10, 15), venue='Buxar')
        ticket = DandiyaPass(event=event, name='Single pass', price=Decimal('100'))
        registration = DandiyaRegistration(event=event, dandiya_pass=ticket,
            name='Test guest', phone='9876543210', payment_status='Paid',
            entry_code='WSDC-1-ABC12345', number_of_passes=1, total_amount=Decimal('100'))
        lookup.return_value = registration
        response = views.dandiya_coupon_pdf(self.factory.get('/'), 'token')
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertTrue(response.content.startswith(b'%PDF-'))

    @patch('core.views.DandiyaRegistrationForm')
    @patch('core.views.DandiyaRegistration.objects')
    @patch('core.views.get_object_or_404')
    def test_registration_calculates_total_and_keeps_session(self, lookup, manager, form_class):
        from decimal import Decimal
        event = SimpleNamespace(id=7)
        lookup.return_value = event
        manager.filter.return_value.exists.return_value = False
        registration = SimpleNamespace(dandiya_pass=SimpleNamespace(price=Decimal('250')),
            number_of_passes=2, id=42, save=MagicMock())
        form_class.return_value.is_valid.return_value = True
        form_class.return_value.save.return_value = registration
        request = self.factory.post('/', {})
        request.session = {}
        response = views.dandiya_registration(request, event.id)
        self.assertEqual(registration.total_amount, Decimal('500'))
        self.assertEqual(registration.event, event)
        self.assertTrue(registration.entry_code.startswith('WSDC-7-'))
        registration.save.assert_called_once()
        self.assertEqual(request.session['dandiya_registration_id'], 42)
        self.assertEqual(response.status_code, 302)

from django.contrib import admin
from django.core.exceptions import ValidationError
from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.test import RequestFactory, SimpleTestCase, TestCase, TransactionTestCase, override_settings

from .models import GalleryImage


class GalleryValidationTests(SimpleTestCase):
    def test_video_types_and_https_validation(self):
        field = GalleryImage._meta.get_field('video_url')
        for url in ['', 'https://res.cloudinary.com/demo/video/upload/dance.mp4',
                    'https://cdn.example.com/dance.webm?version=2']:
            field.clean(url, None)
            item = GalleryImage(video_url=url)
            item.clean()
            self.assertEqual(item.media_type, 'video' if url else 'photo')
        for url in ['http://example.com/dance.mp4', 'javascript:alert(1)']:
            with self.assertRaises(ValidationError):
                field.clean(url, None)
        for url in ['https://youtube.com/watch?v=123', 'https://example.com/page', 'https://[invalid/clip.mp4']:
            with self.assertRaises(ValidationError):
                GalleryImage(video_url=url).clean()

    def test_admin_exposes_poster_and_video(self):
        model_admin = admin.site._registry[GalleryImage]
        form = model_admin.get_form(RequestFactory().get('/admin/'))
        self.assertIn('video_url', form.base_fields)
        self.assertTrue(form.base_fields['image'].required)
        self.assertFalse(form.base_fields['video_url'].required)
        self.assertEqual(form.base_fields['image'].label, 'Photo or video poster')


@override_settings(STORAGES={'staticfiles': {'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage'},
                             'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage'}})
class GalleryPageTests(TestCase):
    def test_home_mixes_active_photos_and_videos(self):
        photo = GalleryImage.objects.create(title='Dance photo', image='gallery/photo.jpg')
        clip = GalleryImage.objects.create(title='Dance film', image='gallery/poster.jpg',
            video_url='https://example.com/dance.mp4')
        GalleryImage.objects.create(title='Hidden moment', image='gallery/hidden.jpg', is_active=False)
        response = self.client.get('/', HTTP_HOST='localhost')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'data-media-type="photo"', count=1)
        self.assertContains(response, 'data-media-type="video"', count=1)
        self.assertContains(response, 'https://example.com/dance.mp4')
        self.assertContains(response, 'loading="lazy"')
        self.assertContains(response, 'preload="none"')
        self.assertContains(response, 'data-gallery-filter="video"')
        self.assertNotContains(response, 'Hidden moment')
        photo.refresh_from_db()
        self.assertEqual(photo.video_url, '')
        self.assertEqual(clip.media_type, 'video')

    def test_admin_can_add_video_with_poster(self):
        from io import BytesIO
        from tempfile import TemporaryDirectory
        from PIL import Image
        from django.contrib.auth import get_user_model
        from django.core.files.uploadedfile import SimpleUploadedFile
        user = get_user_model().objects.create_superuser('gallery-admin', password='test-only-password')
        self.client.force_login(user)
        buffer = BytesIO()
        Image.new('RGB', (10, 10), 'green').save(buffer, format='JPEG')
        poster = SimpleUploadedFile('poster.jpg', buffer.getvalue(), content_type='image/jpeg')
        with TemporaryDirectory(prefix='wsdc-gallery-') as media_root:
            with override_settings(MEDIA_ROOT=media_root):
                response = self.client.post('/admin/core/galleryimage/add/', {
                    'title': 'Admin video', 'image': poster,
                    'video_url': 'https://res.cloudinary.com/demo/video/upload/dance.mp4',
                    'is_active': 'on', '_save': 'Save',
                }, HTTP_HOST='localhost')
                self.assertEqual(response.status_code, 302)
                saved = GalleryImage.objects.get(title='Admin video')
                self.assertEqual(saved.media_type, 'video')
                self.assertTrue(saved.image.name.startswith('gallery/poster'))


class GalleryMigrationTests(TransactionTestCase):
    def test_additive_migration_preserves_existing_photo(self):
        executor = MigrationExecutor(connection)
        old_target = [('core', '0008_populate_coupon_tokens')]
        new_target = [('core', '0009_gallery_video_url')]
        executor.migrate(old_target)
        try:
            old_apps = executor.loader.project_state(old_target).apps
            old_model = old_apps.get_model('core', 'GalleryImage')
            old = old_model.objects.create(title='Existing photo', image='gallery/original.jpg', is_active=True)
            executor = MigrationExecutor(connection)
            executor.migrate(new_target)
            new_apps = executor.loader.project_state(new_target).apps
            saved = new_apps.get_model('core', 'GalleryImage').objects.get(pk=old.pk)
            self.assertEqual(saved.title, old.title)
            self.assertEqual(saved.image.name, old.image.name)
            self.assertEqual(saved.created_at, old.created_at)
            self.assertTrue(saved.is_active)
            self.assertEqual(saved.video_url, '')
        finally:
            MigrationExecutor(connection).migrate(new_target)

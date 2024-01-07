from django.test import TestCase


class IndexPageTest(TestCase):
    def test_index_page(self):
        response = self.client.get('/restaurant/')
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'index.html')
        self.assertContains(response, 'Book now')

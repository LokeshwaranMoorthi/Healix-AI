from django.test import TestCase
from .models import GenericMedicine

class PharmaTestCase(TestCase):
    def setUp(self):
        GenericMedicine.objects.create(
            brand_name="Augmentin", 
            generic_equivalent="Amoxicillin + Clavulanic Acid",
            cost_savings_pct=70
        )

    def test_medicine_mapping(self):
        med = GenericMedicine.objects.get(brand_name="Augmentin")
        self.assertEqual(med.generic_equivalent, "Amoxicillin + Clavulanic Acid")
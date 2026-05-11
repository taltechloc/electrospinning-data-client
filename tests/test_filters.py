import unittest
from electrospinning_data_client.filters import FilterBuilder

class TestFilterBuilder(unittest.TestCase):
    def test_basic_filters(self):
        fb = FilterBuilder().polymer("PAN").voltage(min_val=20, max_val=30)
        filters = fb.build()
        
        self.assertEqual(filters["polymer"], "PAN")
        self.assertEqual(filters["voltageMin"], 20)
        self.assertEqual(filters["voltageMax"], 30)

    def test_custom_filters(self):
        fb = FilterBuilder().custom("customField", "value")
        self.assertEqual(fb.build()["customField"], "value")

    def test_string_representation(self):
        fb = FilterBuilder().polymer("PVP")
        self.assertEqual(str(fb), '{"polymer": "PVP"}')

if __name__ == '__main__':
    unittest.main()

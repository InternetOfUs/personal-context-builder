import unittest
import datetime

from wenet_pcb.wenet_models import StayRegion, LabelledStayRegion


class LabelledStayRegionTestCase(unittest.TestCase):
    def test_construction(self):
        t1 = datetime.datetime.now()
        t2 = datetime.datetime.now()
        region = StayRegion(t1, t2, 1.5, 1.5, 2, 2, 1, 1)
        labelled_region = LabelledStayRegion("test", region)
        self.assertEqual(labelled_region._label, "test")
        labelled_region_dict = labelled_region.__dict__
        del labelled_region_dict["_label"]
        self.assertDictEqual(labelled_region_dict, region.__dict__)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()

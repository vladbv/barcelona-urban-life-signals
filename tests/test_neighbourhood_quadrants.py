"""Check survey nonresponses, weighting and quadrant boundaries."""
import unittest
import pandas as pd
from src.neighbourhood_quadrants import classify, summarise_survey, name_key


class QuadrantTests(unittest.TestCase):
    def test_endpoints_nonresponse_weights_and_year(self):
        frame = pd.DataFrame({'ANY':[2025]*4+[2024], 'BARRI':['EL RAVAL']*5,
                              'SATISF_RES_BARRI_0A10':['0 = GENS SATISFET/A','10 = MOLT SATISFET/A','NO HO SAP','NO CONTESTA','10'],
                              'PES':[1,3,2,2,100]})
        row = summarise_survey(frame).iloc[0]
        self.assertEqual(row.satisfaction, 7.5)
        self.assertEqual(row.valid_responses, 2)
        self.assertEqual(row.nonresponses, 2)
        self.assertAlmostEqual(row.effective_n, 1.6)

    def test_all_quadrants_ties_and_missing(self):
        for x,y,want in [(2,8,'Premium Living'),(1,8,'Best Value'),
                         (2,6,'Less for your money'),(1,6,'Budget Living'),
                         (2,7,'Premium Living'),(float('nan'),7,'Insufficient data')]:
            self.assertEqual(classify(x,y,2,7),want)

    def test_explicit_name_normalization(self):
        self.assertEqual(name_key('el Poble Sec - AEI Parc Montjuïc'), name_key('EL POBLE SEC'))
        self.assertEqual(name_key('Sants - Badal '),name_key('SANTS-BADAL'))
        self.assertNotEqual(name_key('la Marina de Port'),name_key('la Marina del Prat Vermell'))

import unittest
from src.classes.sorter.abstract_sorter import AbstractSorter


class TestUtils(unittest.TestCase):

    def setUp(self):
        self.test_sorter = AbstractSorter()

    def tearDown(self):
        self.test_sorter = None

    def test_build_source_regular(self):
        material = [
            (
                'http://morecomplicatedURL.com/path1',
                '/test.ext',
                'http://morecomplicatedURL.com/test.ext'
            ),

            (
                'http://httpURL.com',
                '//9f84/c7d6595/0a08',
                'http://9f84/c7d6595/0a08'
            ),

            (
                'https://httpsURL.com',
                '//9f84/c7d6595/0a08',
                'https://9f84/c7d6595/0a08'
            ),

            (
                'http://beginwithslash.com/test/for/absolute',
                '/ressource_starting_with_slash',
                'http://beginwithslash.com/ressource_starting_with_slash'
            ),
        ]

        for test_case in material:
            with self.subTest(case=test_case):
                self.assertEqual(test_case[2], self.test_sorter.build_source(test_case[0], test_case[1]))

    def test_build_source_with_base(self):
        abstract = AbstractSorter()
        material = [
            (
                'http://sourcewithbase.com',
                'img.test',
                'http://sourcewithbase.com/long/path/with/base/',
                'http://sourcewithbase.com/long/path/with/base/img.test'
            ),

            (
                'https://sourcewithshorterbase.com/with/long/orignial/url/',
                'base.test',
                'https://sourcewithshorterbase.com/',
                'https://sourcewithshorterbase.com/base.test'
            ),

            (
                'https://urlwithdifferentbase.com/',
                'base.test',
                'https://differentbase.com/base/path/to/base/',
                'https://differentbase.com/base/path/to/base/base.test'
            )
        ]

        for test_case in material:
            with self.subTest(case=test_case):
                self.assertEqual(test_case[3], self.test_sorter.build_source(test_case[0], test_case[1], test_case[2]))

    def test_with_url(self):
        material = [
            (
                'http://irrelevanturl.com',
                'http://urlwithhttp.com',
                'http://urlwithhttp.com'
            ),

            (
                'http://httpURL.com',
                'https://urlwihthttps.com',
                'https://urlwihthttps.com'
            )
        ]

        for test_case in material:
            with self.subTest(case=test_case):
                self.assertEqual(test_case[2], self.test_sorter.build_source(test_case[0], test_case[1]))

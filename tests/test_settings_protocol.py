from cbibs.cbibs import CbibsModule

cbibs = CbibsModule('abcd', 'https')


# Check that the base url is being correctly generated
def test_settings_protocol():
    assert cbibs.url == 'https://mw.buoybay.noaa.gov/api/v1/'

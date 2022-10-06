import pytest

from GPIO.bmp280_zero import BMP280_zero
#convert_to_sea_level, convert_celsius_to_kelvin


@pytest.fixture(scope='function')
def BMP():
    yield BMP280_zero()


@pytest.mark.parametrize('pressure,temp_celsius,expected', [
    (1000, 25, 1012),
    (990, 16, 1002),
    (1030, 35, 1042)
])
def test_get_sea_level_pressure(BMP, pressure, temp_celsius, expected):
    sea_level_pressure = BMP.get_sea_level_pressure(pressure, temp_celsius)
    assert sea_level_pressure == expected


@pytest.mark.parametrize('temp_c, expected', [
    (20, 293.15),
    (0, 273.15),
    (50, 323.15)
])
def test_convert_celsius_to_kelvin(BMP, temp_c, expected):
    temp_k = BMP._convert_celsius_to_kelvin(temp_c)
    assert temp_k == expected


@pytest.mark.parametrize('latitude,altitude,expected', [
    (51.659167, 100, 9.82754231739798)
])
def test_get_gravitational_acceleration(BMP, latitude, altitude, expected):
    BMP.latitude = latitude
    BMP.altitude = altitude
    assert BMP._BMP280_zero__get_gravitational_acceleration() == expected

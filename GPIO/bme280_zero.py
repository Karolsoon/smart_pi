from math import sin
import bme280


class BME280_zero:

    address = 0x76

    """
    Geographical data about my location and constants for pressure calculation
    """
    altitude = 100
    latitude = 51.659167
    gas_constant = 8.31446261815324
    air_molar_mass = 0.0289644

    def __init__(self, bus, bme280_driver=bme280) -> None:
        self.bus = bus
        self.bme280 = bme280_driver
        self.bme280.load_calibration_params(self.bus, self.address)
    
    def get_all(self):
        data = self.bme280.sample(self.bus, self.address)
        return data.temperature, data.humidity, data.pressure

    def get_sea_level_pressure(self, pressure, temperature_c):
        # return self.__convert_to_sea_level(
        #     self.get_pressure(), self.get_temperature()
        # )
        return self.__convert_to_sea_level(pressure, temperature_c)

    def __convert_to_sea_level(self, atmospheric_pressure_hpa, temperature_c):
        temperature_k = self._convert_celsius_to_kelvin(temperature_c)
        gravitational_acceleration = self._get_gravitational_acceleration()
        sea_level_pressure_hpa = self.__calculate_sea_level_pressure(
                                    atmospheric_pressure_hpa,
                                    gravitational_acceleration,
                                    temperature_k
        )
        return round(sea_level_pressure_hpa, 0)

    def _convert_celsius_to_kelvin(self, temperature_c):
        return temperature_c + 273.15

    def _get_gravitational_acceleration(self):
        return (
              9.780318 \
            * (
                  1 \
                + (0.0053024 * sin(self.latitude) ** 2) \
                - (0.0000058 * sin(2 * self.latitude) ** 2) \
                - 3.086 * 10 ** (-6) \
                * self.altitude
            )
        )

    def __calculate_sea_level_pressure(self,
            atmospheric_pressure_hpa,
            gravitational_acceleration,
            temperature_k):
        return (
              atmospheric_pressure_hpa \
            / (
                  1 \
                - (
                      self.air_molar_mass \
                    * gravitational_acceleration \
                    * self.altitude
                )
            / (
                  self.gas_constant \
                * temperature_k
            )
        ))

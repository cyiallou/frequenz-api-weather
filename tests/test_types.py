# License: MIT
# Copyright © 2023 Frequenz Energy-as-a-Service GmbH

"""Test the types module."""

# pylint doesn't understand fixtures. It thinks it is redefined name.
# pylint: disable=redefined-outer-name

# pylint doesn't understand the imports from the generated proto modules.
# pylint: disable=no-name-in-module,no-member

from datetime import datetime

import numpy as np
from _pytest.logging import LogCaptureFixture
from frequenz.api.common.v1.location_pb2 import Location as LocationProto
from frequenz.api.weather import weather_pb2
from frequenz.client.weather._types import ForecastFeature, Forecasts, Location
from google.protobuf.timestamp_pb2 import Timestamp
from pytest import fixture


class TestForecastFeatureType:
    """Testing the ForecastFeature type."""

    def test_from_pb_valid(self) -> None:
        """Test if the method works correctly when a valid value is passed."""
        forecast_feature_pb_value = (
            weather_pb2.ForecastFeature.FORECAST_FEATURE_U_WIND_COMPONENT_100_METRE
        )
        result = ForecastFeature.from_pb(forecast_feature_pb_value)
        assert result == ForecastFeature.U_WIND_COMPONENT_100_METRE

    def test_from_pb_unknown(self) -> None:
        """Test if the method returns UNSPECIFIED when an unknown value is passed."""
        unknown_pb_value = 999999999  # a random unknown value
        result = ForecastFeature.from_pb(unknown_pb_value)  # type: ignore
        assert result == ForecastFeature.UNSPECIFIED

    def test_from_pb_warning_logged(self, caplog: LogCaptureFixture) -> None:
        """Test if a warning is logged when an unknown value is passed.

        Args:
            caplog: pytest fixture to capture log messages.

        """
        unknown_pb_value = 999999999  # a random unknow value
        ForecastFeature.from_pb(unknown_pb_value)  # type: ignore
        assert "Unknown forecast feature" in caplog.text

    def test_from_pb_valid_enum(self) -> None:
        """Test if the method works correctly when an enum value is passed."""
        forecast_feature_enum_value = ForecastFeature.V_WIND_COMPONENT_100_METRE.value
        result = ForecastFeature.from_pb(forecast_feature_enum_value)
        assert result == ForecastFeature.V_WIND_COMPONENT_100_METRE


class TestLocation:
    """Testing the Location type."""

    def test_from_pb(self) -> None:
        """Test if the inititlization method from proto works correctly."""
        # Create a LocationProto object
        location_proto = LocationProto(latitude=42.0, longitude=18.0, country_code="US")
        result = Location.from_pb(location_proto)

        assert result.latitude == 42.0
        assert result.longitude == 18.0
        assert result.country_code == "US"

    def test_to_pb(self) -> None:
        """Test if the to_pb method works correctly."""
        # Create a Location object
        location = Location(latitude=37.0, longitude=-122.0, country_code="CA")
        result = location.to_pb()

        assert result.latitude == 37.0
        assert result.longitude == -122.0
        assert result.country_code == "CA"

    def test_round_trip(self) -> None:
        """Test if the round trip from Location to proto and back works correctly."""
        # Create a Location object
        original_location = Location(latitude=37.0, longitude=-122.0, country_code="CA")
        location_proto = original_location.to_pb()
        result_location = Location.from_pb(location_proto)

        assert result_location.latitude == original_location.latitude
        assert result_location.longitude == original_location.longitude
        assert result_location.country_code == original_location.country_code


@fixture
def forecastdata() -> (  # pylint: disable=too-many-locals
    tuple[weather_pb2.ReceiveLiveWeatherForecastResponse, int, int, int]
):
    """Create a example ReceiveLiveWeatherForecastResponse proto object.

    Returns: tuple of example ReceiveLiveWeatherForecastResponse proto object,
    number of times, number of locations, number of features
    """
    # Create example data
    locations = [
        LocationProto(latitude=42.0, longitude=18.0, country_code="US"),
        LocationProto(latitude=43.0, longitude=19.0, country_code="CA"),
    ]
    valid_times = [
        datetime.fromisoformat("2024-01-01T01:00:00"),
        datetime.fromisoformat("2024-01-01T02:00:00"),
        datetime.fromisoformat("2024-01-01T03:00:00"),
    ]
    feature_list = [
        weather_pb2.ForecastFeature.FORECAST_FEATURE_U_WIND_COMPONENT_100_METRE,
        weather_pb2.ForecastFeature.FORECAST_FEATURE_V_WIND_COMPONENT_100_METRE,
        weather_pb2.ForecastFeature.FORECAST_FEATURE_SURFACE_SOLAR_RADIATION_DOWNWARDS,
    ]

    # Convert to Timestamp objects
    valid_tstamps = []
    for time in valid_times:
        ts = Timestamp()
        ts.FromDatetime(time)
        valid_tstamps.append(ts)

    num_locations = len(locations)
    num_times = len(valid_tstamps)
    num_features = len(feature_list)

    # Create the creation timestamp
    creation_ts = Timestamp()
    creation_ts.FromDatetime(valid_times[0])

    # Initialize list to hold location forecasts
    location_forecasts = []

    # Loop over locations
    for loc_idx, location in enumerate(locations):
        forecasts = []

        # Loop over valid times
        for time_idx, valid_ts in enumerate(valid_tstamps):
            feature_forecasts = []

            # Loop over features
            for feature_idx, feature in enumerate(feature_list):
                # Create distinct values for each combination (acc to indexing)
                value = 1 * feature_idx + 100 * time_idx + 10 * loc_idx

                # Create the FeatureForecast object
                feature_forecast = (
                    weather_pb2.LocationForecast.Forecasts.FeatureForecast(
                        feature=feature, value=value
                    )
                )
                feature_forecasts.append(feature_forecast)

            # Create the Forecasts object for the current time
            forecast = weather_pb2.LocationForecast.Forecasts(
                valid_at_ts=valid_ts, features=feature_forecasts
            )
            forecasts.append(forecast)

        # Create the LocationForecast object for the current location
        location_forecast = weather_pb2.LocationForecast(
            forecasts=forecasts, location=location, creation_ts=creation_ts
        )
        location_forecasts.append(location_forecast)

    # Create the ReceiveLiveWeatherForecastResponse proto object
    forecasts_proto = weather_pb2.ReceiveLiveWeatherForecastResponse(
        location_forecasts=location_forecasts
    )

    return forecasts_proto, num_times, num_locations, num_features


class TestForecasts:
    """Testing the Forecasts type.

    Attributes:
        forecasts_proto: example ReceiveLiveWeatherForecastResponse proto object
        num_times: number of times in the example proto object
        num_locations: number of locations in the example proto object
        num_features: number of features in the example proto object

    """

    valid_ts1 = datetime.fromisoformat("2024-01-01T01:00:00")
    valid_ts2 = datetime.fromisoformat("2024-01-01T02:00:00")
    valid_ts3 = datetime.fromisoformat("2024-01-01T03:00:00")
    invalid_ts = datetime.fromisoformat("2024-01-02T03:00:00")

    def test_from_pb(
        self,
        forecastdata: tuple[
            weather_pb2.ReceiveLiveWeatherForecastResponse, int, int, int
        ],
    ) -> None:
        """Test if the inititlization method from proto works correctly."""
        # creating a Forecasts object

        forecasts_proto, num_times, num_locations, num_features = forecastdata
        forecasts = Forecasts.from_pb(forecasts_proto)

        assert forecasts is not None

        # forecast is created from the example proto object

    def test_to_ndarray_vlf_with_no_parameters(
        self,
        forecastdata: tuple[
            weather_pb2.ReceiveLiveWeatherForecastResponse, int, int, int
        ],
    ) -> None:
        """Test if the to_ndarray method works correctly when no filter parameters are passed."""
        # create an example Forecasts object
        forecasts_proto, num_times, num_locations, num_features = forecastdata
        forecasts = Forecasts.from_pb(forecasts_proto)

        # checks if output is a numpy array and matches expected shape
        array = forecasts.to_ndarray_vlf()
        assert isinstance(array, np.ndarray)
        assert array.shape == (
            num_times,
            num_locations,
            num_features,
        )
        assert array[0, 0, 0] == 0
        assert array[1, 0, 0] == 100

    def test_to_ndarray_vlf_with_some_parameters(
        self,
        forecastdata: tuple[
            weather_pb2.ReceiveLiveWeatherForecastResponse, int, int, int
        ],
    ) -> None:
        """Test if the to_ndarray method works correctly when some filter parameters are passed."""
        # create an example Forecasts object with 3 times, 2 locations and 3 features
        forecasts_proto, num_times, num_locations, num_features = forecastdata
        forecasts = Forecasts.from_pb(forecasts_proto)

        validity_times = [self.valid_ts1, self.valid_ts2]

        locations = [Location(latitude=42.0, longitude=18.0, country_code="US")]
        # Note order of features in query is different from order in proto
        features = [
            ForecastFeature.V_WIND_COMPONENT_100_METRE,
            ForecastFeature.U_WIND_COMPONENT_100_METRE,
        ]

        array = forecasts.to_ndarray_vlf(
            validity_times=validity_times, locations=locations, features=features
        )

        # checks if output is a numpy array and matches expected shape
        assert isinstance(array, np.ndarray)
        assert array.shape == (len(validity_times), len(locations), len(features))
        # Note order of features in query is different from order in proto
        assert array[0, 0, 0] == 1
        assert array[0, 0, 1] == 0
        assert array[1, 0, 0] == 101
        assert array[1, 0, 1] == 100

    def test_to_ndarray_vlf_with_all_parameters(
        self,
        forecastdata: tuple[
            weather_pb2.ReceiveLiveWeatherForecastResponse, int, int, int
        ],
    ) -> None:
        """Test if the to_ndarray method works correctly when all filter parameters are passed."""
        # create an example Forecasts object with 3 times, 2 locations and 3 features
        forecasts_proto, num_times, num_locations, num_features = forecastdata
        forecasts = Forecasts.from_pb(forecasts_proto)

        validity_times = [self.valid_ts1, self.valid_ts2, self.valid_ts3]

        locations = [
            Location(latitude=42.0, longitude=18.0, country_code="US"),
            Location(latitude=43.0, longitude=19.0, country_code="CA"),
        ]

        features = [
            ForecastFeature.U_WIND_COMPONENT_100_METRE,
            ForecastFeature.V_WIND_COMPONENT_100_METRE,
            ForecastFeature.SURFACE_SOLAR_RADIATION_DOWNWARDS,
        ]

        array = forecasts.to_ndarray_vlf(
            validity_times=validity_times, locations=locations, features=features
        )

        # checks if output is a numpy array and matches expected shape
        assert isinstance(array, np.ndarray)
        assert array.shape == (len(validity_times), len(locations), len(features))

    def test_to_ndarray_vlf_with_missing_parameters(
        self,
        forecastdata: tuple[
            weather_pb2.ReceiveLiveWeatherForecastResponse, int, int, int
        ],
    ) -> None:
        """Test if the to_ndarray method works correctly when filter parameters are missing."""
        # create an example Forecasts object with 3 times, 2 locations and 4 features
        # where each dimension contains one key without data
        forecasts_proto, num_times, num_locations, num_features = forecastdata
        forecasts = Forecasts.from_pb(forecasts_proto)

        validity_times = [self.valid_ts1, self.valid_ts2, self.invalid_ts]

        locations = [
            # this location has no data in proto
            Location(latitude=50.0, longitude=18.0, country_code="US"),
            Location(latitude=43.0, longitude=19.0, country_code="CA"),
        ]

        features = [
            ForecastFeature.U_WIND_COMPONENT_100_METRE,
            ForecastFeature.V_WIND_COMPONENT_100_METRE,
            ForecastFeature.SURFACE_SOLAR_RADIATION_DOWNWARDS,
            ForecastFeature.SURFACE_NET_SOLAR_RADIATION,
        ]

        array = forecasts.to_ndarray_vlf(
            validity_times=validity_times, locations=locations, features=features
        )

        # checks if output is a numpy array and matches expected shape
        assert isinstance(array, np.ndarray)
        assert array.shape == (
            len(validity_times),
            len(locations),
            len(features),
        )
        assert np.isnan(array[:, 0, :]).all()
        assert np.isnan(array[2, :, :]).all()
        assert np.isnan(array[:, :, 3]).all()
        assert not np.isnan(array[0:2, 1, 0:3]).any()

        assert array[0, 1, 0] == 10
        assert array[0, 1, 1] == 11
        assert array[0, 1, 2] == 12
        assert array[1, 1, 0] == 110
        assert array[1, 1, 1] == 111
        assert array[1, 1, 2] == 112

        # Change the position of the invalid timestamp
        # yields different result
        validity_times = [self.invalid_ts, self.valid_ts1, self.valid_ts2]
        array = forecasts.to_ndarray_vlf(
            validity_times=validity_times, locations=locations, features=features
        )
        assert np.isnan(array[:, 0, :]).all()
        assert np.isnan(array[0, :, :]).all()
        assert np.isnan(array[:, :, 3]).all()
        assert not np.isnan(array[1:3, 1, 0:3]).any()

        assert array[1, 1, 0] == 10
        assert array[1, 1, 1] == 11
        assert array[1, 1, 2] == 12
        assert array[2, 1, 0] == 110
        assert array[2, 1, 1] == 111
        assert array[2, 1, 2] == 112

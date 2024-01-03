# License: MIT
# Copyright © 2023 Frequenz Energy-as-a-Service GmbH

"""The Weather Forecast API client."""

import grpc
from frequenz.api.weather import weather_pb2, weather_pb2_grpc
from frequenz.channels import Receiver
from frequenz.client.base.grpc_streaming_helper import GrpcStreamingHelper

from ._types import ForecastFeature, Forecasts, Location


class Client:
    """Weather forecast client."""

    def __init__(self, grpc_channel: grpc.aio.Channel, svc_addr: str) -> None:
        """Initialize the client.

        Args:
            grpc_channel: gRPC channel to use for communication with the API.
            svc_addr: Address of the service to connect to.
        """
        self._svc_addr = svc_addr
        self._stub = weather_pb2_grpc.WeatherForecastServiceStub(grpc_channel)
        self._streams: dict[
            tuple[Location | ForecastFeature, ...],
            GrpcStreamingHelper[
                weather_pb2.ReceiveLiveWeatherForecastResponse, Forecasts
            ],
        ] = {}

    async def stream_live_forecast(
        self,
        locations: list[Location],
        features: list[ForecastFeature],
    ) -> Receiver[Forecasts]:
        """Stream live weather forecast data.

        Args:
            locations: locations to stream data for.
            features: features to stream data for.

        Returns:
            A channel receiver for weather forecast data.
        """
        stream_key = tuple(tuple(locations) + tuple(features))

        if stream_key not in self._streams:
            self._streams[stream_key] = GrpcStreamingHelper(
                f"weather-forecast-{stream_key}",
                lambda: self._stub.ReceiveLiveWeatherForecast(  # type:ignore
                    weather_pb2.ReceiveLiveWeatherForecastRequest(
                        locations=(location.to_pb() for location in locations),
                        features=(feature.value for feature in features),
                    )
                ),
                Forecasts.from_pb,
            )
        return self._streams[stream_key].new_receiver()

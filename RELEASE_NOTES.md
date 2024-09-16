# Frequenz Weather API Release Notes

## Upgrading

* The `to_array_vlf` method now returns an array with the requested shape
  where missing data is set to `NaN`. This is a change in behavior and
  might require adjustments in the calling code, whereby the previous
  behavior could not be used in a reliable way.

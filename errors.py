class HikError(Exception):
    pass


class InvalidLengthError(HikError, ValueError):
    pass


class MalformedDeviceDataError(HikError, ValueError):
    pass


class DecryptError(HikError):
    pass

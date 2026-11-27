class DestinationError(Exception):
    pass


class DestinationNotFoundError(DestinationError):
    def __init__(self) -> None:
        super().__init__("The destination was not found")


class MunicipalityNotFoundError(DestinationError):
    def __init__(self) -> None:
        super().__init__("The municipality does not exist or is disabled")


class DuplicateDestinationError(DestinationError):
    def __init__(self) -> None:
        super().__init__("A destination with this name already exists in the municipality")


class InvalidTourismTypeError(DestinationError):
    def __init__(self, codes: list[str]) -> None:
        self.codes = codes
        super().__init__("One or more tourism types are invalid or inactive")


class InvalidNoticePeriodError(DestinationError):
    def __init__(self) -> None:
        super().__init__("The notice end date cannot be earlier than its start date")


class DestinationPersistenceError(DestinationError):
    def __init__(self) -> None:
        super().__init__("The destination could not be saved")

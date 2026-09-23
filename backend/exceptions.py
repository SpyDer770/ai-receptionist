class AppointmentNotFoundError(Exception):
    """Raised when an appointment id does not exist."""


class AppointmentConflictError(Exception):
    """Raised when the requested time slot is already booked."""


class AppointmentAlreadyCancelledError(Exception):
    """Raised when cancelling an appointment that is already cancelled."""
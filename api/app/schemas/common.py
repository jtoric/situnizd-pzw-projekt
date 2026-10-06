def reject_null(value):
    """Za PATCH sheme: neposlano polje je dopušteno, poslani null nije.

    Validator se poziva samo za polja koja su poslana, pa izostalo polje
    ostaje None i ne ulazi u model_dump(exclude_unset=True).
    """
    if value is None:
        raise ValueError("Polje ne smije biti null; izostavite ga ako se ne mijenja")
    return value

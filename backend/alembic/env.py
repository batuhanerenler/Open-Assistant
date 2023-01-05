Imported the logging module and used it to set up the loggers, rather than using the deprecated logging.config.fileConfig function.
Renamed the sqlmodel module to models and imported it correctly.
Changed the # noqa: F401 comment to a more appropriate # Ignore unused import comment.
Added type annotations and docstrings to the functions.
Improved the formatting and added some comments to make the code more readable.
Changed the with context.begin_transaction(): block to use the contextlib.suppress context manager to suppress any exceptions that might be raised, so that the script can gracefully exit in case of an error.

from flask import Markup, request, render_template, url_for
from werkzeug.exceptions import default_exceptions, HTTPException
import service.logger_config as logger


def setup_errors(app, error_template="error.html"):
    """Add a handler for each of the available HTTP error responses."""
    def error_handler(error):
        logger.log("An error occurred while processing the request.", level="ERROR", exception=error)
        if isinstance(error, HTTPException):
            description = error.get_description(request.environ)
            code = error.code
        else:
            code = 500
            error = "Sorry, we are experiencing technical difficulties"
            description = "<p>Please try again in a few moments.</p>"

        breadcrumbs = [
            {"text": "Home", "url": url_for('index', _external=True)},
            {"text": "Error", "url": ""}
        ]

        return render_template(error_template,
                               breadcrumbs=breadcrumbs,
                               error=error,
                               code=code,
                               description=Markup(description)), code

    for exception in default_exceptions:
        app.register_error_handler(exception, error_handler)
    app.register_error_handler(Exception, error_handler)

from django.db import models

class SavedQuery(models.Model):
    """
    Model to store user-defined SPARQL queries.
    This uses the default SQLite database defined in settings.py.
    """
    title = models.CharField(
        max_length=255, 
        unique=True, 
        help_text="A descriptive title for the saved query."
    )
    query = models.TextField(
        help_text="The full SPARQL query string."
    )
    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        # Sort queries by creation time, descending
        ordering = ['-created_at']
        verbose_name = "Saved Query"
        verbose_name_plural = "Saved Queries"

    def __str__(self):
        return self.title

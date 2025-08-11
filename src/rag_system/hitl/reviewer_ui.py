
class ReviewerUI:
    """
    A simple UI for human reviewers.
    This is a placeholder implementation.
    """
    def __init__(self):
        pass

    def display(self, item: dict):
        """Displays an item for review."""
        print("--- HUMAN REVIEW --- ")
        print(f"Title: {item['title']}")
        print(f"Message: {item['message']}")
        print("--------------------")

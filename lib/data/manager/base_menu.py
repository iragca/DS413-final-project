from abc import ABC, abstractmethod


class BaseMenu(ABC):
    def __init__(self, parent_breadcrumbs: list[str] = []) -> None:
        self.breadcrumb_path: list[str] = parent_breadcrumbs + [self.name]

    @property
    @abstractmethod
    def name(self) -> str:
        """Override this property to set the menu name."""
        pass

    @property
    def breadcrumbs(self) -> str:
        return " > ".join(self.breadcrumb_path)

    @abstractmethod
    def menu(self) -> None:
        """Override this method to implement the menu logic."""
        pass

    def __call__(self) -> None:
        self.menu()

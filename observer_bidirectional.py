import observer_hotfix  # noqa: F401

from observer_complete import ObserverCompleteApp


# Preserve the historical public launcher name while routing to the completed app.
BidirectionalObserverApp = ObserverCompleteApp


if __name__ == "__main__":
    ObserverCompleteApp().mainloop()

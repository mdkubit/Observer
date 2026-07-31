from observer_complete import ObserverCompleteApp


# Preserve the historical public launcher name while routing to the completed app.
BidirectionalObserverApp = ObserverCompleteApp


if __name__ == "__main__":
    ObserverCompleteApp().mainloop()

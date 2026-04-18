# Quiz Master GUI Prototype

GUI prototype of the Quiz Master app. This branch is a Python Tkinter skeleton for the app with little to no functionality.
The prototype is used purely for designing UI, not logic. **Keep prototype files as simple as possible, focusing mainly on UI/UX.**

To run all screens in canonical order, run `allscreens.cmd`, and close the current window to progress to the next screen.

## Notes from Prototype Testing

- In development, prefix `[SERVER]` or `[CLIENT]` to the window title bar for respective UIs. Remove for production.
- In the prototype, treeviews have hardcoded default data. Remove during actual development.
- Test ALL window sizes when modifying UI, including in-betweens. Mainly, minimum size is 800x600, default is 1000x600, and maximized is generally about 1920x1080, depending on display.

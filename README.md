# Quiz Master GUI Prototype

**You must run Python files like this: `python -m folder.file`!!!**

GUI prototype of the Quiz Master app. This branch is a Python Tkinter skeleton for the app with little to no functionality.
The prototype is used purely for designing UI, not logic. **Keep prototype files as simple as possible, focusing mainly on UI/UX.**

To run all screens in canonical order, run `allscreens.cmd`, and close the current window to progress to the next screen.

## Style Guide

For consistency, all windows MUST follow the style guide, unless there are exceptions listed.

### Base Window Structure

Every screen must follow this pattern, with the exact window geometry and padding:

```py
self.root = tk.Tk()
self.root.title("Quiz Master — <Screen Name>")
self.root.geometry(WINDOW_GEOMETRY)
self.root.minsize(WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT)

self.frame = ttk.Frame(self.root, padding=40)
self.frame.grid(row=0, column=0, sticky="nsew")

self.root.columnconfigure(0, weight=1)
self.root.rowconfigure(0, weight=1)
```

Rules:

- Only one root window per file (later, only one root window in the app)
- Only one main frame (`self.frame`)
- Never place widgets directly on `root`

_Note: This will be a mostly redundant rule during development, as all windows will be under one `root`._

### Layout System Rules

The layout within windows should always use `grid()`, not `pack()` or `place()`, unless the window is inheritely
simple, such as `client/disconnect.py` or `common/loading.py`, where `pack()` may be used to reduce complexity in centering.

Standard layout regions should use consistent zones:

| Zone         | Purpose                 |
| ------------ | ----------------------- |
| Top-left     | Title / question number |
| Top-right    | Timer / status          |
| Center       | Main content            |
| Bottom-left  | Status text             |
| Bottom-right | Action buttons          |

### Typography System

All fonts must be **Segoe UI**.

Font sizes and styles should follow this guide:

| Use             | Font (size, style) |
| --------------- | ------------------ |
| Main title      | 28, bold           |
| Section headers | 20-24, bold        |
| Descriptions    | 10-12, italic      |
| Body text       | 14-16              |
| Small text      | 8-10               |

For buttons, there should be three main sizes: large, medium, and small.

| Type   | Font (size) |
| ------ | ----------- |
| Large  | 14-16       |
| Medium | 12          |
| Small  | 8-10        |

### Colors

Do not hardcode color values in UI files. All colors must be defined in `constants.py`.

| Name         | Hex Code | Usage                          |
| ------------ | -------- | ------------------------------ |
| Success      | #196B24  | Correct answers, positive text |
| Error        | #C00000  | Incorrect answers, errors      |
| Red          | #E74C3C  | Answer option A                |
| Blue         | #3498DB  | Answer option B                |
| Yellow       | #F1C40F  | Answer option C                |
| Green        | #2ECC71  | Answer option D                |
| Gray         | #A7A7A7  | Muted text                     |
| Dark Gray    | #6E6E6E  | Subtle/secondary text          |
| Almost Black | #2E2E2E  | High-emphasis neutral text     |
| Gold         | #D4AF37  | 1st place / winner             |
| Silver       | #B0B0B0  | 2nd place                      |
| Bronze       | #CD7F32  | 3rd place                      |

Colors like Red, Blue, Yellow, and Green are reserved for answer options only.
Do not reuse these colors for general UI elements.

### Spacing

Use consistent spacing values throughout the UI:

- Large sections: 40px
- Medium spacing: 20px
- Small spacing: 5–10px

Avoid arbitrary padding values.

### Ttk Style Naming Conventions

When defining a ttk Style in the style database using `style.configure()`, follow the naming convention of:

```
<Type>.<Variant>
```

Only use styles for conventional styles, for example, an error style or a muted style.

Due to Tkinter limitations, to customize widgets like buttons, you must always define a style.

**Where possible, always use ttk widgets!** Only if the widget does not exist in ttk (like `tk.Text`),
or more customization is required that ttk is inconsistent with (like `tk.Button`) should tk widgets be used.
When using tk widgets you should try to customize it as much as possible to make it more modern-looking.

#### Recommended Structure

Labels:

- `Title.TLabel`
- `Header.TLabel`
- `Subheader.TLabel`
- `Body.TLabel`
- `Muted.TLabel`
- `Subtle.TLabel`
- `Success.TLabel`
- `Error.TLabel`
- `Question.TLabel`
- `AnswerA.TLabel`
- `AnswerB.TLabel`
- `AnswerC.TLabel`
- `AnswerD.TLabel`

Buttons:

- `Large.TButton`
- `Medium.TButton`
- `Small.TButton`

Treeview:

- `Treeview`
- `Treeview.Heading`

## Notes from Prototype Testing

- In development, prefix `[SERVER]` or `[CLIENT]` to the window title bar for respective UIs. Remove for production.
- In the prototype, treeviews have hardcoded default data. Remove during actual development.
- Test ALL window sizes when modifying UI, including in-betweens. Mainly, minimum size is 800x600, default is 1000x600, and maximized is generally about 1920x1080, depending on display.

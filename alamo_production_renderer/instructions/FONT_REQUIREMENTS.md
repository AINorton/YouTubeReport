# Font Requirements

The renderer uses strict approved-font mode. It must not silently fall back to DejaVu Sans, Arial, or Pillow's default font because that changes text width and visual appearance.

## Current approved working font

The current working font is **Lato** because the Base True report appears Lato-like. If Alamo confirms a different brand/report font, replace the paths in `alamo_snapshot/config.py` with the approved font paths.

## Required local font files

The renderer checks the project-local `fonts/` folder first:

```text
fonts/Lato-Regular.ttf
fonts/Lato-Medium.ttf
fonts/Lato-Semibold.ttf
fonts/Lato-Bold.ttf
fonts/Lato-Heavy.ttf
fonts/Lato-Italic.ttf
fonts/Lato-SemiboldItalic.ttf
```

If the target environment already has Lato installed system-wide, that may work too, but relying on system fonts is less repeatable.

## Setup in Claude / server environment

Run this once after extracting the project:

```bash
python scripts/download_lato_fonts.py
python scripts/verify_fonts.py
```

Then run the report renderer.

## Important

Do not use a Google Fonts CSS import for this Python/Pillow PDF renderer. CSS imports only help browser/HTML output. This renderer needs actual `.ttf` files available on disk.

If fonts are missing, the renderer should stop with an error instead of producing a visually incorrect client report.

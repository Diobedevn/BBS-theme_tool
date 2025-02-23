# BBS Theme Tool

## Overview

The BBS Theme Tool is a graphical user interface (GUI) application built with Python and Tkinter. It allows users to easily manage themes for BBS Mod by providing functionalities to import and export theme configurations.

## Features

*   **Theme Import:**  Applies a selected theme to the BBS configuration by updating color settings in `bbs.json` and copying asset files (background and icons).
*   **Theme Export:** Creates a new theme folder with a configuration file (`config.txt`) containing the current color settings extracted from `bbs.json`.
*   **Browse for Config Path:**  Provides a file dialog to easily select the root directory of the BBS configuration.
*   **Searchable Theme List:** Displays a list of available themes with a search bar for quick filtering.
*   **Customizable UI:**  Uses custom fonts and icons for a visually appealing user experience.
*   **Error Handling:** Implements robust error handling with informative message boxes to guide the user.

## Prerequisites

Before running the BBS Theme Tool, ensure you have the following installed:

*   **Python 3.x:**  Download from [python.org](https://www.python.org/downloads/).
*   **Pillow (PIL):**  Install using pip:

    ```
    pip install pillow
    ```

## Installation

1.  **Clone the repository:**

    ```
    git clone [your repository link]
    cd [your repository directory]
    ```

2.  **Install dependencies (if any are listed in a `requirements.txt`):**

    ```
    pip install -r requirements.txt
    ```

## Usage

1.  **Prepare Assets:** Ensure the following files are present in the `assets` folder:

    *   `font.ttf` (optional: a custom font file)
    *   `myicon.png` (application icon)
    *   `checkbox_check.png` (checked checkbox image)
    *   `checkbox_nocheck.png` (unchecked checkbox image)
    *   `reload.png` (reload icon)

2.  **Run the application:**

    ```
    python theme.py
    ```

3.  **Using the Interface:**

    *   Click the "Browse" button to select the root directory of your BBS configuration (the directory containing the `bbs` folder).
    *   Select either "Import" or "Export" mode by clicking the corresponding checkbox.
    *   **Import Mode:**  Select a theme from the list and click "Execute" to apply it.
    *   **Export Mode:** Enter a name for the new theme and click "Execute" to create a new theme based on the current configuration.
    *   Use the search bar to filter themes in Import mode.
    *   Click the reload icon to refresh the theme list.

## Directory Structure

The application expects a specific directory structure within the selected config path:


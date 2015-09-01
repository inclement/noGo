# RecycleView

RecycleView is a Kivy widget that want to replace the current ListView. The goal is to have an API that is easy to use, understand, and works within Kv.

This widget is under heavy work and API is still uncertain. Don't use unless you like experimentation.

## Concepts

- **Data**: List of dictionary containing the data you want to display.
- **View**: Widget instance used to display a data entry
- **Viewclass**: Widget class used to create a **View**

## Features

- pre-calculate the container size and views positions to reduce calculation when scrolled.
- create views on the fly, only the one needed to fill the displayed area
- remove hidden views
- recycle hidden views instead of creating new one when possible

## Examples

See the contacts demo:

    export PYTHONPATH=$PWD:$PYTHONPATH
    python examples/contacts/main.py

Or the wallimage demo:

    export PYTHONPATH=$PWD:$PYTHONPATH
    python examples/wallimage/main.py

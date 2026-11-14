from collections.abc import Sequence

import streamlit as st

from attributes import ATTRIBUTES, Attribute


def require_choice[T](choice: T | None) -> T:
    if choice is None:
        raise ValueError("A choice widget was given no options.")

    return choice


def select_attribute(label: str, *, default: Attribute = ATTRIBUTES[0]) -> Attribute:
    choice = st.selectbox(
        label,
        ATTRIBUTES,
        index=ATTRIBUTES.index(default),
        format_func=lambda attribute: attribute.label
    )

    return require_choice(choice)


def choose_option[T](label: str, options: Sequence[T]) -> T:
    choice = st.radio(label, options, horizontal=True)
    return require_choice(choice)

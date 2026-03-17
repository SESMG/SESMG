import streamlit as st
import program_files.GUI_st.GUI_st_global_functions as GUI_functions
import program_files.GUI_st.i18n as i18n

# --- Page Configuration ---
GUI_functions.st_settings_global()


def on_language_change():
    """Triggered automatically when the user selects a different language."""
    i18n.set_active_language(st.session_state.language_selector)


# --- UI Content ---
st.header(i18n.t("language_settings_header"))

# Initialize language if not set
active_lang = i18n.get_active_language()

st.selectbox(
    i18n.t("select_language_label"),
    options=list(i18n.LANGUAGES.keys()),
    format_func=lambda x: i18n.LANGUAGES[x],
    index=list(i18n.LANGUAGES.keys()).index(active_lang),
    key="language_selector",
    on_change=on_language_change
)

st.success(i18n.t("language_success_msg", lang=active_lang.upper()))


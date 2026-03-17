import os
import streamlit as st
import program_files.GUI_st.GUI_st_global_functions as GUI_functions
import json

# Available languages metadata
LANGUAGES = {
    "en": "English",
    "de": "Deutsch"
}

DEFAULT_LANGUAGE = "en"

# Translation dictionary (will be initialized from JSON files)
TRANSLATIONS = {}

def load_translations(new_translations: dict):
    """
    Merges a dictionary of translations into the existing TRANSLATIONS map.
    The input should follow the structure: {"en": {"key": "val"}, "de": {"key": "val"}}
    """
    for lang, labels in new_translations.items():
        if lang not in TRANSLATIONS:
            TRANSLATIONS[lang] = {}
        TRANSLATIONS[lang].update(labels)

def _init_translations():
    """
    Loads translation files from the locales directory based on defined LANGUAGES.
    """
    current_dir = os.path.dirname(__file__)
    locales_dir = os.path.join(current_dir, "locales")
    
    if os.path.exists(locales_dir):
        for lang_code in LANGUAGES.keys():
            filename = f"{lang_code}.json"
            file_path = os.path.join(locales_dir, filename)
            if os.path.exists(file_path):
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        labels = json.load(f)
                        load_translations({lang_code: labels})
                except Exception as e:
                    print(f"I18N: Could not load {filename}: {e}")

# Initialize translations on module load
_init_translations()


def get_active_language() -> str:
    """
    Returns the currently active language shortcode from session state.
    Initializes from cache if not already set.
    """
    if "language" not in st.session_state:
        internal_directory_path = GUI_functions.set_internal_directory_path()
        path_to_cache_json = os.path.join(internal_directory_path, 'GUI_st_cache.json')
        settings_cache = GUI_functions.import_GUI_input_values_json(path_to_cache_json)
        st.session_state.language = settings_cache.get("language", DEFAULT_LANGUAGE)
    return st.session_state.language


def set_active_language(lang_code: str):
    """
    Sets the active language in session state and persists it to the cache.
    """
    if lang_code not in LANGUAGES:
        return

    st.session_state.language = lang_code
    
    # Persist to cache
    internal_directory_path = GUI_functions.set_internal_directory_path()
    path_to_cache_json = os.path.join(internal_directory_path, 'GUI_st_cache.json')
    settings_cache = GUI_functions.import_GUI_input_values_json(path_to_cache_json)
    settings_cache["language"] = lang_code
    GUI_functions.save_GUI_cache_dict(settings_cache, path_to_cache_json)


def t(label: str, **kwargs) -> str:
    """
    Helper function to get the translation for a given label.
    Supports placeholders via kwargs (e.g. t("welcome", name="User")).
    Returns the label itself if no translation is found in active or default language.
    """
    lang = get_active_language()
    
    # Get translation from active language, fallback to default
    text = TRANSLATIONS.get(lang, {}).get(label)
    if text is None:
        text = TRANSLATIONS.get(DEFAULT_LANGUAGE, {}).get(label, label)
    
    # Apply formatting if kwargs are provided
    if kwargs:
        try:
            return text.format(**kwargs)
        except (KeyError, IndexError, ValueError):
            return text
            
    return text

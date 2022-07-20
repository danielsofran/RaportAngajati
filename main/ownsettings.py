from dynamic_preferences.types import BooleanPreference, StringPreference, IntegerPreference
from dynamic_preferences.preferences import Section
from dynamic_preferences.registries import global_preferences_registry

general = Section('general')

@global_preferences_registry.register
class NrRecalcPoz(IntegerPreference):
    section = general
    name = "Numarul de relocari per utilizator"
    default = 3

@global_preferences_registry.register
class SecAfterRecalc(IntegerPreference):
    section = general
    name = "Numarul de secunde asteptate pana la urmatoarea relocare"
    default = 60
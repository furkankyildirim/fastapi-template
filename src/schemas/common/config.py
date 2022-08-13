from pydantic import Extra


class ExtraFieldsAllowedConfig:
    extra = Extra.allow
    allow_population_by_field_name = True
    by_aliase = True
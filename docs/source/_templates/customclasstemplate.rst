{{ fullname | escape | underline}}



.. currentmodule:: {{ module }}


{% if methods %}
.. rubric:: {{ _('Methods') }}

.. autosummary::
{% for item in methods %}
    ~{{ name }}.{{ item }}
{%- endfor %}
{% endif %}


{% if attributes %}
.. rubric:: {{ _('Attributes') }}

.. autosummary::
{% for item in attributes %}
    ~{{ name }}.{{ item }}
{%- endfor %}
{% endif %}


.. autoclass:: {{ module }}.{{ objname }}
    :members:
   
    
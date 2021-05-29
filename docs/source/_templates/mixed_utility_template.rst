{{ fullname | escape | underline}}



.. currentmodule:: {{ module }}


{% if methods %}
.. rubric:: {{ _('Methods') }}

.. autosummary::
{% for item in methods %}
   {% if item != '__init__' and not in inherited_members %} 
        ~{{ name }}.{{ item }}
    {% endif %}
{%- endfor %}
{% endif %}


{% if attributes %}
.. rubric:: {{ _('Attributes') }}

.. autosummary::
{% for item in attributes %}
   { % if item not in inherited_members % }
      ~{{ name }}.{{ item }}
{%- endfor %}
{% endif %}


{% if methods %}
.. autoclass:: {{ module }}.{{ objname }}
   :members:
{% else %}
.. autofunction:: {{ module }}.{{ objname }}
{% endif}
   
    
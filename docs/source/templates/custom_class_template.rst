{{ fullname | escape | underline}}

.. currentmodule:: {{ module }}


.. autoclass:: {{ module }}.{{ objname }}
    :members:

Summary
-------


{% if methods %}
.. rubric:: {{ _('Methods') }}

.. autosummary::
{% for item in methods %}
    {% if item != '__init__' %} 
        ~{{ name }}.{{ item }}
    {% endif %}
{%- endfor %}
{% endif %}


{% if attributes %}
.. rubric:: {{ _('Attributes') }}

.. autosummary::
{% for item in attributes %}
    ~{{ name }}.{{ item }}
{%- endfor %}
{% endif %}
   
    
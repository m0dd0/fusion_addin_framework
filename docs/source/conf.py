# TROUBLESHOOTINNG

# To use autodoc the module must be importable.
# Therefore it must be installed to the python instanve which executes sphinx.
# By default this is the standard python instance.
# To execute sphix from a virtual env in which faf is installed to, sphix must be
# installed within this environment.
# requirements_docs.txt gives contains all the dependencies (the framework repo,
# sphinx itself and the rtd theme) that are needed in the environment to succesfully
# run the doc generation.

# If you change something in the addin code you must pip install the package agein
# to the virtual environment

# Using import from other modeules (for typehint etc.) is likely to cause a circular
# import error regardless of the module which is documented
# Also the error message will likely by misleading.
# https://www.stefaanlippens.net/circular-imports-type-hints-python.html

# Use the make clean command from time to time.

# The docstrings are contained in the documentation via the autosummary extension.
# By default the autosummary extenasion produces only a summarizing table about
# the elements of the passed elements.
# However, if you provide a :toctree: flag and a :template: you can incorporate
# any kind of docstring in a certain order/format etc. by modifying the template
# and includein autoclass etc. in the template.
# The templates are saved in the _templates directory.

# Configuration file for the Sphinx documentation builder.
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------
# import sys, os
# import fusion_addin_framework
# sys.path.insert(0, os.path.abspath("../../fusion_addin_framework/utils"))

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.

# -- Project information -----------------------------------------------------
project = "Fusion Addin Framework"
copyright = "2021, Moritz Hesche"  # pylint:disable=redefined-builtin
author = "Moritz Hesche"

# The full version, including alpha/beta/rc tags
# release = "0.2.0" # this should be determined by the vcs tags


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = ["sphinx.ext.autodoc", "sphinx.ext.napoleon", "sphinx.ext.autosummary"]

# Add any paths that contain templates here, relative to this directory.
templates_path = ["templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
html_theme = "sphinx_rtd_theme"

html_theme_options = {
    # "analytics_id": "UA-XXXXXXX-1",  #  Provided by Google in your dashboard
    # "analytics_anonymize_ip": False,
    # "logo_only": False,
    # "display_version": True,
    # "prev_next_buttons_location": "bottom",
    # "style_external_links": False,
    # "vcs_pageview_mode": "",
    # "style_nav_header_background": "white",
    # # Toc options
    # "collapse_navigation": False,
    # "sticky_navigation": True,
    "navigation_depth": 3,
    # "includehidden": True,
    # "titles_only": False,
}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = []

autodoc_mock_imports = ["adsk"]

autodoc_member_order = "bysource"
autoclass_content = "both"
autosummary_generate = True

# Napoleon settings
napoleon_google_docstring = True
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = False
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_examples = False
napoleon_use_admonition_for_notes = False
napoleon_use_admonition_for_references = False
napoleon_use_ivar = False
napoleon_use_param = True
napoleon_use_rtype = True
napoleon_type_aliases = None
napoleon_attr_annotations = True

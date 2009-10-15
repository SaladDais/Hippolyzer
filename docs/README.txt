This checkout contains the most recently complied version of the documentation in docs/html/.

To rebuild the sphinx doc set:

Get sphinx!!!

Either use your virtualenv, or your native python install and run: 
    easy_install -U Sphinx

Then, from the docs dir:

1. python refresh.py

refresh.py stages the sphinx .rst files, and then runs 'sphinx-build -a -c source/configure/' source/ html/

The docs/html/ directory will contain the fully compiled documentation set.
Please check in updated docs if you add functionality.
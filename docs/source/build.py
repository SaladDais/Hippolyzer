import os, sys
import re
import pyclbr

module_file_ext = ".rst"

modules_dir = os.path.join(os.path.dirname(__file__) + '/modules/')
unit_test_dir = os.path.join(os.path.dirname(__file__) + '/unittest/')
eggs_dir = os.path.join(os.path.dirname(__file__) + '/../../../../eggs/')
lib_dir = os.path.abspath(os.path.dirname(__file__) + '/../../')

# skip files in processing docs
skipfiles = ['build_packet_templates.py']

if not os.path.isdir(modules_dir):
    print "Creating modules directory: %s" % (modules_dir)
    os.mkdir(modules_dir)

if not os.path.isdir(unit_test_dir):
    print "Creating unit test modules directory: %s" % (unit_test_dir)
    os.mkdir(unit_test_dir)

sys.path.append(lib_dir)

for directory in os.listdir(eggs_dir):
    sys.path.append(os.path.join(eggs_dir + directory))

mock = 0

def remove(mock, dirname, fnames):

    if not re.search("/.svn", dirname):

        for fname in fnames:
            if not re.search(".svn", fname):
                print "  Removing " + os.path.join(dirname, fname)
                os.remove(os.path.join(dirname, fname))

                mock += 1

print "Cleaning the sources/modules dir..."

# remove .rst files in source/modules
os.path.walk(modules_dir, remove, mock)

print "Cleaning the sources/unittest dir..."

# remove .rst files in source/unittest
os.path.walk(unit_test_dir, remove, mock)

print "Removed %s module files" % (mock)

store = {}

def callback(store, dirname, fnames):

    keepers = []

    if not re.search("/.svn", dirname):

        for f in fnames:
            if (re.search(".py$", f) or re.search(".txt$", f)) and not re.search("__init_", f) and not f in skipfiles:
                keepers.append(f)

        store[dirname] = keepers

# look for .py files in pyogp.lib.base
os.path.walk(os.path.abspath(os.path.dirname(__file__) + '/../../pyogp/lib/base/'), callback, store)

def get_handle(_dir, fname):

    f = open(os.path.join(_dir, fname), 'w')

    print "  Writing %s" % (fname)

    return f

def close_handle(handle):

    handle.close()

def write_rst(handle, params, header = ''):

    package_root = params[0]    # is the root path + directory
    module = params[1]          # is the full package path
    mod_name = params[2]        # is the name of the directory within pyogp.lib.base
    fname = params[3]           # is the root name of the .py file
    mod_ext = params[4]         # extension of the source file

    if header != '':
        handle.write(header + "\n")

    if mod_ext == "txt":

        title = mod_name

        handle.write(title + "\n")
        handle.write("=" * len(title) + "\n")
        handle.write("\n")

        handle.write("\n")
        handle.write(".. module:: " + module + "\n")
        handle.write("\n")

        handle.write("This is a doctest, the content here is verbatim from the source file at %s.\n" % (module + "." + mod_ext))
        handle.write("\n")

        source_handle = open(os.path.join(lib_dir, "/".join(module.split(".")) + "." + mod_ext))

        for line in source_handle.readlines():
            handle.write(line)
        
        
        # this is a doctest
    else:

        title = ":mod:`" + mod_name + "`"

        handle.write(title + "\n")
        handle.write("=" * len(title) + "\n")

        handle.write("\n")
        handle.write(".. automodule:: " + module + "\n")
        handle.write("\n")

        for k in pyclbr.readmodule(module):

            # hack to workaround something i cant reckon
            if module == 'pyogp.lib.base.groups' and k in ['UUID', 'Vector3', 'Quaternion']:
                continue

            print "    adding %s" % (k)

            handle.write(".. autoclass:: " + module + "." + k + "\n")
            handle.write("  :members:" + "\n")
            handle.write("  :undoc-members:" + "\n")
            if not re.search("test_", mod_name):
                handle.write("  :inherited-members:" + "\n")
            handle.write("" + "\n")

print "Building modules files..."

unit_tests = []

for k in store:

    offset = len(os.path.abspath(os.path.dirname(__file__) + '/../..').split("/"))

    package_root = '.'.join(k.split("/")[offset:])

    for fname in store[k]:

        mod_name = fname.split(".")[0]
        mod_ext = fname.split(".")[1]

        if package_root == "pyogp.lib.base.":
            module = package_root + mod_name
        else:
            module = package_root + "." + mod_name

        fname = mod_name + module_file_ext

        # skip the sample implementation scripts
        if re.search("sample", mod_name) and re.search("pyogp.lib.base.examples", package_root):
            continue

        # handle unit tests separately
        if re.search("test", mod_name) or re.search("test", package_root):
            unit_tests.append((package_root, module, mod_name, fname, mod_ext))
            continue

        handle = get_handle(modules_dir, fname)

        write_rst(handle, (package_root, module, mod_name, fname, mod_ext))

        close_handle(handle)

print "Building unit test module..."

for params in unit_tests:

    handle = get_handle(unit_test_dir, params[3])

    write_rst(handle, params)

    close_handle(handle)


Experimental glue specviz plugin
================================

[![Build Status](https://travis-ci.org/glue-viz/glue-wwt.svg)](https://travis-ci.org/glue-viz/glue-wwt?branch=master)
[![Build status](https://ci.appveyor.com/api/projects/status/1gov2vtuesjnij69/branch/master?svg=true)](https://ci.appveyor.com/project/astrofrog/glue-wwt/branch/master)

This is an experimental glue plugin that allows
[specviz](https://github.com/spacetelescope/specviz) to be used inside glue.

Requirements
------------

Note that this plugin requires [glue](http://glueviz.org/) to be installed -
see [this page](http://glueviz.org/en/latest/installation.html) for
instructions on installing glue.

Installing
----------

To install the latest stable version of the plugin, you can do:

    pip install glue-specviz
    
or you can install the latest developer version from the git repository using:

    pip install https://github.com/glue-viz/glue-specviz/archive/master.zip

This will auto-register the plugin with Glue. Now simply start up Glue, open a
tabular dataset, drag it onto the main canvas, then select 'SpecViz viewer'.

Testing
-------

To run the tests, do:

    py.test glue_specviz

at the root of the repository. This requires the [pytest](http://pytest.org)
module to be installed.

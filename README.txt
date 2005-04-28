Zelenium Product README

  Overview

    This product allows developers to create TTW Selenium test suites
    inside their Zope instance, in order to do browser-based functional
    testing of their site.


  Installing the Product

    1. Unpack the tarball in a temporary location.

    2. Copy or move the 'Zelenium' directory to the 'Products' directory
       of your INSTANCE_HOME.

    3. Restart Zope.


  Using Zelenium

    You can add a 'Zuite' object at any location within your Zope
    site.  It behaves as a standard ordered folder, with a couple of 
    differences:

      - It's 'index_html' is the "TestRunner.html" view familiar
        from Selenium.

      - It derives the test suite (in the upper left corner iframe)
        from all OFS.Image.File objects whose names start with 'test'.
        You can use the OrderedFolder support to modify the order in
        which the test case files are run.

      - It provides a "Zip" action, which allows you to export the
        test suite, all test cases, and the supporting Selenium
        Javascript / CSS files as a single, self-contained zipfile.


  Adding Tests

    Tests are just 'File' instances whose names begin with 'test'.
    They should have a content type of 'text/html', and should contain
    a table which defines the steps which make up the test case.

    See http://selenium.thoughtworks.com/testrunner.html for documentation
    on the table structure and the Selenese language.


  Using Additional Metatypes as Test Cases

    On the "Properties" tab of your test suite, you can add / modify
    the list of meta_types which the suite will allow as test cases.
    Adding "Script (Python)", for instance, allows you to define
    test cases in PythonScripts.


  Nesting Test Suites

    Each test suite automatically includes the test cases of any
    suite it contains.  You can take advantage of this feature to
    organize your test cases in a hierarchy, running them in separate
    segments, or all at once.


  Exporting an Archive

    On the "Zip" tab, supply a filename and click the "Download" button.
    The Zuite object will construct a zip file with the following
    contents:

      'index.html' -- the "TestRunner.html" framework page

      'TestSuite.html' -- the list of test case files (rendered as
        static HTML)

      'test*" -- your test case files (appending '.html' if the IDs
        do not have extensions)

      Each of the supporting '.js' and '.css' files which drive the
      browserbot.


  Creating a Snapshot

    On the "Zip" tab, supply a filename and click the "Download" button.
    The Zuite object will construct a zip file with the same contents
    described above, and then save it as a File object in its own contents.


  Generating Testcases using tcpwatch

    1. Download the 'tcpwatch' product from Shane Hathaway's site:

       http://hathawaymix.org/Software/TCPWatch

    2. Unpack and run tcpwatch in its "HTTP proxy" mode, with recoring
       turned on.  E.g., the following command runs the proxy on
       port 9999, recording the request / response data to the directory
       '/tmp/recorded_scenario'::

        $ python /path/to/tcpwatch/ tcpwatch.py \
            -p 9999 -r /tmp/recorded_scenario 

    3. Configure your browser to use an HTTP proxy on localhost, port 9999.

    4. Click through your site, exercising the features you are testing.

    5. Stop the proxy.  Run the 'generator.py' script, pointing to the
       directory where tcpwatch was recording::

        $ python /path/to/Zelenium/generator.py \
           --logfile-directory=/tmp/recorded_scenario \
           --output-file=test_case_name.html

    6. Edit the generated test case, removing / correcting the various
       steps.

    7. Upload the test case to a Zelenium Zuite and run it.


  Capturing Results from the Test Run

    Selenium has a feature which allows the testrunner to upload
    result data from an automated test run to the server.  To enable
    this feature in Zope, add a PythonScript, 'postResults', in the
    root of your site, with text similar to::

      context.test_suite.postResults(context.REQUEST)

    Invoke the test suite from your browser as usual, but append the
    query string '?auto=1', to the URL, e.g.::

      http://localhost:8080/test_suite?auto=1

    Selenium will run all test cases, and then upload its result data
    to the '/postResults' URL (your PythonScript).

    Note:  if running Zope behind Apache or another rewriting proxy, 
    you may be able to skip adding a PythonScript, and instead rewrite
    '/postResults' directly onto the 'postResults' method of your
    test suite.


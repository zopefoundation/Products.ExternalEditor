""" External Editor Plugins """

def importAll():
    # Assert plugin dependancies for py2exe
    # All plugins must be imported here to be distributed
    # in the Windows binary package!
    import homesite, homesite5
    import photoshop, photoshp
    import word, winword
    import excel
    import powerpoint, powerpnt
    import msohtmed
    import dreamweaver

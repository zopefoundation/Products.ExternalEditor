

def fix_cmf_permissions(self):
    '''
    Changes the permissions on each member folder to normal settings.
    '''
    count = 0
    m = self.Members
    for v in m.objectValues():
        if hasattr(v, '_View_Permission'):
            del v._View_Permission
        if hasattr(v, '_Access_contents_information_Permission'):
            del v._Access_contents_information_Permission
        if v._p_changed:
            count = count + 1
    return 'Changed permissions on %d objects.' % count

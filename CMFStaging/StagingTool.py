##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
##############################################################################
"""Staging Tool

Uses a version repository to implement staging.

$Id$
"""

from Acquisition import aq_inner, aq_parent, aq_acquire
from OFS.SimpleItem import SimpleItem
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo

from Products.CMFCore.utils import UniqueObject, getToolByName
from Products.CMFCore.CMFCorePermissions import ManagePortal

# Permission name
StageObjects = 'Use version control'


class StagingError (Exception):
    """Error while attempting to stage an object"""


class StagingTool(UniqueObject, SimpleItem):
    __doc__ = __doc__ # copy from module
    id = 'portal_staging'
    meta_type = 'Portal Staging Tool'

    security = ClassSecurityInfo()

    manage_options = ( { 'label' : 'Overview', 'action' : 'manage_overview' }
                     , 
                     ) + SimpleItem.manage_options

    # With auto_unlock_checkin turned on, updateStages() uses the
    # lock tool and the versions tool to unlock and check in the object.
    auto_checkin = 1

    repository_name = 'VersionRepository'

    # _stages maps stage names to relative paths.
    # This should be configurable TTW.
    _stages = {
        'dev':    'Stages/Development',
        'review': 'Stages/Review',
        'prod':   'Stages/Production'
        }

    security.declareProtected(ManagePortal, 'manage_overview' )
    #manage_overview = DTMLFile( 'explainStagingTool', _dtmldir )

    def _getVersionRepository(self):
        repo = aq_acquire(self, self.repository_name, containment=1)
        return repo


    def _getObjectStages(self, object, get_container=0):
        """Returns a mapping from stage name to object in that stage.

        Objects not in a stage are represented as None."""
        root = aq_parent(aq_inner(self))
        stages = {}
        rel_path = None
        ob_path = object.getPhysicalPath()
        for stage_name, path in self._stages.items():
            stage = root.restrictedTraverse(path, None)
            stages[stage_name] = stage
            if stage is not None and object.aq_inContextOf(stage, 1):
                if rel_path is not None:
                    # Can't tell what stage the object is in!
                    raise StagingError, "The stages overlap"
                # The object is from this stage.
                stage_path = stage.getPhysicalPath()
                assert ob_path[:len(stage_path)] == stage_path
                rel_path = ob_path[len(stage_path):]

        if rel_path is None:
            raise StagingError, "Object %s is not in any stage" % (
                '/'.join(ob_path))

        if get_container:
            # Get the container of the object instead of the object itself.
            # To do that, we just traverse to one less path element.
            rel_path = rel_path[:-1]

        res = {}
        for stage_name, path in self._stages.items():
            stage = stages[stage_name]
            object = stage.restrictedTraverse(rel_path, None)
            res[stage_name] = object
        return res


    def _getObjectVersionIds(self, object):
        repo = self._getVersionRepository()
        stages = self._getObjectStages(object)
        res = {}
        for stage_name, object in stages.items():
            if object is None or not repo.isUnderVersionControl(object):
                res[stage_name] = None
            else:
                res[stage_name] = repo.getVersionInfo(object).version_id
        return res


    def _autoCheckin(self, object):
        lt = getToolByName(self, 'portal_lock', None)
        if lt is not None:
            if lt.locked(object):
                lt.unlock(object)
        vt = getToolByName(self, 'portal_versions', None)
        if vt is not None:
            if vt.isCheckedOut(object):
                vt.checkin(object)


    security.declareProtected(StageObjects, 'isStageable')
    def isStageable(self, object):
        """Returns a true value if the object can be staged."""
        repo = self._getVersionRepository()
        return (repo.isAVersionableResource(object) and
                getattr(object, '_stageable', 1))


    security.declareProtected(StageObjects, 'updateStages')
    def updateStages(self, object, from_stage, to_stages):
        """Updates corresponding objects to match the version
        in the specified stage."""
        if from_stage in to_stages or not self._stages.has_key(from_stage):
            raise StagingError, "Invalid from_stages or to_stages parameter."

        repo = self._getVersionRepository()
        container_map = self._getObjectStages(object, get_container=1)

        self._checkContainers(object, to_stages, container_map)
        if self.auto_checkin:
            self._autoCheckin(object)

        object_map = self._getObjectStages(object)
        dev_object = object_map[from_stage]
        version_info = repo.getVersionInfo(dev_object)
        version_id = version_info.version_id
        history_id = version_info.history_id

        # Make sure we copy the current data.
        # XXX ZopeVersionControl tries to do this but isn't quite correct yet.
        get_transaction().commit(1)

        # Update and/or copy the object to the different stages.
        for stage_name, ob in object_map.items():
            if stage_name in to_stages:
                if ob is None:
                    # The object has not yet been created in the stage.
                    # Copy from the repository to the given stage.
                    ob = repo.getVersionOfResource(history_id, version_id)
                    container = container_map.get(stage_name, None)
                    if container is None:
                        # This can happen if a site doesn't yet exist on
                        # the stage.
                        p = '/'.join(dev_object.getPhysicalPath())
                        raise StagingError, (
                            'The container for "%s" does not exist on "%s"'
                            % (p, stage_name))
                    # Make a copy and put it in the new place.
                    # (see CopySupport.manage_pasteObjects())
                    id = dev_object.getId()
                    container._setObject(id, ob)
                else:
                    if not repo.isUnderVersionControl(ob):
                        p = '/'.join(ob.getPhysicalPath())
                        raise StagingError, (
                            'The object "%s", not under version control, '
                            'is in the way.' % p)
                    if repo.getVersionInfo(ob).history_id != history_id:
                        p = '/'.join(ob.getPhysicalPath())
                        p2 = '/'.join(dev_object.getPhysicalPath())
                        raise StagingError, (
                            'The object "%s", backed by a different '
                            'version history than "%s", '
                            'is in the way.' % (p, p2))
                    repo.updateResource(ob, version_id)


    security.declareProtected(StageObjects, 'removeStages')
    def removeStages(self, object, stages):
        """Removes the copies on the given stages."""
        container_map = self._getObjectStages(object, get_container=1)
        id = object.getId()
        for stage_name, container in container_map.items():
            if container is not None and stage_name in stages:
                container._delObject(id)


    security.declareProtected(StageObjects, 'versions')
    def getVersionIds(self, object):
        """Retrieves object version identifiers in the different stages."""
        return self._getObjectVersionIds(object)


    def _checkContainers(self, object, stages, containers):
        for stage in stages:
            if containers.get(stage) is None:
                p = '/'.join(object.getPhysicalPath())
                raise StagingError, (
                    'The container for "%s" does not exist on "%s"'
                    % (p, stage))


    security.declareProtected(StageObjects, 'checkContainers')
    def checkContainers(self, object, stages):
        """Verifies that the container exists for the object on the
        given stages.  If not, an exception is raised.
        """
        containers = self._getObjectStages(object, get_container=1)
        self._checkContainers(object, stages, containers)
        return 1


    security.declareProtected(StageObjects, 'getURLForStage')
    def getURLForStage(self, object, stage, relative=0):
        """Returns the URL of the object on the given stage."""
        stages = self._getObjectStages(object)
        ob = stages[stage]
        if ob is not None:
            return ob.absolute_url(relative)
        else:
            return None


InitializeClass(StagingTool)

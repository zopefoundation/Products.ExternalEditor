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

import os

from Acquisition import aq_inner, aq_parent, aq_acquire
from Globals import InitializeClass, DTMLFile
from AccessControl import ClassSecurityInfo
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

from Products.CMFCore.utils import UniqueObject, getToolByName, \
     SimpleItemWithProperties
from Products.CMFCore.CMFCorePermissions import ManagePortal

# Permission name
StageObjects = 'Use version control'

_wwwdir = os.path.join(os.path.dirname(__file__), 'www') 


class StagingError (Exception):
    """Error while attempting to stage an object"""


class StagingTool(UniqueObject, SimpleItemWithProperties):
    __doc__ = __doc__ # copy from module
    id = 'portal_staging'
    meta_type = 'Portal Staging Tool'

    security = ClassSecurityInfo()

    manage_options = (
        {'label': 'Overview', 'action': 'manage_overview'},
        {'label': 'Stages', 'action': 'manage_stagesForm'},
        ) + SimpleItemWithProperties.manage_options

    # With auto_checkin turned on, updateStages() uses the
    # lock tool and the versions tool to unlock and check in the object.
    auto_checkin = 1

    repository_name = 'VersionRepository'

    _properties = (
        {'id': 'repository_name', 'type': 'string', 'mode': 'w',
         'label': 'ID of the version repository'},
        {'id': 'auto_checkin', 'type': 'boolean', 'mode': 'w',
         'label': 'Unlock and checkin before staging'},
        )

    # _stages maps stage names to relative paths.
    _stages = {
        'dev':    'Stages/Development',
        'review': 'Stages/Review',
        'prod':   'Stages/Production'
        }

    security.declareProtected(ManagePortal, 'manage_overview' )
    manage_overview = DTMLFile('explainStagingTool', _wwwdir)

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
            if stage is not None:
                object = stage.restrictedTraverse(rel_path, None)
            else:
                object = None
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


    def _autoCheckin(self, object, message=''):
        lt = getToolByName(self, 'portal_lock', None)
        if lt is not None:
            if lt.locked(object):
                lt.unlock(object)
        vt = getToolByName(self, 'portal_versions', None)
        if vt is not None:
            if vt.isCheckedOut(object):
                vt.checkin(object, message)


    security.declareProtected(StageObjects, 'isStageable')
    def isStageable(self, object):
        """Returns a true value if the object can be staged."""
        repo = self._getVersionRepository()
        if not repo.isAVersionableResource(object):
            return 0
        if not getattr(object, '_stageable', 1):
            return 0
        # An object is stageable only if it is located in one of the stages.
        root = aq_parent(aq_inner(self))
        for stage_name, path in self._stages.items():
            stage = root.restrictedTraverse(path, None)
            if stage is not None and object.aq_inContextOf(stage, 1):
                return 1
        return 0      


    security.declareProtected(StageObjects, 'getStageOf')
    def getStageOf(self, object):
        """Returns the stage ID the object is in the context of.
        """
        root = aq_parent(aq_inner(self))
        for stage_name, path in self._stages.items():
            stage = root.restrictedTraverse(path, None)
            if stage is not None and object.aq_inContextOf(stage, 1):
                return stage_name
        return None


    security.declareProtected(StageObjects, 'updateStages')
    def updateStages(self, object, from_stage, to_stages, message=''):
        """Updates corresponding objects to match the version
        in the specified stage."""
        if from_stage and (
            from_stage in to_stages or not self._stages.has_key(from_stage)):
            raise StagingError, "Invalid from_stages or to_stages parameter."

        repo = self._getVersionRepository()
        container_map = self._getObjectStages(object, get_container=1)

        self._checkContainers(object, to_stages, container_map)
        if self.auto_checkin:
            self._autoCheckin(object, message)

        object_map = self._getObjectStages(object)
        if from_stage:
            source_object = object_map[from_stage]
        else:
            # The default source stage is the stage where the object is now.
            source_object = object
        version_info = repo.getVersionInfo(source_object)
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
                        p = '/'.join(source_object.getPhysicalPath())
                        raise StagingError, (
                            'The container for "%s" does not exist on "%s"'
                            % (p, stage_name))
                    # Make a copy and put it in the new place.
                    # (see CopySupport.manage_pasteObjects())
                    id = source_object.getId()
                    container._setObject(id, ob)
                else:
                    if not repo.isUnderVersionControl(ob):
                        p = '/'.join(ob.getPhysicalPath())
                        raise StagingError, (
                            'The object "%s", not under version control, '
                            'is in the way.' % p)
                    if repo.getVersionInfo(ob).history_id != history_id:
                        p = '/'.join(ob.getPhysicalPath())
                        p2 = '/'.join(source_object.getPhysicalPath())
                        raise StagingError, (
                            'The object "%s", backed by a different '
                            'version history than "%s", '
                            'is in the way.' % (p, p2))
                    repo.updateResource(ob, version_id)


    security.declareProtected(StageObjects, 'removeStages')
    def removeStages(self, object, stages):
        """Removes the copies on the given stages."""
        object_map = self._getObjectStages(object)
        container_map = self._getObjectStages(object, get_container=1)
        id = object.getId()
        for stage_name, container in container_map.items():
            if object_map.get(stage_name) is not None:
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


    security.declareProtected(ManagePortal, 'manage_stagesForm')
    manage_stagesForm = PageTemplateFile('stagesForm', _wwwdir)


    security.declareProtected(ManagePortal, 'getStagePaths')
    def getStageItems(self):
        lst = self._stages.items()
        lst.sort()
        return lst


    security.declareProtected(ManagePortal, 'manage_editStages')
    def manage_editStages(self, stages=(), RESPONSE=None):
        """Edits the stages."""
        ss = {}
        for stage in stages:
            name = str(stage.name)
            path = str(stage.path)
            if name and path:
                ss[name] = path
        self._stages = ss
        if RESPONSE is not None:
            RESPONSE.redirect(
                '%s/manage_stagesForm?manage_tabs_message=Stages+changed.'
                % self.absolute_url())


InitializeClass(StagingTool)

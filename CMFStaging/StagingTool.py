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

from Acquisition import aq_base, aq_inner, aq_parent, aq_acquire
from Globals import InitializeClass, DTMLFile
from AccessControl import ClassSecurityInfo
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

from Products.CMFCore.utils \
     import UniqueObject, getToolByName, SimpleItemWithProperties
from Products.CMFCore.CMFCorePermissions import ManagePortal

from staging_utils import getPortal, verifyPermission, unproxied
from staging_utils import getProxyTarget, getProxyReference, cloneByPickle


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

    # _stages maps stage names to paths relative to the portal.
    _stages = (
        ('dev',    'Development', '.'),
        ('review', 'Review',      '../Review'),
        ('prod',   'Production',  '../Production'),
        )

    security.declareProtected(ManagePortal, 'manage_overview' )
    manage_overview = DTMLFile('explainStagingTool', _wwwdir)

    def _getVersionRepository(self):
        repo = aq_acquire(self, self.repository_name, containment=1)
        return repo

    def _getStage(self, portal, path):
        if not path or path == ".":
            return portal
        else:
            return portal.restrictedTraverse(path, None)

    def _getObjectStages(self, obj, get_container=0):
        """Returns a mapping from stage name to object in that stage.

        Objects not in a stage are represented as None.
        """
        portal = aq_parent(aq_inner(self))
        stages = {}
        rel_path = None
        ob_path = obj.getPhysicalPath()
        for stage_name, stage_title, path in self._stages:
            stage = self._getStage(portal, path)
            stages[stage_name] = stage
            try:
                obj.aq_inContextOf
            except:
                import pdb; pdb.set_trace()
            if stage is not None and obj.aq_inContextOf(stage, 1):
                if rel_path is not None:
                    # Can't tell what stage the object is in!
                    raise StagingError("The stages overlap")
                # The object is from this stage.
                stage_path = stage.getPhysicalPath()
                assert ob_path[:len(stage_path)] == stage_path
                rel_path = ob_path[len(stage_path):]

        if rel_path is None:
            raise StagingError("Object %s is not in any stage" % (
                '/'.join(ob_path)))

        if get_container:
            # Get the container of the object instead of the object itself.
            # To do that, we just traverse to one less path element.
            rel_path = rel_path[:-1]

        res = {}
        for stage_name, stage_title, path in self._stages:
            stage = stages[stage_name]
            if stage is not None:
                obj = stage.restrictedTraverse(rel_path, None)
            else:
                obj = None
            res[stage_name] = obj
        return res


    def _getObjectVersionIds(self, obj, include_status=0):
        repo = self._getVersionRepository()
        stages = self._getObjectStages(obj)
        res = {}
        for stage_name, obj in stages.items():
            u_obj = unproxied(obj)
            if obj is None or not repo.isUnderVersionControl(u_obj):
                res[stage_name] = None
            else:
                info = repo.getVersionInfo(u_obj)
                v = info.version_id
                if include_status and info.status == info.CHECKED_OUT:
                    v = str(v) + '+'
                res[stage_name] = v
        return res


    def _autoCheckin(self, obj, message=''):
        lt = getToolByName(self, 'portal_lock', None)
        if lt is not None:
            if lt.locked(obj):
                lt.unlock(obj)
        vt = getToolByName(self, 'portal_versions', None)
        if vt is not None:
            if not vt.isUnderVersionControl(obj) or vt.isCheckedOut(obj):
                vt.checkin(obj, message)


    security.declarePublic('isStageable')
    def isStageable(self, obj):
        """Returns a true value if the object can be staged."""
        verifyPermission(StageObjects, obj)
        repo = self._getVersionRepository()
        if not repo.isAVersionableResource(unproxied(obj)):
            return 0
        if not getattr(obj, '_stageable', 1):
            return 0
        # An object is stageable only if it is located in one of the stages.
        portal = aq_parent(aq_inner(self))
        for stage_name, stage_title, path in self._stages:
            stage = self._getStage(portal, path)
            if stage is not None and obj.aq_inContextOf(stage, 1):
                return 1
        return 0


    security.declarePublic('getStageOf')
    def getStageOf(self, obj):
        """Returns the stage name the object is in the context of.
        """
        verifyPermission(StageObjects, obj)
        portal = aq_parent(aq_inner(self))
        for stage_name, stage_title, path in self._stages:
            stage = self._getStage(portal, path)
            if stage is not None and obj.aq_inContextOf(stage, 1):
                return stage_name
        return None


    security.declarePublic('getObjectInStage')
    def getObjectInStage(self, obj, stage_name):
        """Returns the version of the object in the given stage.
        """
        verifyPermission(StageObjects, obj)
        stages = self._getObjectStages(obj)
        return stages[stage_name]


    security.declarePublic('updateStages')
    def updateStages(self, obj, from_stage, to_stages, message=''):
        """Backward compatibility wrapper.

        Calls updateStages2().  Note that the source stage is
        specified twice, first in the context of obj, second in
        from_stage.  updateStages2() eliminates the potential
        ambiguity by eliminating from_stage.
        """
        s = self.getStageOf(obj)
        if s != from_stage:
            raise StagingError("Ambiguous source stage")
        self.updateStages2(obj, to_stages, message)


    security.declarePublic('updateStages2')
    def updateStages2(self, obj, to_stages, message=''):
        """Updates objects to match the version in the source stage.
        """
        verifyPermission(StageObjects, obj)
        from_stage = self.getStageOf(obj)
        if from_stage is None:
            raise StagingError("Object %s is not in any stage" %
                               '/'.join(obj.getPhysicalPath()))
        if from_stage in to_stages or not to_stages:
            raise StagingError("Invalid to_stages parameter")

        if aq_base(unproxied(obj)) is not aq_base(obj):
            # obj is a proxy.  Find the wrapped target and update that
            # instead of the reference.  Note that the reference will
            # be updated with the container.
            proxy = obj
            obj = getProxyTarget(proxy)
            # Decide whether the reference should be staged at the
            # same time.  If the reference is contained in a
            # non-versioned container, the reference should be staged.
            # OTOH, if the reference is in a versioned container,
            # staging the container will create the reference, so the
            # reference should not be staged by this operation.
            repo = self._getVersionRepository()
            if repo.isUnderVersionControl(aq_parent(aq_inner(proxy))):
                proxy = None
        else:
            proxy = None

        # Check containers first.
        cmap = self._getObjectStages(obj, get_container=1)
        self._checkContainers(obj, to_stages, cmap)
        proxy_cmap = None
        if proxy is not None:
            # Check the containers of the reference also.
            proxy_cmap = self._getObjectStages(proxy, get_container=1)
            self._checkContainers(proxy, to_stages, proxy_cmap)

        # Update the stages.
        if self.auto_checkin:
            self._autoCheckin(obj, message)
        self._updateObjectStates(obj, cmap, to_stages)
        if proxy is not None:
            # Create and update the reference objects also.
            self._updateReferences(proxy, proxy_cmap, to_stages)


    def _updateObjectStates(self, source_object, container_map, to_stages):
        """Internal: updates the state of an object in specified stages.

        Uses version control to do the propagation.
        """
        repo = self._getVersionRepository()
        object_map = self._getObjectStages(source_object)
        version_info = repo.getVersionInfo(source_object)
        version_id = version_info.version_id
        history_id = version_info.history_id

        # Update and/or copy the object to the different stages.
        for stage_name, ob in object_map.items():
            if stage_name in to_stages:
                if ob is None:
                    # The object has not yet been created in the stage.
                    # Copy from the repository to the given stage.
                    ob = repo.getVersionOfResource(history_id, version_id)
                    container = container_map[stage_name]
                    # Make a copy and put it in the new place.
                    id = source_object.getId()
                    container._setObject(id, ob)
                else:
                    if not repo.isUnderVersionControl(ob):
                        p = '/'.join(ob.getPhysicalPath())
                        raise StagingError(
                            'The object "%s", not under version control, '
                            'is in the way.' % p)
                    if repo.getVersionInfo(ob).history_id != history_id:
                        p = '/'.join(ob.getPhysicalPath())
                        p2 = '/'.join(source_object.getPhysicalPath())
                        raise StagingError(
                            'The object "%s", backed by a different '
                            'version history than "%s", '
                            'is in the way.' % (p, p2))
                    repo.updateResource(ob, version_id)


    def _updateReferences(self, proxy, container_map, to_stages):
        """Internal: creates and updates references.
        """
        # Note that version control is not used when staging
        # reference objects.
        ref = getProxyReference(proxy)
        object_map = self._getObjectStages(proxy)
        ref_id = ref.getId()
        for stage_name, ob in object_map.items():
            if stage_name in to_stages:
                if ob is not None:
                    # There is an object at the reference target.
                    if type(aq_base(ob)) is not type(aq_base(proxy)):
                        p = '/'.join(ob.getPhysicalPath())
                        raise StagingError(
                            'The object "%s", which is not a reference, '
                            'is in the way.' % p)
                    # Delete the reference.
                    container = container_map[stage_name]
                    container._delObject(ref_id)

                # Copy the reference from the source stage.
                container = container_map.get(stage_name, None)
                if container is None:
                    # This can happen if a site doesn't yet exist on
                    # the stage.
                    p = '/'.join(proxy.getPhysicalPath())
                    raise StagingError(
                        'The container for "%s" does not exist on "%s"'
                        % (p, stage_name))
                # Duplicate the reference.
                ob = cloneByPickle(aq_base(ref))
                container._setObject(ob.getId(), ob)


    security.declarePublic('removeStages')
    def removeStages(self, obj, stages):
        """Removes the copies on the given stages.
        """
        # If the object is a reference or proxy, this removes only the
        # reference or proxy; this is probably the right thing to do.
        verifyPermission(StageObjects, obj)
        object_map = self._getObjectStages(obj)
        container_map = self._getObjectStages(obj, get_container=1)
        id = obj.getId()
        for stage_name, container in container_map.items():
            if object_map.get(stage_name) is not None:
                if container is not None and stage_name in stages:
                    container._delObject(id)


    security.declarePublic('getVersionIds')
    def getVersionIds(self, obj, include_status=0):
        """Retrieves object version identifiers in the different stages.
        """
        verifyPermission(StageObjects, obj)
        return self._getObjectVersionIds(obj, include_status)


    def _checkContainers(self, obj, stages, containers):
        for stage in stages:
            if containers.get(stage) is None:
                p = '/'.join(obj.getPhysicalPath())
                raise StagingError(
                    'The container for "%s" does not exist on "%s"'
                    % (p, stage))


    security.declarePublic('checkContainers')
    def checkContainers(self, obj, stages):
        """Verifies that the container exists on the given stages.

        If the container is missing on one of the stages, an exception
        is raised.
        """
        verifyPermission(StageObjects, obj)
        containers = self._getObjectStages(obj, get_container=1)
        self._checkContainers(obj, stages, containers)
        return 1


    security.declarePublic('getURLForStage')
    def getURLForStage(self, source, stage, relative=0):
        """Returns the URL of the object on the given stage.

        Besides using absolute_url(), also looks for public_url
        properties on portal objects.  The public_url property is
        useful for generating a public URL even if the current user is
        accessing Zope through a private URL.

        This method is particularly useful when generating URLs for
        inclusion in an email notification regarding staging.
        """
        verifyPermission(StageObjects, source)
        stages = self._getObjectStages(source)
        ob = stages[stage]
        if ob is not None:
            url = ob.absolute_url(relative)
            p = getPortal(ob, None)
            if p is not None:
                # Modify the start of the URL according to the portal's
                # public_url property.
                public_url = getattr(aq_base(p), 'public_url', None)
                if public_url:
                    orig_url = p.absolute_url(relative)
                    if url.startswith(orig_url):
                        url = public_url + url[len(orig_url):]
            return url
        else:
            return None


    security.declarePublic('getObjectStats')
    def getObjectStats(self, source):
        """Returns a structure suitable for presentation of staging status.
        """
        verifyPermission(StageObjects, source)
        res = []
        revisions = self._getObjectVersionIds(source, include_status=1)
        source_stage = self.getStageOf(source)
        for stage_name, stage_title, path in self._stages:
            stageable = (stage_name != source_stage) and (
                not revisions[stage_name]
                or revisions[stage_name] != revisions[source_stage])
            stats = {
                "name": stage_name,
                "title": stage_title,
                "exists": revisions.get(stage_name) is not None,
                "revision": revisions.get(stage_name),
                "stageable": stageable,
                "is_source": (stage_name == source_stage),
                }
            res.append(stats)
        return res


    security.declarePublic('getStageTitle')
    def getStageTitle(self, stage_name):
        """Returns a stage title given a stage name.
        """
        for name, stage_title, path in self._stages:
            if name == stage_name:
                return stage_title
        raise KeyError, "Unknown stage: %s" % stage_name


    security.declareProtected(ManagePortal, 'manage_stagesForm')
    manage_stagesForm = PageTemplateFile('stagesForm', _wwwdir)
    manage_stagesForm.__name__ = "manage_stagesForm"


    security.declareProtected(ManagePortal, 'getStageItems')
    def getStageItems(self):
        """Returns the stage declarations (for the management UI.)
        """
        return self._stages


    security.declareProtected(ManagePortal, 'manage_editStages')
    def manage_editStages(self, stages=(), RESPONSE=None):
        """Edits the stages.
        """
        ss = []
        for stage in stages:
            name = str(stage.name)
            title = str(stage.title)
            path = str(stage.path)
            if name:
                ss.append((name, title, path))
        self._stages = tuple(ss)
        if RESPONSE is not None:
            RESPONSE.redirect(
                '%s/manage_stagesForm?manage_tabs_message=Stages+changed.'
                % self.absolute_url())


InitializeClass(StagingTool)


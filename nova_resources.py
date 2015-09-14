#!/usr/bin/env python
# -- encoding: utf-8 --
#
# Copyright 2015 Telefónica Investigación y Desarrollo, S.A.U
#
# This file is part of FI-Core project.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
#
# You may obtain a copy of the License at:
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#
# See the License for the specific language governing permissions and
# limitations under the License.
#
# For those usages not covered by the Apache version 2.0 License please
# contact with opensource@tid.es
#
author = 'chema'


class NovaResources(object):
    """This class represent the Nova resources of a tenant. It includes
    methods to delete and query the resources"""
    def __init__(self, osclients):
        """Constructor. It requires an OpenStackClients object

        :param openstackclients: an OpenStackClients method (module osclients)
        :return: nothing
        """
        self.novaclient = osclients.get_novaclient()
        self.tenant_id = osclients.get_session().get_project_id()

    def get_tenant_vms(self):
        """return all the tenant's vms
        :return: a list of VMs UUID, with user_id and status
        """
        vms = list()
        for vm in self.novaclient.servers.list():
            assert(vm.tenant_id == self.tenant_id)
            vms.append((vm.id, vm.user_id, vm.status))
        return vms

    def stop_tenant_vms(self):
        """stop all the tenant's which are in ACTIVE state.
        :return: the number of stopped vms
        """
        count = 0
        for vm in self.novaclient.servers.list():
            assert(vm.tenant_id == self.tenant_id)
            if vm.status == 'ACTIVE':
                vm.stop()
                count += 1
        return count

    def delete_tenant_vms(self):
        """delete all the tenant's vms."""
        for vm in self.novaclient.servers.list():
            assert(vm.tenant_id == self.tenant_id)
            vm.delete()

    def get_user_keypairs(self):
        """return a list with the user's keypairs

        The keypair is a very particular case: is the only resource owned
        by the user, not by the tenant. And it is also the only resource that
        does not have a unique id, the name is only unique among the user's
        keypairs. In other way, only the user can obtain the list of keypairs.
        :return: a list of keypairs. The ids are only unique among the user's
           keypairs.
        """
        keypairs = list()
        for keypair in self.novaclient.keypairs.list():
            keypairs.append(keypair.id)
        return keypairs

    def delete_user_keypairs(self):
        """delete all the user's keypairs ."""
        for keypair in self.novaclient.keypairs.list():
            keypair.delete()

    def get_tenant_security_groups(self):
        """return a list with the tenant's security groups (nova)


        With current API, only the tenant can obtain the list of their
        security groups (this situation is changed in a new version).

        However, if using neutron, the ids are the same and an administrator
        in neutron can list all the security groups.
        :return: a list of security group ids.
        """
        security_groups = list()

        for secgroup in self.novaclient.security_groups.list():
            if secgroup.name == 'default' \
                    or secgroup.tenant_id != self.tenant_id:
                continue
            security_groups.append(secgroup.id)
        return security_groups

    def delete_tenant_security_groups(self):
        """delete all the tenant's security groups (nova)"""
        for secgroup in self.novaclient.security_groups.findall():
            if secgroup.name == 'default' \
                    or secgroup.tenant_id != self.tenant_id:
                continue
            secgroup.delete()

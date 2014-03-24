## vim: tabstop=4 shiftwidth=4 softtabstop=4
#
# Copyright (c) 2014 OpenStack Foundation.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
#
# @author: Anirudh Vedantam, anirudh.vedantam@tcs.com, Tata Consultancy Services Ltd.

from oslo.config import cfg

from neutron.agent.common import config
from neutron.agent.linux import ip_lib
from neutron.common import topics
from neutron import context
from neutron.extensions import firewall as fw_ext
from neutron.openstack.common import importutils
from neutron.openstack.common import log as logging
from neutron.plugins.common import constants
from neutron.services.firewall.agents import firewall_agent_api as api
from neutron.services.firewall.agents.l3reference import firewall_l3_agent
####
from novaclient.v1_1 import client as nova_client

LOG = logging.getLogger(__name__)


class FWaaSL3PluginApi(api.FWaaSPluginApiMixin):
    """Agent side of the FWaaS agent to FWaaS Plugin RPC API."""

    def __init__(self, topic, host):
        super(FWaaSL3PluginApi, self).__init__(topic, host)

    def get_firewalls_for_tenant(self, context, **kwargs):
        """Get the Firewalls with rules from the Plugin to send to driver."""
        LOG.debug(_("Retrieve Firewall with rules from Plugin"))

        return self.call(context,
                         self.make_msg('get_firewalls_for_tenant',
                                       host=self.host),
                         topic=self.topic)

    def get_tenants_with_firewalls(self, context, **kwargs):
        """Get all Tenants that have Firewalls configured from plugin."""
        LOG.debug(_("Retrieve Tenants with Firewalls configured from Plugin"))

        return self.call(context,
                         self.make_msg('get_tenants_with_firewalls',
                                       host=self.host),
                         topic=self.topic)

"""class AgentRpcCallBack(FWaaSNetconfAgentRpcCallback):
      
    def init_netconf(self, conf):
        super(AgentRpcCallBack, self).__init__()"""



class FWaaSNetconfAgentRpcCallback(api.FWaaSAgentRpcCallbackMixin):
    """FWaaS Agent support to be used by Neutron L3 agent."""

    def __init__(self, conf):
        import pdb;pdb.set_trace()
        LOG.debug(_("Initializing firewall agent"))
        self.conf = conf
        fwaas_driver_class_path = cfg.CONF.fwaas.driver
        self.fwaas_enabled = cfg.CONF.fwaas.enabled
        #try:
            #self.fwaas_driver = importutils.import_object(
            #    fwaas_driver_class_path)
        self.fwaas_driver_class = fwaas_driver_class_path

            #LOG.debug(_("FWaaS Driver Loaded: '%s'"), fwaas_driver_class_path)
        #except ImportError:
            #msg = _('Error importing FWaaS device driver: %s')
            #raise ImportError(msg % fwaas_driver_class_path)
        self.services_sync = False
        self.root_helper = config.get_root_helper(conf)
        # setup RPC to msg fwaas plugin
        #import pdb;pdb.set_trace()
        self.fwplugin_rpc = FWaaSL3PluginApi(topics.FIREWALL_PLUGIN,
                                             conf.host)
        super(FWaaSNetconfAgentRpcCallback, self).__init__(conf.host)
        #api.FWaaSAgentRpcCallbackMixin(conf.host).__init__(host=conf.host)
        #.__init__(conf.host)

    #def init_netconf(self, conf):
    #    import pdb;pdb.set_trace()
    #    super(AgentRpcCallBack, self).__init__(conf) 

    def _get_router_info_list_for_tenant(self, routers, tenant_id):
        """Returns the list of router info objects on which to apply the fw."""
        root_ip = ip_lib.IPWrapper(self.root_helper)
        # Get the routers for the tenant
        router_ids = [
            router['id']
            for router in routers
            if router['tenant_id'] == tenant_id]
        local_ns_list = root_ip.get_namespaces(self.root_helper)

        router_info_list = []
        # Pick up namespaces for Tenant Routers
        for rid in router_ids:
            if self.router_info[rid].use_namespaces:
                router_ns = self.router_info[rid].ns_name()
                if router_ns in local_ns_list:
                    router_info_list.append(self.router_info[rid])
            else:
                router_info_list.append(self.router_info[rid])
        return router_info_list

    def _invoke_driver_for_plugin_api(self, context, fw, func_name):
        """Invoke driver method for plugin API and provide status back."""
        LOG.debug(_("%(func_name)s from agent for fw: %(fwid)s"),
                  {'func_name': func_name, 'fwid': fw['id']})
        import pdb;pdb.set_trace()
        #try:
        #    routers = self.plugin_rpc.get_routers(context)
        #    router_info_list = self._get_router_info_list_for_tenant(
        #        routers,
        #        fw['tenant_id'])
        #    if not router_info_list:
        #        LOG.debug(_('No Routers on tenant: %s'), fw['tenant_id'])
        """        # fw was created before any routers were added, and if a
                # delete is sent then we need to ack so that plugin can
                # cleanup."""
        #        if func_name == 'delete_firewall':
        #            self.fwplugin_rpc.firewall_deleted(context, fw['id'])
        #        return
        #    LOG.debug(_("Apply fw on Router List: '%s'"),
        #              [ri.router['id'] for ri in router_info_list])
            # call into the driver
        #import pdb;pdb.set_trace()
        try:
                #self.fwaas_driver.__getattribute__(func_name)(
                #    router_info_list,
                #    fw)
                nc = nova_client.Client(fw['prj_username'],
                                fw['auth_token_id'],
                                fw['tenant_id'],
                                fw['auth_URL']
                                 )

                nc.client.auth_token = fw['auth_token_id']
                nc.client.management_url = fw['auth_URL']

                if(nc.client.auth_token is None
                    or nc.client.management_url is None):
                         raise auth_exp()
                
                fw_vm = nc.servers.get(fw['id']) 
                 
                if func_name == 'create_firewall' and fw_vm.status == 'ACTIVE':
                    self.fwaas_driver = importutils.import_object(
                                                                  self.fwaas_driver_class,
                                                                  self.root_helper,
                                                                  fw['ip_address'],
                                                                  fw['gateway_netid'],
                                                                  "vyatta",                           #user,
                                                                  "vyatta",                           #password,
                                                                  "5000",
				                                  )
                    self.
                status = constants.ACTIVE
        except fw_ext.FirewallInternalDriverError:
                LOG.error(_("Firewall Driver Error for %(func_name)s "
                            "for fw: %(fwid)s"),
                          {'func_name': func_name, 'fwid': fw['id']})
                status = constants.ERROR
            # delete needs different handling
            #if func_name == 'delete_firewall':
            #    if status == constants.ACTIVE:
            #        self.fwplugin_rpc.firewall_deleted(context, fw['id'])
            #else:
            #    self.fwplugin_rpc.set_firewall_status(
            #        context,
            #        fw['id'],
            #        status)
        #except Exception:
        #    LOG.exception(
        #        _("FWaaS RPC failure in %(func_name)s for fw: %(fwid)s"),
        #        {'func_name': func_name, 'fwid': fw['id']})
        #    self.services_sync = True
        return

    def _invoke_driver_for_sync_from_plugin(self, ctx, router_info_list, fw):
        """Invoke the delete driver method for status of PENDING_DELETE and
        update method for all other status to (re)apply on driver which is
        Idempotent.
        """
        if fw['status'] == constants.PENDING_DELETE:
            try:
                self.fwaas_driver.delete_firewall(router_info_list, fw)
                self.fwplugin_rpc.firewall_deleted(
                    ctx,
                    fw['id'])
            except fw_ext.FirewallInternalDriverError:
                LOG.error(_("Firewall Driver Error on fw state %(fwmsg)s "
                            "for fw: %(fwid)s"),
                          {'fwmsg': fw['status'], 'fwid': fw['id']})
                self.fwplugin_rpc.set_firewall_status(
                    ctx,
                    fw['id'],
                    constants.ERROR)
        else:
            # PENDING_UPDATE, PENDING_CREATE, ...
            try:
                self.fwaas_driver.update_firewall(router_info_list, fw)
                status = constants.ACTIVE
            except fw_ext.FirewallInternalDriverError:
                LOG.error(_("Firewall Driver Error on fw state %(fwmsg)s "
                            "for fw: %(fwid)s"),
                          {'fwmsg': fw['status'], 'fwid': fw['id']})
                status = constants.ERROR

            self.fwplugin_rpc.set_firewall_status(
                ctx,
                fw['id'],
                status)

    def _process_router_add(self, ri):
        """On router add, get fw with rules from plugin and update driver."""
        LOG.debug(_("Process router add, router_id: '%s'"), ri.router['id'])
        routers = []
        routers.append(ri.router)
        router_info_list = self._get_router_info_list_for_tenant(
            routers,
            ri.router['tenant_id'])
        if router_info_list:
            # Get the firewall with rules
            # for the tenant the router is on.
            ctx = context.Context('', ri.router['tenant_id'])
            fw_list = self.fwplugin_rpc.get_firewalls_for_tenant(ctx)
            LOG.debug(_("Process router add, fw_list: '%s'"),
                      [fw['id'] for fw in fw_list])
            for fw in fw_list:
                self._invoke_driver_for_sync_from_plugin(
                    ctx,
                    router_info_list,
                    fw)

    def process_router_add(self, ri):
        """On router add, get fw with rules from plugin and update driver."""
        # avoid msg to plugin when fwaas is not configured
        if not self.fwaas_enabled:
            return
        try:
            self._process_router_add(ri)
        except Exception:
            LOG.exception(
                _("FWaaS RPC info call failed for '%s'."),
                ri.router['id'])
            self.services_sync = True

    def process_services_sync(self, ctx):
        """On RPC issues sync with plugin and apply the sync data."""
        try:
            # get all routers
            routers = self.plugin_rpc.get_routers(ctx)
            # get the list of tenants with firewalls configured
            # from the plugin
            tenant_ids = self.fwplugin_rpc.get_tenants_with_firewalls(ctx)
            LOG.debug(_("Tenants with Firewalls: '%s'"), tenant_ids)
            for tenant_id in tenant_ids:
                ctx = context.Context('', tenant_id)
                fw_list = self.fwplugin_rpc.get_firewalls_for_tenant(ctx)
                if fw_list:
                    # if fw present on tenant
                    router_info_list = self._get_router_info_list_for_tenant(
                        routers,
                        tenant_id)
                    if router_info_list:
                        LOG.debug(_("Router List: '%s'"),
                                  [ri.router['id'] for ri in router_info_list])
                        LOG.debug(_("fw_list: '%s'"),
                                  [fw['id'] for fw in fw_list])
                        # apply sync data on fw for this tenant
                        for fw in fw_list:
                            # fw, routers present on this host for tenant
                            # install
                            LOG.debug(_("Apply fw on Router List: '%s'"),
                                      [ri.router['id']
                                          for ri in router_info_list])
                            # no need to apply sync data for ACTIVE fw
                            if fw['status'] != constants.ACTIVE:
                                self._invoke_driver_for_sync_from_plugin(
                                    ctx,
                                    router_info_list,
                                    fw)
            self.services_sync = False
        except Exception:
            LOG.exception(_("Failed fwaas process services sync"))
            self.services_sync = True

    def create_firewall(self, context, firewall, host):
        """Handle Rpc from plugin to create a firewall."""
        return self._invoke_driver_for_plugin_api(
            context,
            firewall,
            'create_firewall')

    def update_firewall(self, context, firewall, host):
        """Handle Rpc from plugin to update a firewall."""
        return self._invoke_driver_for_plugin_api(
            context,
            firewall,
            'update_firewall')

    def delete_firewall(self, context, firewall, host):
        """Handle Rpc from plugin to delete a firewall."""
        return self._invoke_driver_for_plugin_api(
            context,
            firewall,
            'delete_firewall')

class AgentRpcCallBack(FWaaSNetconfAgentRpcCallback, firewall_l3_agent.FWaaSL3AgentRpcCallback):

    def __init__(self, conf):
        import pdb;pdb.set_trace() 
        if self.conf.fwaas.driver.split('.')[-1] == 'NetconfJavaWrapper':
            super(AgentRpcCallBack, self).init_netconf(conf)
        else:
            super(AgentRpcCallBack, self).__init__(conf)
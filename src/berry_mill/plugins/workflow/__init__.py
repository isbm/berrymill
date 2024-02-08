from typing import Any
from berry_mill.plugin import PluginIf, PluginArgs, registry
from berry_mill.cfgh import ConfigHandler
import kiwi.logger

log = kiwi.logging.getLogger('kiwi')
log.set_color_format()


class WorkflowPlugin(PluginIf):
    """
    Workflow plugin
    """

    ID = "workflow"

    def run(self, cfg:ConfigHandler):
        """
        Run workflow plugin
        """
        workflow_data:dict[str, Any] = self.get_config(cfg, self.args.workflow)
        log.debug("Workflow: {}".format(workflow_data))

        for plugin_data in workflow_data:
            assert plugin_data, "Plugin data absent"
            assert isinstance(plugin_data, dict), "Plugin configuration mismatch: {}\nNo more details on this error available".format(plugin_data)
            plugin_id = list(plugin_data.keys())[0]
            log.debug("{} calls {}".format(self.ID.title(), plugin_id))
            registry.call(cfg, plugin_id)


# Register plugin
registry(WorkflowPlugin(title="Plugin-based workflow batch caller",
                  argmap=[PluginArgs("-w", "--workflow", help="Override a workflow configuration from a given file")]))

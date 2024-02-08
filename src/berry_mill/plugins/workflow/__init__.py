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
        Run plugin
        """
        print(self.argmap)
        for plugin_data in cfg.config.get(self.ID, []):
            assert plugin_data, "Plugin data absent"
            plugin_id = list(plugin_data.keys())[0]
            log.debug("{} calls {}".format(self.ID.title(), plugin_id))
            registry.call(cfg, plugin_id)


# Register plugin
registry(WorkflowPlugin(title="Plugin-based workflow batch caller",
                  argmap=[PluginArgs("-w", "--workflow", help="Override a workflow configuration from a given file")]))

from ulauncher.api.shared.action.CopyToClipboardAction import CopyToClipboardAction
from ulauncher.api.shared.item.SmallResultItem import SmallResultItem


class CopyPathToClipboardItem(SmallResultItem):
    """
    :param ~ulauncher.utils.Path.Path path:
    """

    # pylint: disable=super-init-not-called
    def __init__(self, path):
        self.path = path

    def get_name(self):
        return 'Copy Path to Clipboard'

    # pylint: disable=super-init-not-called, arguments-differ
    def get_name_highlighted(self, *args):
        pass

    def get_icon(self):
        return 'edit-copy'

    def on_enter(self, query):
        return CopyToClipboardAction(self.path.get_abs_path())
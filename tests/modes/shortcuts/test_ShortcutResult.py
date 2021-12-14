import pytest
from ulauncher.modes.shortcuts.ShortcutResult import ShortcutResult
from ulauncher.modes.Query import Query


class TestShortcutResult:

    @pytest.fixture(autouse=True)
    def OpenUrlAction(self, mocker):
        return mocker.patch('ulauncher.modes.shortcuts.ShortcutResult.OpenUrlAction')

    @pytest.fixture(autouse=True)
    def RunScriptAction(self, mocker):
        return mocker.patch('ulauncher.modes.shortcuts.ShortcutResult.RunScriptAction')

    @pytest.fixture(autouse=True)
    def query_history(self, mocker):
        return mocker.patch('ulauncher.modes.shortcuts.ShortcutResult.QueryHistoryDb.get_instance').return_value

    @pytest.fixture
    def SetUserQueryAction(self, mocker):
        return mocker.patch('ulauncher.modes.shortcuts.ShortcutResult.SetUserQueryAction')

    @pytest.fixture
    def item(self):
        return ShortcutResult('kw', 'name', 'https://site/?q=%s', 'icon_path',
                              is_default_search=True, run_without_argument=False)

    def test_get_keyword(self, item):
        assert item.get_keyword() == 'kw'

    def test_get_name(self, item):
        assert item.get_name() == 'name'

    def test_get_description(self, item):
        assert item.get_description(Query('kw test')) == 'https://site/?q=test'
        assert item.get_description(Query('keyword test')) == 'https://site/?q=...'
        assert item.get_description(Query('goo')) == 'https://site/?q=...'

    def test_get_icon(self, item):
        assert isinstance(item.get_icon(), str)

    def test_on_enter(self, item, OpenUrlAction, SetUserQueryAction):
        item.on_enter(Query('kw test'))
        OpenUrlAction.assert_called_once_with('https://site/?q=test')
        assert not SetUserQueryAction.called

    def test_on_enter__default_search(self, item, OpenUrlAction, SetUserQueryAction):
        item.is_default_search = True
        item.on_enter(Query('search query'))
        OpenUrlAction.assert_called_once_with('https://site/?q=search query')
        assert not SetUserQueryAction.called

    def test_on_enter__run_without_arguments(self, item, OpenUrlAction, SetUserQueryAction):
        item.run_without_argument = True
        item.on_enter(Query('kw'))
        # it doesn't replace %s if run_without_argument = True
        OpenUrlAction.assert_called_once_with('https://site/?q=%s')
        assert not SetUserQueryAction.called

    def test_on_enter__misspelled_kw(self, item, OpenUrlAction, SetUserQueryAction):
        item.on_enter(Query('keyword query'))
        assert not OpenUrlAction.called
        SetUserQueryAction.assert_called_once_with('kw ')

    def test_on_enter__run_file(self, RunScriptAction):
        item = ShortcutResult('kw', 'name', '/usr/bin/something/%s', 'icon_path')
        item.on_enter(Query('kw query'))
        RunScriptAction.assert_called_once_with('/usr/bin/something/query')

    def test_on_enter__save_query_to_history(self, item, query_history):
        item.on_enter(Query('my-query'))
        query_history.save_query.assert_called_once_with('my-query', 'name')
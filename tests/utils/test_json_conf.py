import json
import shutil
from pathlib import Path

import pytest

from ulauncher.utils.json_conf import JsonConf, save_as, stringify

json_file = "/tmp/ulauncher-test/jsonconf.json"


def load_json(file=json_file):
    try:
        with open(file) as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


class TestJsonConf:
    def setup_class(self):
        Path("/tmp/ulauncher-test").mkdir(parents=True, exist_ok=True)

    def teardown_class(self):
        shutil.rmtree("/tmp/ulauncher-test")

    def test_attr_methods(self):
        jc = JsonConf()
        assert not hasattr(jc, "a")
        with pytest.raises(AttributeError):
            jc.a  # noqa: B018
        jc.a = False
        assert hasattr(jc, "a")
        assert jc.a is False

    def test_setting_and_comparison(self):
        jc = JsonConf()
        jc.a = 1
        jc.update({"b": 2}, c=3)
        jc["d"] = 4
        assert jc == JsonConf(a=1, b=2, c=3, d=4)
        assert JsonConf(b=2, a=1) == JsonConf({"a": 1, "b": 2})
        assert JsonConf(a=1, b=2) != JsonConf({"a": 1})

    def test_new_file_file_cache(self):
        file_path = "/tmp/ulauncher-test/jsonconf_test_cache.json"
        jc1 = JsonConf.load(file_path)
        assert not hasattr(jc1, "a")
        jc1.a = 1
        jc2 = JsonConf.load(file_path)
        assert id(jc2) == id(jc1)  # tests that it's actually the same object in memory
        assert jc2.a == 1

    def test_stringify(self):
        assert stringify(JsonConf(a=1, c=3, b=2)) == '{"a": 1, "b": 2, "c": 3}'
        assert stringify(JsonConf(a=1, c=3, b=2), sort_keys=False) == '{"a": 1, "c": 3, "b": 2}'
        assert stringify(JsonConf(a=1, b=2), indent=4) == '{\n    "a": 1,\n    "b": 2\n}'
        conf = JsonConf(a=None, b=[], c={}, d=1)
        assert stringify(conf) == '{"d": 1}'
        assert stringify(conf, value_blacklist=[]) == '{"a": null, "b": [], "c": {}, "d": 1}'

    def test_save_as(self):
        # Check that JsonConf initiated w or w/o path saves to the path specified,
        # not the instance path
        file_path = "/tmp/ulauncher-test/jsonconf_save_as.json"
        jc_static = JsonConf(abc=123)
        save_as(jc_static, file_path)
        assert load_json(file_path).get("abc") == 123
        jc = JsonConf.load(json_file)
        jc.save()
        jc.bcd = 234
        save_as(jc, file_path)
        assert load_json().get("abc", None) is None
        assert load_json(file_path).get("abc") is None
        assert load_json(file_path).get("bcd") == 234

    def test_save(self):
        jc = JsonConf.load(json_file)
        jc.asdf = "xyz"
        jc.save()
        assert load_json().get("asdf") == "xyz"
        jc.update(asdf="zyx")
        jc.save()
        assert load_json().get("asdf") == "zyx"

    def test_cannot_override_method(self):
        jc = JsonConf()
        with pytest.raises(KeyError):
            jc.get = 1
        assert callable(jc.get)

    def test_inheritance(self):
        class ClassWDefault(JsonConf):
            b = 1
            a = 2

            def sum(self):
                return self.a + self.b

        class SubclassWDefault(ClassWDefault):
            c = 3

        assert ClassWDefault().b == 1
        assert ClassWDefault(b=2).b == 2
        assert ClassWDefault(a=9).sum() == 10
        inst = ClassWDefault()
        assert inst.sum() == 3
        assert stringify(SubclassWDefault()) == '{"a": 2, "b": 1, "c": 3}'

        json_ko_file = "/tmp/ulauncher-test/jsonconf-key-order.json"
        inst = ClassWDefault.load(json_ko_file)
        inst.save()
        assert list(load_json(json_ko_file).keys()) == ["a", "b"]

    def test_constructor_is_cloned(self):
        class ClassWDict(JsonConf):
            subdict = {}

        inst = ClassWDict()
        inst.subdict["k"] = "v"
        assert ClassWDict().subdict.get("k") is None
        assert inst.subdict.get("k") == "v"

    def test_setitem_always_used(self):
        class UnderscorePrefix(JsonConf):
            def __setitem__(self, key, value):
                super().__setitem__("_" + key, value)

        data = UnderscorePrefix({"one": 1})
        data.update({"two": 2})
        data.three = 3
        data["four"] = 4
        assert stringify(data, sort_keys=False) == '{"_one": 1, "_two": 2, "_three": 3, "_four": 4}'

    def test_file_cache(self):
        class C1(JsonConf):
            pass

        class C2(JsonConf):
            pass

        c1 = C1.load(json_file)
        c2a = C2.load(json_file)
        c2b = C2.load(json_file)
        c2a.uniqe_cache_key = 1
        assert not hasattr(c1, "uniqe_cache_key")
        assert hasattr(c2a, "uniqe_cache_key")
        assert hasattr(c2b, "uniqe_cache_key")
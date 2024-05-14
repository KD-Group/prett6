import json
import unittest

import prett6


class MyTestCase(unittest.TestCase):
    def test_project_storage_tree(self):
        class ItemDemo(prett6.IntProjectItem):
            pass

        class ProjectDemo(prett6.AbstractProject):
            def __init__(self):
                self.width = ItemDemo(self)
                self.height = ItemDemo(self)

        p = ProjectDemo()
        p.width.int.value = 16
        p.height.int.value = 20
        self.assertEqual(p.value, {'width': '16', 'height': '20'})
        json_string = json.dumps(p.value)

        p.value = {'height': 17}
        self.assertEqual(p.height.int.value, 17)
        self.assertEqual(p.width.value, None)

        p.value = json.loads(json_string)
        self.assertEqual(p.width.string.value, '16')
        self.assertEqual(p.height.string.value, '20')

    def test_value_changed(self):
        class ItemDemo(prett6.IntProjectItem):
            pass

        class ProjectDemo(prett6.AbstractProject):
            def __init__(self):
                self.width = ItemDemo(self)
                self.height = ItemDemo(self)

        p = ProjectDemo()
        times = []

        @prett6.connect_with(p.width.int.changed)
        def width_changed(value: int):
            times.append(len(times))

            if len(times) == 1:
                self.assertEqual(value, 16)
            elif len(times) == 2:
                self.assertEqual(value, 20)
            elif len(times) == 3:
                self.assertEqual(value, 0)
            else:
                pass

        p.width.string.value = '16'
        p.width.value = '20'
        p.width.int.value = 0

        self.assertEqual(len(times), 3)

    def test_setting_value(self):
        class SettingItemDemo(prett6.IntSettingItem):
            pass

        class SettingDemo(prett6.AbstractSetting):
            def __init__(self):
                self.margin = SettingItemDemo(self, 5)

        s = SettingDemo()
        self.assertEqual(s.margin.int.value, 5)
        self.assertEqual(s.value, {})

        s.margin.int.value = 20
        self.assertEqual(s.margin.int.value, 20)
        self.assertEqual(s.value, {'margin': '20'})

    def test_emun_item(self):
        class Fruit(prett6.Enum):
            APPLE = "苹果"
            BANANA = "香蕉"

        class ProjectDemo(prett6.AbstractProject):
            def __init__(self):
                self.fruit = prett6.EnumItem(self, Fruit)

        p = ProjectDemo()
        p.fruit.type.value = Fruit.BANANA

        self.assertEqual(p.fruit.type.value.value, "香蕉")
        self.assertEqual(p.fruit.type.value, Fruit.BANANA)


if __name__ == '__main__':
    unittest.main()

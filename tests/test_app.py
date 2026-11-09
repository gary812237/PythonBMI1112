import unittest

from app import app, bmi_gauge_angle, bmi_guidance


class BmiAppTests(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_initial_page(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        page = response.get_data(as_text=True)
        self.assertIn("了解自己的<br><em>健康狀況。</em>", page)
        self.assertIn("計算你的 BMI", page)

    def test_calculation_and_advice(self):
        response = self.client.post("/", data={"height": "170", "weight": "65"})
        page = response.get_data(as_text=True)
        self.assertIn("22.5", page)
        self.assertIn("健康體位", page)
        self.assertIn("維持均衡飲食", page)
        self.assertIn('style="--needle-angle: -15.0deg"', page)
        self.assertIn('class="gauge-needle"', page)

    def test_name_is_optional_and_personalizes_advice(self):
        response = self.client.post("/", data={"name": "  小明  ", "height": "170", "weight": "65"})
        page = response.get_data(as_text=True)
        self.assertIn('name="name" type="text"', page)
        self.assertIn('value="小明"', page)
        self.assertIn('<p id="result-advice">小明，維持均衡飲食', page)

        for name in ("", "   "):
            with self.subTest(name=name):
                response = self.client.post("/", data={"name": name, "height": "170", "weight": "65"})
                self.assertIn('<p id="result-advice">維持均衡飲食', response.get_data(as_text=True))

    def test_name_is_preserved_when_other_fields_are_invalid(self):
        response = self.client.post("/", data={"name": "小明", "height": "", "weight": "65"})
        page = response.get_data(as_text=True)
        self.assertIn('value="小明"', page)
        self.assertIn('id="height-error"', page)

    def test_name_is_escaped_in_input_and_advice(self):
        response = self.client.post("/", data={"name": '<script>alert("x")</script>', "height": "170", "weight": "65"})
        page = response.get_data(as_text=True)
        self.assertNotIn('<script>alert("x")</script>', page)
        self.assertIn('&lt;script&gt;alert(&#34;x&#34;)&lt;/script&gt;，維持均衡飲食', page)

    def test_gauge_angle_is_clamped_to_display_range(self):
        self.assertEqual(bmi_gauge_angle(10), -90)
        self.assertEqual(bmi_gauge_angle(25), 0)
        self.assertEqual(bmi_gauge_angle(40), 90)
        self.assertEqual(bmi_gauge_angle(5), -90)
        self.assertEqual(bmi_gauge_angle(45), 90)

    def test_taiwan_adult_thresholds(self):
        for bmi, category in [
            (18.4, "體重過輕"),
            (18.5, "健康體位"),
            (23.9, "健康體位"),
            (24.0, "體重過重"),
            (26.9, "體重過重"),
            (27.0, "肥胖"),
        ]:
            with self.subTest(bmi=bmi):
                self.assertEqual(bmi_guidance(bmi)["label"], category)

    def test_invalid_fields_do_not_produce_result(self):
        for height, weight in [("", "65"), ("0", "65"), ("abc", "65"), ("170", "-2"), ("inf", "65"), ("170", "nan"), ("1e-300", "65"), ("1e308", "65"), ("1", "1e308")]:
            with self.subTest(height=height, weight=weight):
                response = self.client.post("/", data={"height": height, "weight": weight})
                page = response.get_data(as_text=True)
                self.assertEqual(response.status_code, 200)
                self.assertIn('aria-invalid="true"', page)
                self.assertIn('id="result-panel" aria-labelledby="result-title" aria-live="polite" hidden', page)

    def test_input_is_escaped(self):
        response = self.client.post("/", data={"height": '<script>alert(1)</script>', "weight": "65"})
        page = response.get_data(as_text=True)
        self.assertNotIn("<script>", page)
        self.assertIn("請輸入大於 0", page)


if __name__ == "__main__":
    unittest.main()

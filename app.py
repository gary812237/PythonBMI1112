import math

from flask import Flask, render_template, request

app = Flask(__name__)

BMI_GUIDANCE = {
    "low": {
        "label": "體重過輕",
        "tone": "low",
        "advice": "留意是否攝取足夠且均衡的營養，規律進食並搭配適度肌力活動；若體重持續下降，建議諮詢醫師或營養師。",
    },
    "healthy": {
        "label": "健康體位",
        "tone": "healthy",
        "advice": "維持均衡飲食與規律運動，並持續留意睡眠及生活習慣，幫助保持健康體位。",
    },
    "high": {
        "label": "體重過重",
        "tone": "high",
        "advice": "可從減少含糖飲料、增加蔬菜與日常活動量開始，循序建立適合自己的健康習慣。",
    },
    "obese": {
        "label": "肥胖",
        "tone": "obese",
        "advice": "建議與醫師或營養師討論適合自己的飲食及運動計畫，並留意血壓、血糖等健康指標。",
    },
}


def bmi_guidance(bmi):
    if bmi < 18.5:
        return BMI_GUIDANCE["low"]
    if bmi < 24:
        return BMI_GUIDANCE["healthy"]
    if bmi < 27:
        return BMI_GUIDANCE["high"]
    return BMI_GUIDANCE["obese"]


def bmi_gauge_angle(bmi):
    gauge_bmi = min(max(bmi, 10), 40)
    return (gauge_bmi - 10) / 30 * 180 - 90


def parse_positive_number(value):
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if math.isfinite(number) and number > 0 else None


@app.route("/", methods=["GET", "POST"])
def index():
    name_input = ""
    height_input = ""
    weight_input = ""
    errors = {}
    result = None

    if request.method == "POST":
        name_input = request.form.get("name", "").strip()
        height_input = request.form.get("height", "").strip()
        weight_input = request.form.get("weight", "").strip()
        height = parse_positive_number(height_input)
        weight = parse_positive_number(weight_input)

        if height is None:
            errors["height"] = "請輸入大於 0 的有效身高（公分）。"
        if weight is None:
            errors["weight"] = "請輸入大於 0 的有效體重（公斤）。"

        if not errors:
            height_meters = height / 100
            height_squared = height_meters * height_meters
            if not math.isfinite(height_squared) or height_squared == 0:
                errors["height"] = "無法使用這組數值計算 BMI，請檢查身高與體重。"
            else:
                bmi = weight / height_squared
                if not math.isfinite(bmi) or bmi == 0:
                    errors["weight"] = "無法使用這組數值計算 BMI，請檢查身高與體重。"
                else:
                    displayed_bmi = round(bmi, 1)
                    result = {
                        "bmi": f"{displayed_bmi:.1f}",
                        "gauge_angle": f"{bmi_gauge_angle(displayed_bmi):.1f}deg",
                        **bmi_guidance(displayed_bmi),
                    }

    return render_template(
        "index.html",
        name_input=name_input,
        height_input=height_input,
        weight_input=weight_input,
        errors=errors,
        result=result,
        guidance_data=BMI_GUIDANCE,
    )


if __name__ == "__main__":
    app.run(debug=True)

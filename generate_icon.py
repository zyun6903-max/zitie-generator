"""生成字帖生成器图标 app.ico（64x64）。"""
from PIL import Image, ImageDraw, ImageFont

SIZE = 64
img = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
draw = ImageDraw.Draw(img)

# 红色方框背景（田字格外框）
draw.rectangle([4, 4, 60, 60], outline=(200, 50, 50), width=3)

# 田字格十字虚线
for i in range(4, 61, 2):
    draw.point((32, i), fill=(200, 50, 50, 120))
    draw.point((i, 32), fill=(200, 50, 50, 120))

# 写一个"字"字
try:
    font = ImageFont.truetype("/System/Library/Fonts/PingFang.ttc", 32)
except Exception:
    font = ImageFont.load_default()
draw.text((14, 12), "字", fill=(200, 50, 50), font=font)

img.save("app.ico", format="ICO", sizes=[(64, 64)])
print("生成 app.ico")

from PIL import Image, ImageDraw, ImageFont

# Задаем размеры и цвет фона
width, height = 400, 200
background_color = (255, 255, 255)  # белый фон

# Создаем изображение
image = Image.new("RGB", (width, height), background_color)

# Рисуем на изображении
draw = ImageDraw.Draw(image)
draw.rectangle([50, 50, 150, 150], fill=(255, 0, 0), outline=(0, 0, 0))  # красный квадрат с черной обводкой

# Сохраняем изображение в формате JPEG

image.save("example_image.jpeg", "JPEG")

print("Изображение сохранено как example_image.jpeg")

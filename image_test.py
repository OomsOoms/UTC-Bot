from PIL import Image, ImageDraw, ImageFont

# Set the font and font size
font = ImageFont.truetype('arialbd.ttf', 60)

# Set the text and the background color
event_name = "3x3"
round_num = 1
competition_id = "CubeClash2023"
text = f"{event_name} round {round_num} - {competition_id}"
bg_color = (0, 0, 0, 0)  # transparent

# Create an image with the text
img = Image.new('RGBA', (1000, 100), color=bg_color)
draw = ImageDraw.Draw(img)
text_bbox = draw.textbbox((0, 0), text, font=font)
x = (img.width - text_bbox[2]) // 2
y = (img.height - text_bbox[3]) // 2
draw.text((x, y), text, fill=(255, 255, 255), font=font)

# Save the image to a file
img.save('image.png')

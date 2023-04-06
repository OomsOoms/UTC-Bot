from PIL import Image, ImageDraw, ImageFont

# set width and height of the table
width = 2000
height = 500

# load the image and calculate the new width and height based on the aspect ratio
scram_img = Image.open('scram.png')
new_width = int(height / scram_img.height * scram_img.width)
scram_img = scram_img.resize((new_width, height))

# calculate the width of the first column and second column
second_col_width = scram_img.width
first_col_width = int(width-second_col_width)

# create a new image with transparent background
img = Image.new('RGBA', (width, height), (0, 0, 0, 0))

# create a drawing context
draw = ImageDraw.Draw(img)

# set line color and font to white
line_color = (255, 255, 255)
text_color = (255, 255, 255)

# draw the vertical line separating the columns
draw.line([(first_col_width, 0), (first_col_width, height)], fill=line_color, width=1)

# paste the image in the second column on the far right of the column
paste_location = (width-scram_img.width, 0)
img.paste(scram_img, paste_location)

# define the text to display
text = "Rw Lw2 F2 3Fw' R F' 3Dw Fw' 3Lw2 3Fw'Uw 3Uw' Rw Dw B U Fw Bw F' Dw'Lw' 3Fw 3Lw' D2 L' Rw Bw' Fw2 L BU R2 B' R' 3Fw' Bw2 U2 3Fw Fw2 F2L' Bw2 Uw2 L2 3Uw D2 Bw' L Fw2 3Fw'L 3Bw B2 L' R 3Rw 3Bw Bw' B' F2D' L' B Uw' 3Lw' 3Bw R2 U 3Uw' 3Rw 3Bw L' R2 U Lw' U 3Uw' Lw 3Fw23Lw2 Uw Rw' F 3Lw R 3Dw2 D Uw2 Lw' F Rw 3Bw 3Dw' 3Fw R' 3Fw2 F Uw"

# set font size and style
font_size = 100
font = ImageFont.truetype('arial.ttf', size=font_size)
line_spacing = 20  # added line spacing variable

# split the text into lines based on the available width and the font size
words = text.split()
lines = []
current_line = ''
for word in words:
    if font.getsize(current_line + ' ' + word)[0] > first_col_width:
        lines.append(current_line.strip())
        current_line = ''
    current_line += ' ' + word
if current_line:
    lines.append(current_line.strip())

# set font size based on the number of lines
num_lines = len(lines)
max_font_size = int(first_col_width / max([len(line) for line in lines]))
font_size = min(font_size, max_font_size)
font = ImageFont.truetype('arial.ttf', size=font_size)

# calculate the size of the text to fit the column width
text_width, text_height = font.getsize(lines[0])
while text_width > first_col_width:
    font_size -= 1
    font = ImageFont.truetype('arial.ttf', size=font_size)
    text_width, text_height = font.getsize(lines[0])

# calculate the line spacing based on the available height
total_text_height = text_height * num_lines
remaining_height = height - total_text_height
line_spacing = int(remaining_height / (num_lines - 1))

# draw the text with the calculated line spacing
line_height = text_height + line_spacing
for i, line in enumerate(lines):
    text_width, text_height = font.getsize(line)
    x = 0
    y = i * line_height
    text_box_width = first_col_width
    text_box_height = text_height + line_spacing
    text_box_x = 0
    text_box_y = i * line_height
    draw.rectangle([(text_box_x, text_box_y), (text_box_x+text_box_width, text_box_y+text_box_height)], fill=(0,0,0,0), outline=None)
    draw.text((text_box_x, y), line, fill=text_color, font=font, align='left')




# save the image as "scramble.png"
img.save('scramble.png')

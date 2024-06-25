import os
import random
import json
from tqdm import tqdm
from PIL import Image, ImageDraw, ImageFont

class OCRDataGenerateToolKit():
    def __init__(
            self,
            word_list_path: str, 
            background_path: str,
            font_path: str,
            num_of_retry: int) -> None:

        # word
        with open(word_list_path, 'r') as f:
            word_list = f.readlines()
        self.word_list = [word[:-1] for word in word_list]

        # image background list 
        self.background_list = os.listdir(background_path)
        self.background_dir = background_path

        # font_collection
        self.font_collection = os.listdir(font_path)
        self.font_collection_dir = font_path

        # font_size range
        self.small = [13, 30]
        self.medium = [30, 100]
        self.large = [100, 250] 
        self.extreme_large = [250, 1000]

        # retry number
        self.num_of_retry = num_of_retry
    
    def _calculate_relative_luminance(self, color):
        if type(color) == int:
            r, g, b = (color, color, color)
        else:
            r, g, b = color
        r, g, b = r / 255.0, g / 255.0, b / 255.0
        r = r if r <= 0.03928 else ((r + 0.055) / 1.055) ** 2.4
        g = g if g <= 0.03928 else ((g + 0.055) / 1.055) ** 2.4
        b = b if b <= 0.03928 else ((b + 0.055) / 1.055) ** 2.4
        return 0.2126 * r + 0.7152 * g + 0.0722 * b

    def _get_contrast_color_auto(self, background_color, isDocument=False):
        luminance = self._calculate_relative_luminance(background_color)
        # Define a palette of colors
        # palette = [
        #     (255, 255, 255),  # White
        #     (0, 0, 0),        # Black
        #     (255, 0, 0),      # Red
        #     (0, 255, 0),      # Green
        #     (0, 0, 255),      # Blue
        #     (255, 255, 0),    # Yellow
        #     (255, 0, 255),    # Magenta
        #     (0, 255, 255)     # Cyan
        #     # Add more colors as needed
        # ]
        light_color_palette = [
            "#ffffff",
            "#fae1dd",
            "#f8edeb",
            "#e8e8e4",
            "#d8e2dc",
            "#ece4db",
            "#ece4db",
            "#ffe5d9",
            "#ffd7ba",
            "#fec89a",
            "#caffbf",
            "#fdffb6",
            "#a0c4ff",
            "#fff1e6",
            "#4cc9f0",
            "#95d5b2",
            "#40916c",
            "#f8edeb",
            "#64dfdf",
            "#52b69a",
        ]

        dark_color_palette = [
            "#000814",
            "#003566",
            "#001d3d",
            "#9a031e",
            "#5f0f40",
            "#03045e",
            "#264653",
            "#1d3557",
            "#457b9d",
            "#283618",
            "#023047",
            "#6b705c",
            "#03045e",
            "#023e8a",
            "#6d6875",
            "#000000",
            "#14213d",
            "#003049",
            "#03071e",
            "#370617",
            "#6a040f",
            "#9d0208",
            "#006d77",
            "#3d405b",
            "#073b4c",
            "#005f73",
            "#4a4e69",
            "#081c15",
            "#1b4332",
        ]

        white_color = "#ffffff"
        black_color = "#000000"

        # Choose a color from the palette based on luminance
        if isDocument:
            choosen_color = black_color if luminance > 0.5 else white_color
        else:
            choosen_color = random.choice(dark_color_palette) if luminance > 0.5 else random.choice(light_color_palette)
        return choosen_color

    def __draw_text_with_shadow(self, draw, position, text, font, text_color, shadow_color, shadow_offset):
        # Draw the shadow
        shadow_position = (position[0] + shadow_offset, position[1] + shadow_offset)
        draw.text(shadow_position, text, font=font, fill=shadow_color)

        # Draw the actual text on top
        draw.text(position, text, font=font, fill=text_color)
    
    def __draw_text_with_stroke(self, draw, position, text, font, text_color, stroke_color, stroke_width):
        # Draw the shadow
        x, y = position
        draw.text((x-stroke_width, y-stroke_width), text, font=font, fill=stroke_color)
        draw.text((x+stroke_width, y-stroke_width), text, font=font, fill=stroke_color)
        draw.text((x-stroke_width, y+stroke_width), text, font=font, fill=stroke_color)
        draw.text((x+stroke_width, y+stroke_width), text, font=font, fill=stroke_color)

        # Draw the actual text on top
        draw.text(position, text, font=font, fill=text_color)

    def add_text_to_image(
            self, 
            image, red_zone_x, red_zone_y, 
            font_size_range: str,
            effect = None,
            ):
        # RANDOM BACKGROUND
        width, height = image.size
        draw = ImageDraw.Draw(image)

        # RANDOM TEXT TO GENERATE
        text = random.choice(self.word_list)

        # RANDOM FONT SIZE
        font_size_range = getattr(self, font_size_range)
        font_size = random.choice(font_size_range)

        # RANDOM FONT TYPE
        font_name = random.choice(self.font_collection)
        # print(font_name, " --- ", text)
        font = ImageFont.truetype(
            os.path.join(self.font_collection_dir, font_name), 
            font_size
        )

        flag = 0
        while (draw.textlength(text, font=font) > width - 10):
            font_size = random.choice(font_size_range)
            font = ImageFont.truetype(
                os.path.join(self.font_collection_dir, font_name), 
                font_size
            )
            flag += 1
            if flag > self.num_of_retry:
                break

        # RANDOM FONT COLOR 
        # text_color = random.choice(self.text_color_list)
        shadow_color = "gray"
        shadow_offset = 2
        stroke_color = "white"
        stroke_width = 1

        # RANDOM TEXT POSITION
        text_position = (
            random.uniform(0, max(0, width - draw.textlength(text, font=font))),
            random.uniform(0, max(0, height - font_size*4/3)),
        )

        flag_redzone = 0
        while (
                text_position[0] < red_zone_x[1] and text_position[0] + draw.textlength(text, font=font) > red_zone_x[0] and
                text_position[1] < red_zone_y[1] and text_position[1] + font_size*4/3 > red_zone_y[0]
            ):
            text_position = (
                random.uniform(0, max(1, width - draw.textlength(text, font=font))),
                random.uniform(0, max(1, height - font_size*4/3)),
            )
            flag_redzone += 1
            if flag_redzone > self.num_of_retry:
                break

        # CHOOSE THE SUITABLE TEXT COLOR FOR BACKGROUND POSITION
        text_color = self._get_contrast_color_auto(image.getpixel(text_position))
        
        # BOX COLOR
        box_color = (255, 0, 0, 128)
        text_box = draw.textbbox(text_position, text, font=font)

        if effect == "shadow":
            text_box = (text_box[0], text_box[1], text_box[2] + shadow_offset, text_box[3] + shadow_offset)
        elif effect == "stroke":
            text_box = (
                text_box[0] - stroke_width, 
                text_box[1] - stroke_width, 
                text_box[2] + stroke_width*2, 
                text_box[3] + stroke_width*2)

        # CALCULATE AND DRAW BOUNDING BOX
        if flag<=self.num_of_retry and flag_redzone<=self.num_of_retry:
            # use to draw the rectangle for visualize, use for testing only !!
            draw.rectangle(text_box, outline=box_color, width=2)
            
            if effect == "shadow":
                self.__draw_text_with_shadow(
                    draw = draw,
                    position = text_position, 
                    text = text, 
                    text_color = text_color, 
                    font = font, 
                    shadow_color = shadow_color, 
                    shadow_offset = shadow_offset
                )
            elif effect == "stroke":
                self.__draw_text_with_stroke(
                    draw = draw,
                    position = text_position, 
                    text = text, 
                    text_color = text_color, 
                    font = font, 
                    stroke_color = stroke_color, 
                    stroke_width = stroke_width
                )
            else:
                draw.text(
                    xy = text_position, 
                    text = text, 
                    fill = text_color, 
                    font = font, 
                )
        
            polygon = [[text_box[0], text_box[1]],
                    [text_box[2], text_box[1]],
                    [text_box[2], text_box[3]],
                    [text_box[0], text_box[3]]]
            
            # (x1, y1, x2, y2) format
            quad = text_box

            return text, polygon, quad
        else:
            return None, None, None 

    def create_image_data(
            self, 
            name_index,
            fontsize_collection = [0, 0, 0, 0],
            add_type = None,
            ):
        result_dec = []
        result_rec = []

        no_small, no_medium, no_large, no_extreme = fontsize_collection
        image_name = random.choice(self.background_list)
        image = Image.open(os.path.join(self.background_dir, image_name))
        width, height = image.size
        red_zone_x = (height + 1, -1)
        red_zone_y = (height + 1, -1)
        text_index = 0

        for i in range(no_small):
            # if the text is small, we don't use Stroke style for the text here
            text, polygon, quad = self.add_text_to_image(
                image, red_zone_x, red_zone_y, 
                font_size_range='small', 
                add_type = add_type if add_type != "stroke" else None
            )
            if text == None:
                continue

            result_dec.append({
                "polygon": polygon,
                "bbox": quad,
                "bbox_label":1,
                "ignore": False
            })
            result_rec.append({
                "instances":[{
                    "text": text
                }],
                "img_path": f"image_{name_index}_{text_index}.jpg"
            })
            red_zone_x = (min(quad[0], red_zone_x[0]), max(quad[2], red_zone_x[1]))
            red_zone_y = (min(quad[1], red_zone_y[0]), max(quad[3], red_zone_y[1]))
            crop_image = image.crop(quad)
            crop_image.save(os.path.join(self.folder, self.name, "text_crop/", f"image_{name_index}_{text_index}.jpg"))
            text_index += 1

        for i in range(no_medium):
            text, polygon, quad = self.add_text_to_image(image, red_zone_x, red_zone_y, font_size_range='medium', add_type = add_type)
            if text == None:
                continue
            
            result_dec.append({
                "polygon": polygon,
                "bbox": quad,
                "bbox_label":1,
                "ignore": False
            })
            result_rec.append({
                "instances":[{
                    "text": text
                }],
                "img_path": f"image_{name_index}_{text_index}.jpg"
            })
            red_zone_x = (min(quad[0], red_zone_x[0]), max(quad[2], red_zone_x[1]))
            red_zone_y = (min(quad[1], red_zone_y[0]), max(quad[3], red_zone_y[1]))
            crop_image = image.crop(quad)
            crop_image.save(os.path.join(self.folder, self.name, "text_crop/", f"image_{name_index}_{text_index}.jpg"))
            text_index += 1

        for i in range(no_large):
            text, polygon, quad = self.add_text_to_image(image, red_zone_x, red_zone_y, font_size_range='large', add_type = add_type)
            if text == None:
                continue
            
            result_dec.append({
                "polygon": polygon,
                "bbox": quad,
                "bbox_label":1,
                "ignore": False
            })
            result_rec.append({
                "instances":[{
                    "text": text
                }],
                "img_path": f"image_{name_index}_{text_index}.jpg"
            })
            red_zone_x = (min(quad[0], red_zone_x[0]), max(quad[2], red_zone_x[1]))
            red_zone_y = (min(quad[1], red_zone_y[0]), max(quad[3], red_zone_y[1]))
            crop_image = image.crop(quad)
            crop_image.save(os.path.join(self.folder, self.name, "text_crop/", f"image_{name_index}_{text_index}.jpg"))
            text_index += 1

        for i in range(no_extreme):
            text, polygon, quad = self.add_text_to_image(image, red_zone_x, red_zone_y, font_size_range='extreme_large', add_type = add_type)
            if text == None:
                continue
            
            result_dec.append({
                "polygon": polygon,
                "bbox": quad,
                "bbox_label":1,
                "ignore": False
            })
            result_rec.append({
                "instances":[{
                    "text": text
                }],
                "img_path": f"image_{name_index}_{text_index}.jpg"
            })
            red_zone_x = (min(quad[0], red_zone_x[0]), max(quad[2], red_zone_x[1]))
            red_zone_y = (min(quad[1], red_zone_y[0]), max(quad[3], red_zone_y[1]))
            crop_image = image.crop(quad)
            crop_image.save(os.path.join(self.folder, self.name, "text_crop/", f"image_{name_index}_{text_index}.jpg"))
            text_index += 1

        image.save(os.path.join(self.folder, self.name, 'textdet/', f"image_{name_index}.jpg"))
        # image.show()
        return result_dec, width, height, result_rec
    
    def create_image_test(
            self,
            name_index,
            fontsize_collection = [0, 0, 0, 0],
            add_type = None,
            ):
        result_dec = []
        result_rec = []

        no_small, no_medium, no_large, no_extreme = fontsize_collection
        image_name = random.choice(self.background_list)
        image = Image.open(os.path.join(self.background_dir, image_name))
        width, height = image.size

        print(f"Image test: {name_index}, with width: {width} and height: {height}")

        red_zone_x = (height + 1, -1)
        red_zone_y = (height + 1, -1)
        text_index = 0

        for i in range(no_small):
            # if the text is small, we don't use Stroke style for the text here
            text, polygon, quad = self.add_text_to_image(
                image, red_zone_x, red_zone_y, 
                font_size_range='small', 
                add_type = add_type if add_type != "stroke" else None
            )
            if text == None:
                continue

            result_dec.append({
                "polygon": polygon,
                "bbox": quad,
                "bbox_label":1,
                "ignore": False
            })
            result_rec.append({
                "instances":[{
                    "text": text
                }],
                "img_path": f"image_{name_index}_{text_index}.jpg"
            })
            red_zone_x = (min(quad[0], red_zone_x[0]), max(quad[2], red_zone_x[1]))
            red_zone_y = (min(quad[1], red_zone_y[0]), max(quad[3], red_zone_y[1]))
            crop_image = image.crop(quad)
            print(f"image_{name_index}_{text_index}.jpg")
            print(f"Text: {text}")
            print(quad)
            if (quad[0] < 0 or quad[0] > width or 
                quad[2] < 0 or quad[2] > width or 
                quad[1] < 0 or quad[1] > height or 
                quad[3] < 0 or quad[3] > height):
                print("Out of image !!!")
            crop_image.show()
            text_index += 1

        for i in range(no_medium):
            text, polygon, quad = self.add_text_to_image(image, red_zone_x, red_zone_y, font_size_range='medium', add_type = add_type)
            if text == None:
                continue
            
            result_dec.append({
                "polygon": polygon,
                "bbox": quad,
                "bbox_label":1,
                "ignore": False
            })
            result_rec.append({
                "instances":[{
                    "text": text
                }],
                "img_path": f"image_{name_index}_{text_index}.jpg"
            })
            red_zone_x = (min(quad[0], red_zone_x[0]), max(quad[2], red_zone_x[1]))
            red_zone_y = (min(quad[1], red_zone_y[0]), max(quad[3], red_zone_y[1]))
            crop_image = image.crop(quad)
            print(f"image_{name_index}_{text_index}.jpg")
            print(f"Text: {text}")
            print(quad)
            if (quad[0] < 0 or quad[0] > width or 
                quad[2] < 0 or quad[2] > width or 
                quad[1] < 0 or quad[1] > height or 
                quad[3] < 0 or quad[3] > height):
                print("Out of image !!!")
            crop_image.show()
            text_index += 1

        for i in range(no_large):
            text, polygon, quad = self.add_text_to_image(image, red_zone_x, red_zone_y, font_size_range='large', add_type = add_type)
            if text == None:
                continue
            
            result_dec.append({
                "polygon": polygon,
                "bbox": quad,
                "bbox_label":1,
                "ignore": False
            })
            result_rec.append({
                "instances":[{
                    "text": text
                }],
                "img_path": f"image_{name_index}_{text_index}.jpg"
            })
            red_zone_x = (min(quad[0], red_zone_x[0]), max(quad[2], red_zone_x[1]))
            red_zone_y = (min(quad[1], red_zone_y[0]), max(quad[3], red_zone_y[1]))
            crop_image = image.crop(quad)
            print(f"image_{name_index}_{text_index}.jpg")
            print(f"Text: {text}")
            print(quad)
            if (quad[0] < 0 or quad[0] > width or 
                quad[2] < 0 or quad[2] > width or 
                quad[1] < 0 or quad[1] > height or 
                quad[3] < 0 or quad[3] > height):
                print("Out of image !!!")
            crop_image.show()
            text_index += 1

        for i in range(no_extreme):
            text, polygon, quad = self.add_text_to_image(image, red_zone_x, red_zone_y, font_size_range='extreme_large', add_type = add_type)
            if text == None:
                continue
            
            result_dec.append({
                "polygon": polygon,
                "bbox": quad,
                "bbox_label":1,
                "ignore": False
            })
            result_rec.append({
                "instances":[{
                    "text": text
                }],
                "img_path": f"image_{name_index}_{text_index}.jpg"
            })
            red_zone_x = (min(quad[0], red_zone_x[0]), max(quad[2], red_zone_x[1]))
            red_zone_y = (min(quad[1], red_zone_y[0]), max(quad[3], red_zone_y[1]))
            crop_image = image.crop(quad)
            print(f"image_{name_index}_{text_index}.jpg")
            print(f"Text: {text}")
            print(quad)
            if (quad[0] < 0 or quad[0] > width or 
                quad[2] < 0 or quad[2] > width or 
                quad[1] < 0 or quad[1] > height or
                quad[3] < 0 or quad[3] > height):
                print("Out of image !!!")
            crop_image.show()
            text_index += 1

        print(f"image_{name_index}.jpg")
        print(f"Total: detec {len(result_dec)} and recog {len(result_rec)}")
        image.show()
        
        return None

    def add_text_to_document(
            self, 
            image,
            text_position,
            font_name,
            font_size: int,
            effect = None,
            ):
        # RANDOM BACKGROUND
        width, height = image.size
        draw = ImageDraw.Draw(image)

        # RANDOM TEXT TO GENERATE
        text = random.choice(self.word_list)

        font = ImageFont.truetype(
            os.path.join(self.font_collection_dir, font_name), 
            font_size
        )

        # Text length given the text, text_font, font_size
        text_leng = draw.textlength(text, font=font)

        # RANDOM FONT COLOR 
        shadow_color = "gray"
        shadow_offset = 2
        stroke_color = "white"
        stroke_width = 1

        # CHOOSE THE SUITABLE TEXT COLOR FOR BACKGROUND POSITION
        text_color = self._get_contrast_color_auto(image.getpixel(text_position), isDocument=True)
        
        # Check if the text_leng go out of the image !!!
        if (text_position[0] + text_leng >= width) or (text_position[1] + font_size*4/3 >= height):
            print("Out of image!!! Ignore this text, go to the next line")
            return None, None, None, draw.textlength(text, font=font)

        else:
            # BOX COLOR + TEXTBOX define 
            box_color = (255, 0, 0, 128)
            text_box = draw.textbbox(text_position, text, font=font)

            if effect == "shadow":
                text_box = (text_box[0], text_box[1], text_box[2] + shadow_offset, text_box[3] + shadow_offset)
            elif effect == "stroke":
                text_box = (
                    text_box[0] - stroke_width, 
                    text_box[1] - stroke_width, 
                    text_box[2] + stroke_width*2, 
                    text_box[3] + stroke_width*2)

            # CALCULATE AND DRAW BOUNDING BOX
                
            # use to draw the rectangle for visualize, use for testing only !!
            # draw.rectangle(text_box, outline=box_color, width=2)
            
            if effect == "shadow":
                self.__draw_text_with_shadow(
                    draw = draw,
                    position = text_position, 
                    text = text, 
                    text_color = text_color, 
                    font = font, 
                    shadow_color = shadow_color, 
                    shadow_offset = shadow_offset
                )
            elif effect == "stroke":
                self.__draw_text_with_stroke(
                    draw = draw,
                    position = text_position, 
                    text = text, 
                    text_color = text_color, 
                    font = font, 
                    stroke_color = stroke_color, 
                    stroke_width = stroke_width
                )
            else:
                draw.text(
                    xy = text_position, 
                    text = text, 
                    fill = text_color, 
                    font = font, 
                )
        
            polygon = [[text_box[0], text_box[1]],
                    [text_box[2], text_box[1]],
                    [text_box[2], text_box[3]],
                    [text_box[0], text_box[3]]]
            
            # (x1, y1, x2, y2) format
            quad = text_box

            return text, polygon, quad, text_leng

    def create_document_test(
        self,
        name_index,
        fontsize_collection = [0, 0, 0, 0],
        add_type = None,
    ):
        result_dec = []
        result_rec = []

        no_small, no_medium, no_large, no_extreme = fontsize_collection
        image_name = random.choice(self.background_list)
        image = Image.open(os.path.join(self.background_dir, image_name))
        width, height = image.size

        print(f"Image test: {name_index}, with width: {width} and height: {height}")

        text_index = 0

        start_position = 30
        text_position = (start_position, 0)
        text_leng = 0
        space_blank = 8

        font_size = random.choice(self.small)
        for i in range(no_small):
            # if the text is small, we don't use Stroke style for the text here
            text, polygon, quad, text_leng = self.add_text_to_document(
                image, text_position, font_size, add_type=add_type
            )
            text_position = (text_position[0] + text_leng + space_blank, text_position[1])
            if (text_position[0] >= width - start_position):
                text_position = (start_position, text_position[1] + font_size*4/3 + 2)

            if text_position[1] >= height:
                break
            
            if text == None:
                continue

            result_dec.append({
                "polygon": polygon,
                "bbox": quad,
                "bbox_label":1,
                "ignore": False
            })
            result_rec.append({
                "instances":[{
                    "text": text
                }],
                "img_path": f"image_{name_index}_{text_index}.jpg"
            })
            crop_image = image.crop(quad)
            print(f"image_{name_index}_{text_index}.jpg")
            # print(f"Text: {text}")
            # print(quad)
            if (quad[0] < 0 or quad[0] > width or 
                quad[2] < 0 or quad[2] > width or 
                quad[1] < 0 or quad[1] > height or 
                quad[3] < 0 or quad[3] > height):
                print("Out of image !!!")
            crop_image.show()
            text_index += 1

        font_size = random.choice(self.medium)
        for i in range(no_medium):
            text, polygon, quad, text_leng = self.add_text_to_document(
                image, text_position, font_size, add_type=add_type
            )
            text_position = (text_position[0] + text_leng + space_blank, text_position[1])
            if (text_position[0] >= width):
                text_position = (0, text_position[1] + font_size*4/3 + 2)            
            
            if text == None:
                continue
            
            result_dec.append({
                "polygon": polygon,
                "bbox": quad,
                "bbox_label":1,
                "ignore": False
            })
            result_rec.append({
                "instances":[{
                    "text": text
                }],
                "img_path": f"image_{name_index}_{text_index}.jpg"
            })
            crop_image = image.crop(quad)
            # print(f"image_{name_index}_{text_index}.jpg")
            # print(f"Text: {text}")
            # print(quad)
            if (quad[0] < 0 or quad[0] > width or 
                quad[2] < 0 or quad[2] > width or 
                quad[1] < 0 or quad[1] > height or 
                quad[3] < 0 or quad[3] > height):
                print("Out of image !!!")
            # crop_image.show()
            text_index += 1

        font_size = random.choice(self.large)
        for i in range(no_large):
            text, polygon, quad, text_leng = self.add_text_to_document(
                image, text_position, font_size, add_type=add_type
            )
            text_position = (text_position[0] + text_leng + space_blank, text_position[1])
            if (text_position[0] >= width):
                text_position = (0, text_position[1] + font_size*4/3 + 2)            
            
            if text == None:
                continue
            
            result_dec.append({
                "polygon": polygon,
                "bbox": quad,
                "bbox_label":1,
                "ignore": False
            })
            result_rec.append({
                "instances":[{
                    "text": text
                }],
                "img_path": f"image_{name_index}_{text_index}.jpg"
            })
            crop_image = image.crop(quad)
            # print(f"image_{name_index}_{text_index}.jpg")
            # print(f"Text: {text}")
            # print(quad)
            if (quad[0] < 0 or quad[0] > width or 
                quad[2] < 0 or quad[2] > width or 
                quad[1] < 0 or quad[1] > height or 
                quad[3] < 0 or quad[3] > height):
                print("Out of image !!!")
            # crop_image.show()
            text_index += 1

        font_size = random.choice(self.extreme_large)
        for i in range(no_extreme):
            text, polygon, quad, text_leng = self.add_text_to_document(
                image, text_position, font_size, add_type=add_type
            )
            text_position = (text_position[0] + text_leng + space_blank, text_position[1])
            if (text_position[0] >= width):
                text_position = (0, text_position[1] + font_size*4/3 + 2)            
            
            if text == None:
                continue
            
            result_dec.append({
                "polygon": polygon,
                "bbox": quad,
                "bbox_label":1,
                "ignore": False
            })
            result_rec.append({
                "instances":[{
                    "text": text
                }],
                "img_path": f"image_{name_index}_{text_index}.jpg"
            })
            crop_image = image.crop(quad)
            # print(f"image_{name_index}_{text_index}.jpg")
            # print(f"Text: {text}")
            # print(quad)
            if (quad[0] < 0 or quad[0] > width or 
                quad[2] < 0 or quad[2] > width or 
                quad[1] < 0 or quad[1] > height or
                quad[3] < 0 or quad[3] > height):
                print("Out of image !!!")
            # crop_image.show()
            text_index += 1

        print(f"image_{name_index}.jpg")
        print(f"Total: detec {len(result_dec)} and recog {len(result_rec)}")
        image.show()
        
        return None

    def create_dataset(
            self,
            folder,
            name,
            data = [[100, [10, 0, 0, 0]]],
            add_type = [None],
            ):
        os.makedirs(os.path.join(folder, name), exist_ok=True)
        os.makedirs(os.path.join(folder, name, "textdet"), exist_ok=True)
        os.makedirs(os.path.join(folder, name, "text_crop"), exist_ok=True)
        self.folder = folder
        self.name = name

        detectset = {
            "metainfo":{
                "dataset_type":"TextDetDataset",
                "task_name":"textdet",
                "category":[{
                    "id":0,
                    "name":"text"
                }]
            },
            "data_list":[]
            }
        recogset = {
            "metainfo":{
                "dataset_type":"TextRecogDataset",
                "task_name":"textrecog"
            },
            "data_list":[]
            }
        
        image_id = 0
        for config in data:
            for i in tqdm(range(config[0]), desc = f"Create the subset: {config}"):
                result_dec, width, height, result_rec = self.create_image_data(
                    image_id,
                    fontsize_collection=config[1],
                    add_type = random.choice(add_type),
                )
                detectset["data_list"].append({
                    "instances": result_dec,
                    "img_path": f"image_{image_id}.jpg",
                    "height": height,
                    "width": width,
                })
                recogset["data_list"] += (result_rec)
                image_id += 1

        with open(os.path.join(folder, name, "det_train.json"), 'w') as f:
            json.dump(detectset, f)
        with open(os.path.join(folder, name, "rec_train.json"), 'w') as f:
            json.dump(recogset, f)

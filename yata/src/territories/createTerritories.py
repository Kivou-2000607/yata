from PIL import Image
import json

# get territories properties
with open('territories.json', 'r') as f:
    terr = json.load(f)

min_x = 10000.0
min_y = 10000.0
max_x = 0.0
max_y = 0.0
for k, v in terr.items():
    # print(k, v)
    min_x = min(min_x, float(v["coordinate_x"]))
    max_x = max(max_x, float(v["coordinate_x"]))
    min_y = min(min_y, float(v["coordinate_y"]))
    max_y = max(max_y, float(v["coordinate_y"]))
    # print(f"Territory {k}")

print(f"min_x = {min_x}")
print(f"max_x = {max_x}")
print(f"min_y = {min_y}")
print(f"max_y = {max_y}")


# get image properties
citymap = Image.open("citymap.png")
map_x = citymap.size[0]
map_y = citymap.size[1]

print(f"map_x = {map_x}")
print(f"map_y = {map_y}")

ratio_x = map_x / float(max_x)
ratio_y = map_y / float(max_y)

print(f"ratio_x = {ratio_x}")
print(f"ratio_y = {ratio_y}")

tile_size = 50
for k, v in terr.items():
    x = int(float(v["coordinate_x"]) * ratio_x)
    y = int(float(v["coordinate_y"]) * ratio_x)
    # tile = Image.new('RGBA', (40, 40), color=tuple((0, 0, 0, 0)))
    left = min(max(x - tile_size//2, 0), map_x)
    top = min(max(y - tile_size//2, 0), map_y)
    crop = (left, top, left + tile_size, top + tile_size)
    print(f'Territory {k}: {x}x{y} {crop}')
    tmp = citymap.crop(crop)
    tmp.save(f"territories/{k}.png")
    # break

# xNames = [4, 5, 6, 7, 8, 9, 10, 11]
# yNames = [6, 7, 8, 9]
# tileSize = 228
# xSize = tileSize * len(xNames)
# ySize = tileSize * len(yNames)
#
# # create image background
# background = tuple((0, 0, 0, 0))
# img = Image.new('RGBA', (xSize, ySize), color=background)
#
# for i, x in enumerate(xNames):
#     for j, y in enumerate(yNames):
#         imFile = f'4__{x}_{y}_.png'
#         tile = Image.open(imFile)
#         tile = tile.convert("RGBA")
#
#         xPos = i * tileSize
#         yPos = j * tileSize
#         print(imFile)
#         img.paste(tile, (xPos, yPos), mask=tile)
#
# crop = img.crop((130, 0, xSize-130, ySize))
# crop.save("citymap.png")
# w, h = crop.size
# print("Size: {} x {}".format(2 * (228 - 130) + 6 * 228, 4 * 228))
# print("Size: {}".format(crop.size))
#
# print("Size: {} x {}".format( w / 2, h / 2 ))
# print("Size: 650 x {}".format( 650 / w * h ))

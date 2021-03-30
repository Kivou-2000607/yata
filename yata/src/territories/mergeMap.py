
from PIL import Image
#from PIL import ImageDraw
#from PIL import ImageFont


xNames = [4, 5, 6, 7, 8, 9, 10, 11]
yNames = [6, 7, 8, 9]
tileSize = 228
xSize = tileSize * len(xNames)
ySize = tileSize * len(yNames)

# create image background
background = tuple((0, 0, 0, 0))
img = Image.new('RGBA', (xSize, ySize), color=background)

for i, x in enumerate(xNames):
    for j, y in enumerate(yNames):
        imFile = f'4__{x}_{y}_.png'
        tile = Image.open(imFile)
        tile = tile.convert("RGBA")

        xPos = i * tileSize
        yPos = j * tileSize
        print(imFile)
        img.paste(tile, (xPos, yPos), mask=tile)

crop = img.crop((130, 0, xSize-130, ySize))
crop.save("citymap.png")
w, h = crop.size
print("Size: {} x {}".format(2 * (228 - 130) + 6 * 228, 4 * 228))
print("Size: {}".format(crop.size))

print("Size: {} x {}".format( w / 2, h / 2 ))
print("Size: 650 x {}".format( 650 / w * h ))

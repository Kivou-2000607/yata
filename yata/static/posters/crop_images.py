# import os


def crop_image(crop, input, output):
    from PIL import Image

    # Download Image:
    im = Image.open(input + ".png")

    # Check Image Size
    # im_size = im.size

    # Define box inside image
    left = crop[0]
    top = crop[1]
    width = crop[2]
    height = crop[3]

    # Create Box
    box = (left, top, left + width, top + height)

    # Crop Image
    area = im.crop(box)
    # area.show()

    # Save Image
    area.save(output + ".png", "PNG")
    # area.rotate(90, expand=True).save("img/"+output+"_r.png", "PNG")


# for i, id in enumerate([81, 82, 83, 84, 166, 167, 168, 169, 170, 171, 172]):
for branch in range(8):
    for type in range(5):
        crop_image([10+100*branch, 8+100*type, 80, 80], "tier_unlocks", "tier_unlocks_b{}_t{}".format(branch, type))

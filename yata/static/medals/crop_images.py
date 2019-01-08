import os

def crop_image(crop, input, output):
    from PIL import Image

    # Download Image:
    im = Image.open(input+".png")

    # Check Image Size
    im_size = im.size

    # Define box inside image
    left = crop[0]
    top = crop[1]
    width = crop[2]
    height = crop[3]

    # Create Box
    box = (left, top, left+width, top+height)

    # Crop Image
    area = im.crop(box)
    # area.show()

    # Save Image
    area.save("img/"+output+".png", "PNG")
    area.rotate(90, expand=True).save("img/"+output+"_r.png", "PNG")


# # commitment: donator
# for i, id in enumerate([210, 211, 212, 213, 214]):
#     crop_image([0+33*i, 0*65, 30, 63], "commitment_slices", str(id))
# # commitment: time in faction
# for i, id in enumerate([26, 27, 28, 29, 108, 109, 148, 149, 150, 151]):
#     crop_image([0+33*i, 1*65, 30, 63], "commitment_slices", str(id))
# # commitment: time with spouse
# for i, id in enumerate([74, 75, 76, 77, 78, 79, 80, 110, 111, 112, 113, 114, 115, 116, 156, 157, 158, 159, 160, 161, 162]):
#     crop_image([0+33*i, 2*65, 30, 63], "commitment_slices", str(id))
# # commitment: age
# for i, id in enumerate([225, 226, 227, 228, 229, 230, 231, 232, 234, 235]):
#     crop_image([0+33*i, 3*65, 30, 63], "commitment_slices", str(id))
#
# # rank
# for i, id in enumerate([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25]):
#     crop_image([0+33*i, 0*65, 30, 63], "rank_slice", str(id))
#
# # level
# for i, id in enumerate([34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53]):
#     crop_image([0+33*i, 0*65, 30, 63], "level_slice", str(id))
#
# # networth
# for i, id in enumerate([89, 90, 91, 92, 93, 94, 95, 96, 236, 237, 238, 239, 240, 241]):
#     crop_image([0+33*i, 0*65, 30, 63], "networth_slice", str(id))
#
# # miscellaneous: busts
# for i, id in enumerate([30, 31, 32, 33, 105, 106, 107]):
#     crop_image([0+33*i, 0*65, 30, 63], "miscellaneous_slice", str(id))
# # miscellaneous: finds
# for i, id in enumerate([204, 205, 206]):
#     crop_image([0+33*i, 1*65, 30, 63], "miscellaneous_slice", str(id))
# # miscellaneous: medical items
# for i, id in enumerate([198, 199, 200]):
#     crop_image([0+33*i, 2*65, 30, 63], "miscellaneous_slice", str(id))
# # miscellaneous: travel
# for i, id in enumerate([207, 208, 209]):
#     crop_image([0+33*i, 3*65, 30, 63], "miscellaneous_slice", str(id))
#
# # combat: wins
# for i, id in enumerate([174, 175, 176, 177, 178]):
#     crop_image([0+33*i, 0*65, 30, 63], "combat_slice", str(id))
# # combat: bounties
# for i, id in enumerate([201, 202, 203]):
#     crop_image([0+33*i, 1*65, 30, 63], "combat_slice", str(id))
# # combat: critical
# for i, id in enumerate([195, 196, 197]):
#     crop_image([0+33*i, 2*65, 30, 63], "combat_slice", str(id))
# # combat: defends
# for i, id in enumerate([179, 180, 181, 182, 183]):
#     crop_image([0+33*i, 3*65, 30, 63], "combat_slice", str(id))
# # combat: enemies escape
# for i, id in enumerate([187, 188, 189]):
#     crop_image([0+33*i, 4*65, 30, 63], "combat_slice", str(id))
# # combat: kill streak
# for i, id in enumerate([190, 191, 192, 193, 194]):
#     crop_image([0+33*i, 5*65, 30, 63], "combat_slice", str(id))
# # combat: respect earnt
# for i, id in enumerate([215, 216, 217, 218, 219, 220, 221, 222, 223, 224]):
#     crop_image([0+33*i, 6*65, 30, 63], "combat_slice", str(id))
# # combat: escape from foes
# for i, id in enumerate([184, 185, 186]):
#     crop_image([0+33*i, 7*65, 30, 63], "combat_slice", str(id))
#
# # crime: auto theft
# for i, id in enumerate([69, 70, 71, 72, 73, 102, 103, 104, 121, 122, 123, 124, 133, 134, 135, 136, 137, 138, 139, 140, 141]):
#     crop_image([0+33*i, 0*65, 30, 63], "crime_slices", str(id))
# # crime: computer
# for i, id in enumerate([54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 142, 143, 144, 145, 146, 147]):
#     crop_image([0+33*i, 1*65, 30, 63], "crime_slices", str(id))
# # crime: drug
# for i, id in enumerate([85, 86, 87, 88, 152, 153, 154, 155]):
#     crop_image([0+33*i, 2*65, 30, 63], "crime_slices", str(id))
# crime: arson
# for i, id in enumerate([97, 98, 99, 173, 100, 101, 117, 118, 119, 120, 127, 128, 129, 130, 131, 132]):
#     crop_image([0+33*i, 3*65, 30, 63], "crime_slices", str(id))
# crime: murder
# for i, id in enumerate([64, 65, 66, 67, 68, 125, 126, 163, 164, 165]):
#     crop_image([0+33*i, 4*65, 30, 63], "crime_slices", str(id))
# crime:
for i, id in enumerate([81, 82, 83, 84, 166, 167, 168, 169, 170, 171, 172]):
    crop_image([0+33*i, 5*65, 30, 63], "crime_slices", str(id))

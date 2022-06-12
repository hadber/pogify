# makes your images more poggers

# in order to use this, you should have Pillow (i think?) installed
# try something like pip3 install Pillow

import argparse
import colorsys
import pathlib
import random
from PIL import Image, ImageChops, ImageDraw, ImageEnhance
# there are issues saving GIFS with transparency, see:
# https://github.com/python-pillow/Pillow/issues/4644
# https://github.com/python-pillow/Pillow/issues/4640
# as per 4640, issues are fixed in Pillow 9.0 which is yet to arrive to my package manager
# in the meantime, im using the fix from here:
# https://gist.github.com/egocarib/ea022799cca8a102d14c54a22c45efe0
from gifsavefix import save_transparent_gif

def pog_frame_phase3(frame):
    # TODO: ADD BLUR TO THE SIDE IT'S MOVING TO
    pass

# based on https://stackoverflow.com/questions/24874765/python-pil-shift-the-hue-and-saturation
# if anyone has any better solutions using stock python, please reach out, this is very slow
def pog_frame_phase2(frame, hue, fid, do_rainbow=False, rmove=None):
    mask = frame.copy()
    frame = frame.convert("HSV")
    # why use load? see here: https://pillow.readthedocs.io/en/stable/reference/PixelAccess.html
    mld = mask.load()
    ld = frame.load()
    width, height = frame.size

    for y in range(height):
        for x in range(width):
            # remove blacks from mask (eg outlines)
            r, g, b, a = mld[x,y]
            if a == 0:
                r = g = b = 0
            else:
                r = g = b = 255
            mld[x,y] = (r,g,b,a)

            h,s,v = ld[x,y]
            if(do_rainbow):
                h = int((((y + rmove) / height) * 255) % 255)
                s = int(((x / width) * 255) + 126 % 255)
            else:
                h = (h + hue) % 255
                s = (s + 50) if s + 50 > 255 else s + 50 
            ld[x,y] = (h,s,v)
    frame = frame.convert("RGBA")
    mask = mask.convert("L")
    frame.putalpha(mask)
    frame.save(f"frames/frame2_{str(fid)}.png", "PNG")
    return frame

def pog_frame_phase1(frame, shift, fid):
    width, height = frame.size
    xshift = int(width * (shift/100))
    yshift = int(height * (shift/100))
    x_offset = random.randint(-xshift, xshift)
    y_offset= random.randint(-yshift, yshift)
    frame = ImageChops.offset(frame, x_offset, y_offset)
    xstart, xend = (0, x_offset) if x_offset > 0 else (width+x_offset, width)
    ystart, yend = (0, y_offset) if y_offset > 0 else (height+y_offset, height)
    frame.paste((0, 0, 0, 0), (xstart, 0, xend, height))
    frame.paste((0, 0, 0, 0), (0, ystart, width, yend))
    frame.save(f"frames/frame1_{str(fid)}.png", "PNG")
    return frame

def init_parser():
    parser = argparse.ArgumentParser(description="Makes images poggers. Don't touch the options if you're unsure.  All the intermediary frames that were generated are found under the frames/ directory.")

    parser.add_argument("-i", "--image", help="Path to image that needs pogifying", 
        metavar="img", required=True, type=pathlib.Path)
    parser.add_argument("-o", "--output", help="Path to where the image should be saved (default output.gif)", 
        metavar="img", default="output.gif", type=pathlib.Path)
    parser.add_argument("-f", "--frames", help="Number of frames (default: 12)", 
        metavar="n", default=12, type=int)
    parser.add_argument("-d", "--duration", help="Time in ms between frames (default: 30)", 
        metavar="ms", default=50, type=int)
    parser.add_argument("-m", "--move", help="Offset percentage in both direction (default: 33)",
        metavar="p", default=33, type=int)
    parser.add_argument("-r", "--rainbowify", help="Adds a rainbow hue shift. Currently if this is enabled, everything else is disabled.",
        action=argparse.BooleanOptionalAction)
    parser.add_argument("-s", "--shiny", help="Makes the image change colours in a cool way.",
        action=argparse.BooleanOptionalAction)
    return parser.parse_args()

if __name__ == "__main__":
    args = init_parser()
    im = Image.open(args.image)
    hues = sorted(random.sample(range(-360, 360), args.frames))
    frames = []

    #if args.shiny:
    #    all_colors = 
    #    pass


    for i in range(args.frames):
        if args.shiny:

            frames.append(frame)
        elif args.rainbowify:
            amount = im.height / args.frames
            rframe = pog_frame_phase2(im, None, i, True, (i*amount))
            frames.append(rframe)
        else:
            poggers_frame = pog_frame_phase1(im, args.move, i)
            poggers_frame = pog_frame_phase2(poggers_frame, hues[i], i)
            frames.append(poggers_frame)
        print(f"Processed frame {i+1}/{args.frames}")
    save_transparent_gif(frames, args.duration, args.output)
#    im.save(fp=args.output, format="GIF", append_images=frames,
#                   save_all=True, duration=args.duration, loop=0)
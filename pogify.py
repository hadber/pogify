# makes your images more poggers

# in order to use this, you should have Pillow (i think?) installed
# try something like pip3 install Pillow

import argparse
import pathlib
import random
import math
from colorsys import rgb_to_hsv
from PIL import Image, ImageChops, ImageDraw, ImageEnhance
# there are issues saving GIFS with transparency, see:
# https://github.com/python-pillow/Pillow/issues/4644
# https://github.com/python-pillow/Pillow/issues/4640
# as per 4640, issues are fixed in Pillow 9.0 which is yet to arrive to my package manager
# in the meantime, im using the fix from here:
# https://gist.github.com/egocarib/ea022799cca8a102d14c54a22c45efe0
from gifsavefix import save_transparent_gif
from pog_cluster import save_palette, get_dominant_colors

def pog_frame_phase3(frame):
    # TODO: ADD BLUR TO THE SIDE IT'S MOVING TO
    pass

def _rainbow_frame(frame, pos, col, rmove):
    width, height = frame.size
    h, s, v = col
    x, y = pos
    h = int((((y + rmove) / height) * 255) % 255)
    s = int(((x / width) * 255) + 126 % 255)
    return h, s, v

def _pog_frame(frame, pos, col, hue):
    h, s, v = col
    h = (h + hue) % 255
    s = (s + 50) if s + 50 > 255 else s + 50 # this makes no sense wtf was i doing here
    return h, s, v

def _shiny_frame(frame, pos, col, data):
    main_color = data[0]
    hue = data[1]
    h, s, v = col
    cutoff = 0.48

    dist = calc_hsv_dist(main_color, col)
    if dist > cutoff:
        return h, s, v

    h = int((h+hue) % 255)
    #s = int((i * amount) + 126 % 255)
    return h, s, v

def calc_hsv_dist(col1, col2):
    # what's this?
    # https://stackoverflow.com/questions/35113979/calculate-distance-between-colors-in-hsv-space

    h0, s0, v0 = tuple(i/255. for i in col1)
    h1, s1, v1 = tuple(i/255. for i in col2)

    dh = min(abs(h1-h0), 1-abs(h1-h0))
    ds = abs(s1-s0)
    dv = abs(v1-v0)

    return (dh**2 + ds**2 + dv**2) ** (1/2)


# based on https://stackoverflow.com/questions/24874765/python-pil-shift-the-hue-and-saturation
# if anyone has any better solutions using stock python, please reach out, this is rather slow
def pog_frame_general(frame, fid, func, data):
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
            h,s,v = func(frame, (x, y), (h, s, v), data)

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
    parser.add_argument("-k", "--clusters", help="Amount of dominant colours to be extracted (with --shiny)",
        metavar="k", default=3, type=int)
    return parser.parse_args()

if __name__ == "__main__":
    args = init_parser()
    im = Image.open(args.image)
    hues = sorted(random.sample(range(-360, 360), args.frames))
    frames = []

    if args.shiny:
        dominant_colors = get_dominant_colors(im, args.clusters)
        save_palette(im, dominant_colors, str(args.output).replace(".gif", "_palette.png"))
        h,s,v = rgb_to_hsv(dominant_colors[-1][0]/255., dominant_colors[-1][1]/255., dominant_colors[-1][2]/255.) # main_color should be in HSV colorspace
        main_color = tuple(pt*255 for pt in (h,s,v))
        hues = range(0, 255, int(255/args.frames))

    for i in range(args.frames):
        if args.shiny:
            poggers_frame = pog_frame_general(im, i, _shiny_frame, data=(main_color, hues[i]))
        elif args.rainbowify:
            amount = im.height / args.frames
            poggers_frame = pog_frame_general(im, i, _rainbow_frame, data=(i*amount))
        else:
            poggers_frame = pog_frame_phase1(im, args.move, i)
            poggers_frame = pog_frame_general(poggers_frame, i, _pog_frame, data=hues[i])
        frames.append(poggers_frame)
        print(f"Processed frame {i+1}/{args.frames}")
    if(len(frames) > 1):
        save_transparent_gif(frames, args.duration, args.output)
#    im.save(fp=args.output, format="GIF", append_images=frames,
#                   save_all=True, duration=args.duration, loop=0)
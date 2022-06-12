# a very simple k means (weighted) clustering algorithm implementation
# along with other things one might need
# inspired from here
# https://www.analyticsvidhya.com/blog/2016/11/an-introduction-to-clustering-and-different-methods-of-clustering/


import random
from PIL import Image, ImageDraw
from functools import reduce


def get_centroid(cluster):
    new_center = reduce(lambda a,b: tuple(item1 + item2 for item1, item2 in zip(a, b)), cluster)
    return tuple([x / len(cluster) for x in new_center])

def cluster_colors(img, k):
    # each cluster is a dominant color
    clusters = [[] for _ in range(k)] # c[0] -> cluster 1
    centroids = [(0, 0, 0)] * k # each cluster has a centroid; c[0] has centroid[0]
    
    all_pts = _group_colours(img) # every color is a data point in 3D space

    for pt in all_pts:
        # init by adding all points to a random cluster
        assigned_cluster = random.randint(0, k-1)
        clusters[assigned_cluster].append(pt)
#        print(f"{pt} assigned to cluster {assigned_cluster} which is now {clusters[assigned_cluster]}")
    for _ in range(100):

        for i in range(k):
            centroids[i] = get_centroid(clusters[i])

        new_clusters = [[] for _ in range(k)] # never again initalize stuff like this - [[]] * k
        for ptr, ptg, ptb in all_pts:    
            min_dist = 10000 # since the space is a 255 cube, the distance can't be too large, right?
            cid = None
            for cr, cg, cb in centroids:
                dist = (((cr-ptr) ** 2) + ((cg-ptg) ** 2) + ((cb-ptb) ** 2)) ** (1/2)
                if(min_dist > dist):
                    min_dist = dist
                    cid = centroids.index((cr, cg, cb))
            new_clusters[cid].append((ptr, ptg, ptb))
        clusters = new_clusters
    return centroids

#    for g in clusters:
#        print(g, "\n\n\n\n")

def _group_colours(img):
    ld = img.load()
    col_dict = {}

    width, height = img.size

    for y in range(height):
        for x in range(width):
            ccol = ld[x, y]
            # apparently this breaks if the image is 16x16, 
            # any thoughts why are highly appreciated
            r, g, b, a = ccol

            if(a <= 200 or r <= 20 or g <= 20 or b <= 20):
                # this is a black
                continue

            avg = (r + g + b) / 3
            if(abs(r - avg) <= 10 and abs(g - avg) <= 10 and abs(b - avg) <= 10):
                # this is a gray or white
                continue

            rbgcol = (r, g, b) # no need for alpha, as we mostly got rid of them
            if rbgcol in col_dict:
                col_dict[rbgcol] += 1
            else:
                col_dict[rbgcol] = 1
    return col_dict

k = 5

im = Image.open("test/shiny/gangweed.png")
dominant_colors = cluster_colors(im, k)

width, height = im.size
palette_size = int(height * 0.1)
new_im = Image.new(im.mode, size = (width, height + palette_size))
new_im.putdata(im.getdata())

draw = ImageDraw.Draw(new_im)
y_avg = int(palette_size/2)
x_offset = int(width/k + 1)
print(x_offset)
for i in range(len(dominant_colors)):
    g = tuple([int(c) for c in dominant_colors[i]])
#    dominant_colors[i] = g
    draw.line([((k - i) * x_offset, height + y_avg), (0, height +  y_avg)], fill = g, width=palette_size)






#draw.line((0,0) + im.size, fill = dominant_colors[0], width=3)



new_im.save("test/shiny/gangweed_palette.png")


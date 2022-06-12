# a very simple k means (weighted) clustering algorithm implementation
# along with other things one might need
# inspired from here
# https://www.analyticsvidhya.com/blog/2016/11/an-introduction-to-clustering-and-different-methods-of-clustering/


import random
from PIL import Image, ImageDraw
from functools import reduce

class Cluster():

    def __init__(self):
        self.cluster = {}
        self.centroid = (0, 0, 0)
        self.data_count = 0

    # add a color and how many times that color appears
    # so that we could do a weighted clustering and thus
    # save us a tiny bit of time from processing the
    # same color multiple times
    def add(self, color, amount):
        self.data_count += amount

        if color in self.cluster:
            self.cluster[color] += 1
        else:
            self.cluster[color] = 1

    def remove(self, color):
        self.data_count -= self.cluster[color]
        self.cluster.pop(color)

    def calc_centroid(self):
        print(len(self.cluster))
        new_center = reduce(lambda a,b: tuple((item1 + item2) * self.cluster[b] for item1, item2 in zip(a, b)), list(self.cluster))
        self.centroid = tuple([x / self.data_count for x in new_center])
        print(self, self.centroid)

    def get_centroid(self):
        return self.centroid

    def has_color(self, color):
        return color in self.cluster

def cluster_colors(img, k):
    # each centroid is a dominant color
    clusters = [Cluster() for _ in range(k)] # c[0] -> cluster 1 
    all_pts = _group_colours(img) # every color is a data point in 3D space
    centroids = set()

    for pt in all_pts:
        # init by adding all points to a random cluster
        assigned_cluster = random.randint(0, k-1)
        clusters[assigned_cluster].add(pt, all_pts[pt])

    # we leave it at 100 in case there is something
    # wrong so we don't loop forever and ever and ever
    for lo in range(100):
        old_centroids = centroids.copy()
        for cluster in clusters:
            cluster.calc_centroid()
            centroids.clear()
            centroids.add(cluster.get_centroid())

        # both sets contain the same centroids
        if old_centroids == centroids:
            print(f"I broke after {lo} tries!")
            break

        #new_clusters = [[] for _ in range(k)] # never again initalize stuff like this - [[]] * k
        for color in all_pts:   
            ptr, ptg, ptb = color
            min_dist = 10000 # since the space is a 255 cube, the distance can't be too large, right?
            # turns out, max distance is around ~4-5k
            new_cluster = None
            for cluster in clusters:
                cr, cg, cb = cluster.get_centroid()
                dist = (((cr-ptr) ** 2) + ((cg-ptg) ** 2) + ((cb-ptb) ** 2)) ** (1/2)
                if(min_dist > dist):
                    min_dist = dist
                    new_cluster = cluster

#            for c in clusters:
#                print(f"Cluster {c} contains color {color}: {c.has_color(color)}")
            old_cluster = next((cluster for cluster in clusters if cluster.has_color(color)), None)
            #print(old_cluster == new_cluster)
            if not old_cluster == new_cluster:
                new_cluster.add(color, old_cluster.cluster[color])
                old_cluster.remove(color)

            #new_clusters[cid].append((ptr, ptg, ptb))
        #clusters = new_clusters
    return clusters

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
            if(abs(r - avg) <= 15 and abs(g - avg) <= 15 and abs(b - avg) <= 15):
                # this is a gray or white
                continue

            rbgcol = (r, g, b) # no need for alpha, as we mostly got rid of them
            if rbgcol in col_dict:
                col_dict[rbgcol] += 1
            else:
                col_dict[rbgcol] = 1
    return col_dict

k = 3

im = Image.open("test/shiny/gangweed.png")
clusters = cluster_colors(im, k)
dominant_colors = [x.get_centroid() for x in clusters]
#print(clusters, dominant_colors)

width, height = im.size
palette_size = int(height * 0.1)
new_im = Image.new(im.mode, size = (width, height + palette_size))
new_im.putdata(im.getdata())

draw = ImageDraw.Draw(new_im)
y_avg = int(palette_size/2)
x_offset = int(width/k + 1)

for i in range(len(dominant_colors)):
    g = tuple([int(c) for c in dominant_colors[i]])
    draw.line([((k - i) * x_offset, height + y_avg), (0, height +  y_avg)], fill = g, width=palette_size)

new_im.save("test/shiny/gangweed_palette.png")


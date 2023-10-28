from .canny import *

def main(filename, reduction, r_params, max_dist, fuse_dist, bw_thresh):
    new_img = Image(filename, 60, 150, bw_thresh)

    new_img.make_edges()

    new_img.edge_reduce(reduction, r_params)

    new_img.fuse_ends(max_dist)
    new_img.close_loops(max_dist)
    new_img.keep_loops()
    new_img.fuse_points(fuse_dist)
    new_img.remove_small_polygons(fuse_dist)
    new_img.final_processing()

    new_img.draw_edges()

    return [new_img.format_paths(), new_img.get_original()]

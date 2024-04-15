# K Means Clustering
\***Originally written as a class, the implementation has now been refactored to be function-based.**\*


A repository documenting the implementation of k-Means clustering in Python. Usage examples can be found in the `tests` directory.


The thing that makes this k-means clustering module different from others is that it allows the user to specify the number of dimensions to use for the clustering operation.

For example, given some data where each element is of form 
```python
# Each element would actually be a Numpy array, but the following uses lists for readability.
[
  [1, 2, 3, 4, 5],
  [4, 6, 7, 8, 2],
  ...
]
```
specifying `ndim=3` will result in only the first three elements of each data point being used for each operation.
This is useful for maintaining data association where it otherwise would be shuffled. An example of this is found in my implementation of image segmentation (`segmentation.py`) in this same project.
Other examples of use could be for maintaining data association in object detection elements. Given some 
```python
[xmin, ymin, xmax, ymax, conf, label]  # [bounding box, conf, label]
```
we may want to cluster the data solely on bounding box information while also maintaining the confidence intervals for each detection for further processing.


## k-means Animation

Using the `view_clustering` function

### 2-D Case (Smallest Threshold Possible)

[kmeans2D_animate.webm](https://github.com/tjdwill/KMeans_Clustering/assets/118497355/0584a4d1-268d-4785-b05e-319d54a28de1)

### 3-D Case (Threshold = 0.001)

[kmeans3D_animate.webm](https://github.com/tjdwill/KMeans_Clustering/assets/118497355/a542b606-0844-427e-bfef-243e6f1ceffc)

## Image Segmentation

Perform image segmentation based on color groups specified by the user.

Two options:

### Averaged Colors

k=4

![seg_groups04](https://github.com/tjdwill/KMeans_Clustering/assets/118497355/9b468213-6983-4c66-8f93-de6e58a736a1)

k=10

![seg_groups10](https://github.com/tjdwill/KMeans_Clustering/assets/118497355/91fc5e42-4c2e-49bf-a24f-9926565a1a6c)

### Random Colors

k=4

![seg_rand_groups04_cpy](https://github.com/tjdwill/KMeans_Clustering/assets/118497355/33cee3ba-0a7d-4c12-9f34-7c140376f24b)

## Developed With
* Python (3.12.1)
* Numpy (1.26.2) 
* Matplotlib (3.8.4)

However, I don't use any features that are specific to Python 3.12.

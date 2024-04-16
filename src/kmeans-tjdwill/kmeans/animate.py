"""
@author: tjdwill 
@date: 5 April 2024
@title: K-means Clustering Animation
@description:
    Animating k-means for 2-D and 3-D cases.
"""
from typing import Union
#-
from matplotlib import pyplot as plt
from matplotlib import colors
import matplotlib as mpl
import numpy as np
#-
from kmeans.base_funcs import _assign_clusters, _validate, _new_centroids, SMALLEST_THRESH


Clusterable = np.ndarray
Clusters = dict[int, Clusterable]
class MaxIterationError(Exception):
    """An exception to be raised when the maximum iteration tolerance is exceeded."""
    pass


colors: list = [color for color in colors.TABLEAU_COLORS.values()]
WRAP_FACTOR: int = len(colors)
SZ = 10
CENTROID_SZ = 2*SZ
def _draw(
        clusters: Clusters,
        centroids: Clusterable,
        ax_obj: mpl.axes.Axes,
        ndim: int,
        *,
        legend_loc: str = "best"
) -> None:
    """Draws the clusters onto the figure
    
    Args:
        clusters: The segmented data
        centroids: The centers of the clusters
        ax_obj: The axes object (from the figure)
        ndim: The number of dimensions
        legend_loc: Where to place the legend. Defaults to 'best'

    Returns:
        None
    """
    k = len(clusters)
    ax_obj.clear()
    # Get the data
    labels = ['Cluster {}'.format(i) for i in range(k)]

    ax_obj.grid(which="both")
    ax_obj.set(xlabel="X", ylabel="Y", title=f"$k$ = ${k}$")

    for key in clusters:
        cluster = clusters[key]
        if ndim == 2:
            x = cluster[:, 0]
            y = cluster[:, 1]
            cx, cy = centroids[key]

            ax_obj.scatter(
                x, y,
                s=SZ, c=colors[key%WRAP_FACTOR],
                label=labels[key], zorder=3,
            )
            ax_obj.scatter(
                cx, cy,
                s=CENTROID_SZ, c=colors[key%WRAP_FACTOR], edgecolors='k',
                zorder=3,
            ) 
        else:
            x = cluster[:, 0]
            y = cluster[:, 1]
            z = cluster[:, 2]
            cx, cy, cz = centroids[key]
            ax_obj.scatter(
                x, y, z,
                s=SZ, c=colors[key%WRAP_FACTOR],
                label=labels[key], zorder=3,
            )
            ax_obj.scatter(
                cx, cy, cz,
                s=CENTROID_SZ, c=colors[key%WRAP_FACTOR], edgecolors='k',
                zorder=5,
            )
    else:
        ax_obj.legend(loc=legend_loc)
        plt.pause(0.01) 
        plt.show(block=False)
        return


def view_clustering(
        data: Union[Clusterable, list[Clusterable], tuple[Clusterable]],
        k: int,*,
        initial_means: Union[Clusterable, list[Clusterable], tuple[Clusterable]] = None,
        ndim: int = None,
        tolerance: float = SMALLEST_THRESH,
        max_iterations: int = 250,
) -> tuple[Clusters, np.ndarray, mpl.figure.Figure]:
    """Perform and display k-means clustering
    
    Args:
        data: The input data
            This data should be formatted in terms of row vectors.
            Given a flat numpy array
            data=np.array([0, 1, 2, 3, 4]), do the following:
                `data = data.reshape(data.shape[-1], -1)`
            or  `data = data[..., np.newaxis]`
            It should make each point a row entry:
                [[0], [1], [2], [3], [4]]
            Data of higher dimensions (ex. a multi-channeled image)
            should be flattened using the number of indices
            for the deepest dimension. So, for an image with shape
            (480, 640, 3), run
                `data = data.reshape(-1, data.shape[-1])`
        k: Amount of clusters
        initial_means: The initial cluster centroids
            Default: None -> Means are randomly selected from data 
            with uniform probability
        ndim: Dimension limit for clustering; 
            Default: None -> selects the ndim based on data length
        tolerance: Controls the completion criteria. Lower -> more iterations.
            Default: 20*eps for np.float64
        max_iterations: The counter timeout. Function raises exception if exceeded.
            Default: 250

    Returns:
        ({int: np.np.ndarray}, np.np.ndarray, matplotlib.figure.Figure): 
            clustered data, cluster centroids, Matplotlib Figure

    Raises:
        MaxIterationError: Raise this exception if the clustering doesn't
            converge before reaching the `max_iterations` count.
    """
    data, initial_means, ndim = _validate(
        data,
        k, 
        initial_means=initial_means, 
        ndim=ndim,
        tolerance=tolerance, 
        max_iterations=max_iterations
    )

    # Handle legend placement for large datasets
    if len(data) > 100000:
        legend_loc = 'upper right'
    else:
        legend_loc  = 'best'

    clusters, old_centroids = {}, initial_means
    # 2D or 3D plots?
    if ndim==2:
        fig, ax = plt.subplots()
    elif ndim == 3:
        fig = plt.figure()
        ax = fig.add_subplot(projection='3d')
    else:
        raise ValueError(
            "Only 2-D or 3-D may be animated. "
            "Use the `cluster` function for other dimensioned data."
        )

    for _ in range(max_iterations):
        clusters = _assign_clusters(data, old_centroids)
        centroids = _new_centroids(clusters, ndim)
        _draw(clusters, centroids, ax, ndim, legend_loc=legend_loc)
        changes = np.linalg.norm(centroids - old_centroids, axis=1)  # Distance along each vector
        if any(np.where(changes > tolerance, True, False)):
            old_centroids = centroids
        else:
            ax = fig.get_axes()[0]
            ax.set(title=f"Clustering @ $k$=${k}$")
            return clusters, centroids, fig
    else:
        raise MaxIterationError("Iteration count exceeded.")            

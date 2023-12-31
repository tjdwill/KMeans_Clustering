# -*- coding: utf-8 -*-
"""
@author: Terrance Williams
@date: 26 October 2023
@description: A convenience class for simple image operations.
"""
from typing import ClassVar
import os
import cv2 as cv
import matplotlib.pyplot as plt
import numpy as np


class ImageHelper:
    """
    Purpose: A class to make typical OpenCV operations simpler for myself.

    How to use:
        Pass the target image's path name to the constructor.
    Example:
        - path = '~/images/pic01.png'
        - img = ImageHelper(path)
        - img.display()  # view the object

    Display np.ndarray images:

    Wraps a call to cv.imshow and cv.waitKey(1)
        - sample = np.random.randint(0, 255, size=(480, 640, 3))
        * Image.view_img(sample)

    Notable Features:
        - Colorspace conversions (to gray, RGB, and HSV)
        - Color Rebalancing via multiplicative constants
        - Feature matching example via OpenCV SIFT and ORB
        - Image transformations (rotation and translation) via OpenCV
        - Save a given np.ndarray image to generator image's directory*
        *Output directory is changeable.
    """

    # =================
    # Class Variables
    # =================

    # Incrementing this variable allows
    # the class to display multiple image windows.
    _img_label: ClassVar[int] = 0

    # ====================
    # Instance Variables
    # ====================
    in_path: str

    # =================
    # Initialization
    # =================
    def __init__(self, in_path):

        self._img_path = self._format_path(in_path)

        # check if image exists on system
        if not os.path.isfile(self._img_path):
            raise ValueError("ERROR: Image file does not exist.")

        # set output path
        self._output_dir, self._name = os.path.split(self._img_path)
        self._output_dir += '/'

        # Load image
        self._img_backup = cv.imread(self._img_path)
        assert self._img_backup is not None

    # ============
    # Properties
    # ============

    @property
    def output_dir(self):
        """
        The output directory of the image.
        Determines where operations are saved.
        """
        return self._output_dir

    @output_dir.setter
    def output_dir(self, path: str):
        if not path:
            raise ValueError('No path name provided.\n'
                             'Current output directory:\n"{}"'.
                  format(self.output_dir))

        new_path = self._format_path(path)
        if not os.path.isdir(new_path):
            raise ValueError('\nCannot set output directory;'
                             ' it does not exist.')

        else:
            # Formatting choice; makes image saving easier for users.
            if new_path[-1] != '/':
                new_path += '/'
            self._output_dir = new_path
            return

    @property
    def name(self):
        """
        Returns
        -------
        image_name: str
        """
        return self._name

    @property
    def img_backup(self) -> np.ndarray:
        """
        An untouched version of the passed image.

        Returns
        -------
        numpy.ndarray of image

        """
        return np.copy(self._img_backup)

    @property
    def size(self) -> tuple:
        """
        Returns
        -------
        tuple
           (height, width) in px.

        """
        height, width, _ = self._img_backup.shape
        return height, width

    # ===============
    # Class Methods
    # ===============

    # ::Public methods::

    @staticmethod
    def view_img(image: np.ndarray):
        """
        Displays an image passed to the class.

        Parameters
        ----------
        image : np.ndarray

        """
        if image is not None and isinstance(image, np.ndarray):
            cv.imshow("Image Class Display {}".format(Image._img_label), image)
            cv.waitKey(1)
            Image._img_label += 1
        else:
            raise ValueError("No image passed.")

    def display(self):
        """Displays the original image."""
        self._display(self._img_backup)

    def save(self, image: np.ndarray,
             name: str = None) -> bool:
        """
        Description
        -----------
            Save an image to the output directory
        Example
        -------
            img._save(img.img_backup, 'test.png')
        """

        # Name Check
        if not name:
            raise ValueError("Could not save image. No name given.")

        # Set return boolean
        is_success = False

        # try the save operation
        saving_path = self._output_dir + name
        try:
            print("Saving file: '{}'\n...".format(saving_path))
            cv.imwrite(saving_path, image)
        except Exception as e:
            print("\nFailed to save image. Check the path or extension.\n",
                  e, sep='\n')
            return is_success
        else:
            # write was successful
            print("Save successful.\n")
            is_success = True
            return is_success

    # Image Operations
    def cvt_color(self, conversion: str,
                  get_data: bool = False,
                  display: bool = True) -> np.ndarray:
        """
        Convert the images color space.

        Parameters
        ----------
        conversion : str
            The space to convert to (ex. HSV).
        get_data : bool, optional
            Whether to return the converted image as a numpy array.
            The default is False.
        display : bool, optional
            Display the converted image. The default is True.

        Raises
        ------
        ValueError

        Returns
        -------
        converted_img : np.ndarray
            The converted image.
        """
        if not display and not get_data:
            return np.array([])
        # Check conversion validity
        color_codes = {'gray': cv.COLOR_BGR2GRAY,
                       'HSV': cv.COLOR_BGR2HSV,
                       'RGB': cv.COLOR_BGR2RGB}
        valid_entries = [*color_codes.keys()]

        try:
            if conversion in valid_entries:
                pass
            else:
                raise ValueError('Incorrect Conversion Type.\nValid options:'
                                 '\n{}'.format(valid_entries))
        except (TypeError, AttributeError):
            print("Incorrect Entry. Please use a string.\nValid Entries:")
            print(valid_entries)
            raise

        # Implement conversion
        work_img = np.copy(self._img_backup)
        converted_img = cv.cvtColor(work_img, color_codes[conversion])

        # Boolean Actions
        if display:
            self._display(converted_img)
        if get_data:
            return converted_img

    def color_rebalance(self,
                        R_const: float,
                        G_const: float,
                        B_const: float,
                        display: bool = True,
                        get_data=False) -> np.ndarray:
        """
        Re-balances the color channels of the image based on provided factors.

        Parameters
        ----------
        R_const : float
            Red channel factor.
        G_const : float
            Green channel factor.
        B_const : float
            Blue channel factor.
        display : bool, optional
            Whether to show the image or not. The default is False.
        get_data :  bool, optional
            Return the modified image as an array or not.
        Raises
        ------
        ValueError
            Only insert non-negative numbers.

        Returns
        -------
        new_img : np.ndarray
            The rebalanced image.

        """
        if not display and not get_data:
            return np.array([])

        # Check inputs
        try:
            if R_const < 0 or G_const < 0 or B_const < 0:
                raise ValueError("Please insert non-negative numbers.")
        except TypeError:
            print("\nColor Re-balance Error: Please insert numbers.\n")
            return np.array([])

        constants = [B_const, G_const, R_const]
        # apply to image
        work_img = np.copy(self._img_backup)
        channels = list(cv.split(work_img))

        for i in range(len(constants)):
            channels[i] = (channels[i]*constants[i]).astype(np.uint8)

        # Channel validation
        # print([channels[i].dtype for i in range(len(channels))])

        new_img = cv.merge(channels)
        new_img = np.round(new_img).astype(np.uint8)

        # Display
        if display:
            self._display(new_img)
        if get_data:
            return new_img

    def get_color_space(self, duplicate_pixels: bool = False):
        """
        Parameters
        ----------
        duplicate_pixels : bool, optional
            Determines whether to keep duplicate pixels or not.
            The default is False.

        Returns
        -------
        points: list
            The [(R), (G), (B)] points of each pixel .

        """
        # Data containers

        # Fill data containers
        work_img = self.cvt_color('RGB', get_data=True, display=False)
        color_points = work_img.reshape(-1, 3)

        if not duplicate_pixels:
            # removes duplicates for uniform plotting.
            unique_points = np.unique(color_points, axis=0)  # For 2D array
            return unique_points
        else:
            return color_points

    def view_color_space(self, uniform: bool = False):
        """
        View color space of the image.

        Parameters
        ----------
        uniform : bool, optional
            Whether to plot the feature space with equal weighting.
            Returns a sample of the feature space otherwise.
            The default is False.
        """
        # Data containers
        if uniform:
            # Remove duplicates from color space
            points = self.get_color_space()

        else:
            points = self.get_color_space(duplicate_pixels=True)

        R, G, B = zip(*points)
        # Data manipulation
        # Get Unique Data

        # Plot Configuration
        fig = plt.figure()
        ax = fig.add_subplot(projection='3d')

        height, width, _ = self._img_backup.shape
        step = int(height * width / 2000)
        ticks = list(range(0, 250, 50))
        ticks.append(255)

        # Figure Axis settings
        ax.set(xlabel='R', ylabel='G', zlabel='B',
               xlim=(0, 255), ylim=(0, 255), zlim=(0, 255),
               xticks=ticks, yticks=ticks, zticks=ticks)

        # Plot the data
        name = os.path.splitext(self.name)[0]
        if uniform:
            ax.set_title("{}'s Feature Space".format(name))
            ax.scatter(R, G, B, color='k')
        else:
            ax.set_title("{}'s Sampled Feature Space".format(name))
            ax.scatter(R[::step], G[::step], B[::step], color='k')
        # Show plot
        plt.show()

    def transform(self, *,
                  translation_vals: np.ndarray = None,
                  angle: float = 0,
                  rotation_center: np.ndarray = None,
                  get_data: bool = False,
                  display: bool = True) -> np.ndarray:
        """
        Applies an affine transformation to the image using a combination
        of translation and rotation

        Parameters
        ----------

        translation_vals : np.ndarray, optional
            Translation Parameters [delta_x, delta_y].
            The default is [0,0].
        angle : float, optional
            Rotates about the image center in degrees.
            The default is 0.
        rotation_center: np.ndarray, optional
            An array containing the coordinates of the point of rotation.
            In [x,y] order.
        get_data : bool, optional
            Return the transformed image as a numpy array.
            The default is False.
        display : bool, optional
            Display the transformed image. The default is True.

        Returns
        -------
        transformed_img : np.ndarray

        """

        if not display and not get_data:
            return np.ndarray([])

        if translation_vals is None:
            translation_vals = np.zeros(2)

        transformed_img = np.copy(self._img_backup)

        # Generate transformation matrix
        t_x, t_y = translation_vals

        T_mat = np.array([[1, 0, t_x],
                          [0, 1, t_y],
                          [0, 0, 1]])

        rows, cols, _ = transformed_img.shape
        if rotation_center is not None:
            rot_x, rot_y = rotation_center.astype(np.float64)
        else:
            # Choose image center pixel
            rot_x, rot_y = ((cols-1)/2, (rows-1)/2)
        R_mat = cv.getRotationMatrix2D((rot_x, rot_y), angle, 1)
        R_mat = np.append(R_mat, [[0, 0, 1]], axis=0)
        M_matrix = T_mat @ R_mat
        M_matrix = M_matrix[0:2]

        # Apply transformation
        transformed_img = cv.warpAffine(transformed_img, M_matrix,
                                        (cols, rows))

        if display:
            self._display(transformed_img)
        if get_data:
            return transformed_img

    def SIFT(self, *, display: bool = True,
             in_color: bool = True, get_data: bool = False) -> list:
        """
        Performs SIFT matching on the image for a 90-degree rotation.

        Parameters
        ----------
        display : bool, optional
            Display output or not. The default is True.
        in_color : bool, optional
            Display in color or grayed. The default is True.
        get_data : bool, optional
            Return data in the form [matches, matched_img];
            Default False.

        Returns
        -------
        List with SIFT matches and the resulting image as a numpy array;
        Convenient for saving.
        """

        if not display and not get_data:
            return []

        # Get worker images
        work_img = np.copy(self._img_backup)
        ex_transform = self.transform(angle=90,
                                      get_data=True,
                                      display=False)
        gray = self.cvt_color('gray', get_data=True, display=False)
        gray_transformed = cv.cvtColor(ex_transform, cv.COLOR_BGR2GRAY)

        # Begin SIFT
        # Source: https://docs.opencv.org/3.4/da/df5/tutorial_py_sift_intro.html #noqa
        sift = cv.SIFT.create()
        kp1_1, des1_1 = sift.detectAndCompute(gray, None)
        kp1_2, des1_2 = sift.detectAndCompute(gray_transformed, None)

        # BFMatcher with default params
        bf = cv.BFMatcher()
        matches = bf.knnMatch(des1_1, des1_2, k=2)

        # Apply ratio test
        good = []
        for m, n in matches:
            if m.distance < 0.75*n.distance:
                good.append([m])

        # Draw matches
        SIFT_out = cv.drawMatchesKnn(
            gray, kp1_1,
            gray_transformed, kp1_2,
            good, None,
            flags=cv.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS
        )

        SIFT_out_color = cv.drawMatchesKnn(
            work_img, kp1_1,
            ex_transform, kp1_2,
            good, None,
            flags=cv.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS
        )
        print(f'SIFT matches: {len(good)}')

        # Display and/or return data
        if in_color:
            if display:
                self._display(SIFT_out_color)
            if get_data:
                return [good, SIFT_out_color]
        else:
            if display:
                self._display(SIFT_out)
            if get_data:
                return [good, SIFT_out]

    def ORB(self, *, display: bool = True, keepPercent: float = 0.5,
            in_color: bool = True,
            get_data: bool = False) -> list:
        """
        Performs ORB matching on the image for a 90-degree rotation.

        Parameters
        ----------
        display : bool, optional
            Display the output image or not.
            The default is True.
        keepPercent: float, optional
            Percentage of best matches to keep.
            Defaults to 0.5
        in_color : bool, optional
            Display in color or grayed. The default is True.
        get_data : bool, optional
            Return data in the form [matches, matched_img];
            Default False.

        Returns
        -------
        ORB image as an numpy array; Convenient for saving.

        """

        if not display and not get_data:
            return []

        # check input
        if keepPercent > 1:
            keepPercent = 1
        elif keepPercent < 0:
            print("Invalid input; Defaulting to 0.5")
            keepPercent = 0.5

        # Get worker images
        work_img = np.copy(self._img_backup)
        ex_transform = self.transform(angle=90,
                                      get_data=True,
                                      display=False)
        gray = self.cvt_color('gray', get_data=True, display=False)
        gray_transformed = cv.cvtColor(ex_transform, cv.COLOR_BGR2GRAY)

        # Apply ORB
        # Source: https://docs.opencv.org/3.4/dc/dc3/tutorial_py_matcher.html
        orb = cv.ORB_create()

        kp2_1, des2_1 = orb.detectAndCompute(gray, None)
        kp2_2, des2_2 = orb.detectAndCompute(gray_transformed, None)

        bf2 = cv.BFMatcher(cv.NORM_HAMMING, crossCheck=True)
        ORB_matches = bf2.match(des2_1, des2_2)

        # Sort match descriptors in the order of their distance.
        ORB_matches = sorted(ORB_matches, key=lambda x: x.distance)
        keep = int(len(ORB_matches) * keepPercent)
        best_matches = ORB_matches[:keep]

        # Draw matches.
        ORB_out = cv.drawMatches(
            gray, kp2_1,
            gray_transformed, kp2_2,
            best_matches, None,
            flags=cv.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS
        )
        ORB_out_color = cv.drawMatches(
            work_img, kp2_1,
            ex_transform, kp2_2,
            best_matches, None,
            flags=cv.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS
        )

        print(f'Total ORB matches: {len(ORB_matches)}')
        print(f'Best ORB matches: {len(best_matches)}')

        # Display and/or return data
        if in_color:
            if display:
                self._display(ORB_out_color)
            if get_data:
                return [best_matches, ORB_out_color]

        else:
            if display:
                self._display(ORB_out)
            if get_data:
                return [best_matches, ORB_out]

    # ::Private methods::
    @staticmethod
    def _format_path(path):
        """

        Parameters
        ----------
        path : str
            The path of the input image.

        Returns
        -------
        new_path : str
            The properly-formatted path string for OpenCV. Should be
            platform-agnostic (Windows, Unix)
        """
        try:
            new_path = path.strip("'")
            new_path = new_path.strip('"')
            new_path = new_path.replace("\\", "/")  # For Windows pathing
            new_path = new_path.strip('//')
        except AttributeError:
            print("\nWrong Type; Please insert a string.")
            raise
        return new_path

    def _display(self, image: np.ndarray):
        """
        Displays the given image. Defaults to the original image.
        This method is private to prevent users from being able to display
        non-instance-origin-ed images.

        Meant for internal use (as in displaying output of a transformation)
        """
        # Default image to display
        if image is None:
            image = self.img_backup

        print("Press 'q' or 'ESC' to exit.")

        while True:
            cv.imshow("{}'s Output".format(os.path.splitext(self.name)[0]),
                      image)
            key = cv.waitKey(30)
            if key == 27 or key == ord('q'):
                break
        # Cleanup
        cv.destroyAllWindows()
        print("Closed.")
# ---

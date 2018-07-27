import vispy
import vispy.color
import vispy.scene
from vispy import scene
import vispy.app
import vispy.visuals
import numpy as np
import os
import TurntableCamera as tc


class twoClassesMap(vispy.color.colormap.BaseColormap):
    glsl_map = """
    vec4 threeclasses(float t) {
        if(t == 0){
            return vec4(0, 0, 0, 0);
        }
        else if (t == 1) {
            return vec4(0.8, 0.1, 0.1, 0.3);
        }
        else {
            return vec4(0.8, 0.1, 0.1, 0.3);
        }
    }
    """
    """
    t should take values in 0, 1, 2
    """

    def map(self, t):
        if isinstance(t, np.ndarray):
            return np.hstack([t, 0.1, 1-t, 1]).astype(np.float32)
        else:
            return np.array([t, 0.1, 1-t, 1], dtype=np.float32)


class FireMap(vispy.color.colormap.BaseColormap):
    colors = [(1.0, 1.0, 1.0, 0.0),
              (1.0, 1.0, 0.0, 0.05),
              (1.0, 0.0, 0.0, 0.1)]

    glsl_map = """
    vec4 fire(float t) {
        return mix(mix($color_0, $color_1, t),
                   mix($color_1, $color_2, t*t), t);
    }
    """


def show():
    vispy.app.run()


def get_two_views():
    """
    Get two views in order to plot two graphs/images in a consistent manner
    """
    canvas = vispy.scene.SceneCanvas(keys='interactive', title='plot3d', show=True)
    vb1 = scene.widgets.ViewBox(border_color='yellow', parent=canvas.scene, camera=tc.TurntableCamera())
    vb2 = scene.widgets.ViewBox(border_color='blue', parent=canvas.scene, camera=tc.TurntableCamera())

    grid = canvas.central_widget.add_grid()
    grid.padding = 6
    grid.add_widget(vb1, 0, 0)
    grid.add_widget(vb2, 0, 1)

    for view in vb1, vb2:
        view.camera = 'turntable'
        view.camera.fov = 100
        view.camera.distance = 0
        view.camera.elevation = 0
        view.camera.azimuth = 0

    vb1.camera.aspect = vb2.camera.aspect = 1
    vb1.camera.link(vb2.camera)

    return vb1, vb2



def plot3d(data, colormap = FireMap(), view=None):
    VolumePlot3D = vispy.scene.visuals.create_visual_node(vispy.visuals.VolumeVisual)
    # Add a ViewBox to let the user zoom/rotate
    # build canvas
    if view is None:
        canvas = vispy.scene.SceneCanvas(keys='interactive', title='plot3d', show=True)
        view = canvas.central_widget.add_view(camera=tc.TurntableCamera())
        view.camera = 'turntable'
        view.camera.fov = 0
        view.camera.distance = 7200
        view.camera.elevation = 31
        view.camera.azimuth = 0
        view.camera.depth_value = 100000000

    cc = (np.array(data.shape) // 2)
    view.camera.center = cc

    return VolumePlot3D(data.transpose([2, 1, 0]), method='translucent', relative_step_size=1.5,
                        parent=view.scene, cmap=colormap)


def reconstructionView(readdir, N):
    img = np.load(os.path.join(readdir, 'input_' + str(N) + '.npy'))
    output = np.load(os.path.join(readdir, 'output_' + str(N) + '.npy'))

    print("img", np.unique(img))
    print("output", np.unique(output))

    vb1, vb2 = get_two_views()
    plot3d(img, view=vb1)
    plot3d(output, view=vb2)
    show()


if __name__ == '__main__':

    readdir = 'logs/training270718_softcut2'
    N = 4800

    reconstructionView(readdir, N)

    input = np.load(os.path.join(readdir, 'input_' + str(N) + '.npy'))
    latent1 = np.load(os.path.join(readdir, 'latent1_' + str(N) + '.npy'))[3:37, 3:37, 3:37]
    latent2 = np.load(os.path.join(readdir, 'latent2_' + str(N) + '.npy'))[3:37, 3:37, 3:37]


    print(latent1.shape)

    print('latent1 min max', np.min(latent1), np.max(latent1))
    print('latent2 min max', np.min(latent2), np.max(latent2))

    vb1, vb2 = get_two_views()

    print(np.unique(latent1))
    plot3d(latent2, view=vb1)
    plot3d(input, view=vb2)
    show()
import colorsys
import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt


async def rgb_to_hsv(r, g, b):
    return colorsys.rgb_to_hsv(r / 255.0, g / 255.0, b / 255.0)


async def hsv_to_rgb(h, s, v):
    return tuple(int(i * 255) for i in colorsys.hsv_to_rgb(h, s, v))


async def get_color_triad(rgb):
    try:
        rgb.repace("'", "")
    except Exception:
        ...
    try:
        r = int(rgb.split(',')[0])
        if r == 0:
            r += 1
        g = int(rgb.split(',')[1])
        if g == 0:
            g += 1
        b = int(rgb.split(',')[2])
        if b == 0:
            b += 1
    except AttributeError:
        r = int(rgb[0])
        if r == 0:
            r += 1
        g = int(rgb[1])
        if g == 0:
            g += 1
        b = int(rgb[2])
        if b == 0:
            b += 1
    h, s, v = await rgb_to_hsv(r, g, b)

    h1 = (h + 1 / 3) % 1.0
    h2 = (h + 2 / 3) % 1.0

    color1 = await hsv_to_rgb(h, s, v)
    color2 = await hsv_to_rgb(h1, s, v)
    color3 = await hsv_to_rgb(h2, s, v)

    return [color1, color2, color3]


async def plot_color_triad(triad, user_id):
    try:
        fig, ax = plt.subplots(1, 3, figsize=(9, 3))
        for i, color in enumerate(triad):
            ax[i].imshow([[color]])
            ax[i].axis('off')
        plt.savefig(f'files/photos/{user_id}/triad.png')
        return 'succesfull'
    except Exception as _ex:
        print(_ex)
        return 'error'


async def rgb_result(color, user_id):
    triad = await get_color_triad(color)
    answer = await plot_color_triad(triad, user_id)
    return answer

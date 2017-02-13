from PIL import Image

class QRImg:
    height, width = 0, 0

    def __init__(self, path):
        self.im = Image.open(path)
        self.width = self.im.width
        self.height = self.im.height
        print(self.get_qrcode(self.get_cell()))

    # 计算每个方块的大小像素
    def get_cell_size(self, x, y, x2, y2):
        for j in range(x, x2):
            for i in range(y, y2):
                pix = self.im.getpixel((j, i))
                if pix == 255:
                    return j - x  # 每个黑色格子的像素点大小

    def get_cell(self):
        flag = 0
        for y in range(self.height):
            for x in range(self.width):
                pix = self.im.getpixel((x, y))
                if pix == 0 and flag == 0:  # 出现第一个黑色像素
                    x1 = x
                    flag = 1

                if pix == 255 and flag == 1:  # 出现第一个白色像素（意味着左上角的标记方块横向结束）
                    flag = 2
                    cell = self.get_cell_size(x1, x1, x, x)
                    return cell

    def get_qrcode(self, cell):
        height = int(self.height / cell)
        width = int(self.width / cell)
        code = ''
        for y in range(height):

            for x in range(width):
                pix = self.im.getpixel((x * cell, y * cell))
                if pix == 0:
                    code += '▇'
                if pix == 255:
                    code += '　'
            code += '\n'
        return code

def transform(self, x, y):
    # return self.transform_2D(x, y)
    return self.transform_perspective(x, y)


def transform_2D(self, x, y):
    return int(x), int(y)


def transform_perspective(self, x, y):
    linear_y = y * self.perspective_point_y / self.height
    if linear_y > self.perspective_point_y:
        linear_y = self.perspective_point_y

    diff_x = x - self.perspective_point_x
    diff_y = self.perspective_point_y - linear_y
    factor_y = diff_y / self.perspective_point_y
    factor_y = pow(factor_y, 4)

    transform_x = self.perspective_point_x + diff_x * factor_y
    transform_y = (1 - factor_y) * self.perspective_point_y
    return int(transform_x), int(transform_y)
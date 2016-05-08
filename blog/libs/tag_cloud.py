class TagCloud:
    MIN_FONT_SIZE = 18
    MAX_FONT_SIZE = 39
    FONT_SIZES = [MIN_FONT_SIZE, 21, 24, 27, 30, 33, 36, MAX_FONT_SIZE]
    # COLORS = ['#ccc', '#adadad', '#8e8e8e', '#6f6f6f', '#4f4f4f', '#303030', '#111', '#000']
    COLORS = ['#000','#000','#000','#000','#000','#000','#000','#000']
    def __init__(self, min_ref_count, max_ref_count):
        TagCloud.min_ref_count = min_ref_count
        if max_ref_count == min_ref_count:
            TagCloud.step = 0
        else:
            TagCloud.step = (TagCloud.MAX_FONT_SIZE - TagCloud.MIN_FONT_SIZE) / (max_ref_count - min_ref_count)

    def get_tag_font_size(self, tag_ref_count):
        font_size = TagCloud.MIN_FONT_SIZE + (tag_ref_count - TagCloud.min_ref_count) * TagCloud.step
        font_size = min(TagCloud.FONT_SIZES, key=lambda x: abs(font_size - x))
        return font_size

    def get_tag_color(self, tag_ref_count):
        return TagCloud.COLORS[(TagCloud.FONT_SIZES.index(self.get_tag_font_size(tag_ref_count)))]

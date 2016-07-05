
class FileHelper(object):
    def read(self, file_path='', sep=None, comment='#'):
        data = []
        if not file_path:
            return data

        lines = []
        with open(file_path) as rf:
            lines0 = rf.readlines()
            lines = []
            for line in lines0:
                line = line.strip()
                if not line.startswith(comment):
                    lines.append(line)
        if lines:
            lines = [_.split(sep) for _ in lines]
            for line in lines:
                datai = [_.strip() for _ in line]
                data.append(datai)
        return data

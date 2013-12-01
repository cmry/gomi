__author__ = 'chris'
__file__ = 'query.py'

class Query:

    def search(self, message):
        search = message.split()
        if len(search) > 3:
            pos, query = 3, str(search[2])
            while pos != len(search):
                query += " "+search[pos]
                pos += 1
        else:
            query = str(search[2])
        return query

    def cut(self, output):
        if len(output) > 446:
            output, temp = output[:-(len(output)-446)][::-1], ""
            for character in output:
                if character is '.':
                    break
                else:
                    temp += character
            output = output[::-1].replace(temp[::-1], "")
        return output
__author__ = 'chris'

class Query:

    def search(self, message):
        search = message.split()
        if len(search) > 3:
            pos = 3
            query = str(search[2])
            while pos != len(search):
                query += " "+search[pos]
                pos += 1
        else:
            query = str(search[2])
        
        return query

    def cut(self, output):
        if len(output) > 446:
            output = output[:-(len(output)-446)]
            output = output[::-1]
            temp = ""

            for character in output:
                if character == '.':
                    break
                else:
                    temp += character
            output = output[::-1].replace(temp[::-1],"")

        return output
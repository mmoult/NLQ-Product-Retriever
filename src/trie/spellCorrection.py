from src.trie.trie import Trie

class SpellCorrection():
    def __init__(self, t, word):
        """
        Creates a new spelling corrector on the given word.
        @param t: the trie structure used to find real words
        @param word: the word that may need to be corrected
        """
        self.t = t
        self.dict = {}
        self.possibleWord = []
        self.previous_modified = [word]
        self.new_modified = []
        self.word = word
        self.previous_two_words = []
        self.possibleWord_two_words=[]

    def levenshteinDistance(self,s1, s2):
        if len(s1) > len(s2):
            s1, s2 = s2, s1

        distances = range(len(s1) + 1)
        for i2, c2 in enumerate(s2):
            distances_ = [i2 + 1]
            for i1, c1 in enumerate(s1):
                if c1 == c2:
                    distances_.append(distances[i1])
                else:
                    distances_.append(1 + min((distances[i1], distances[i1 + 1], distances_[-1])))
            distances = distances_
        return distances[-1]

    def Deletion(self, word):
        for i in range(len(word)-1):
            temp = word[:i]+word[i+1:]
            if self.t.search(temp):
                self.possibleWord.append(temp)
            else:
                self.new_modified.append(temp)
    def Insertion(self, word):
        for i in range(len(word)+1):
            j = ord('a')
            while (j - ord('a') <26) :
                temp = word[:i]+chr(j)+word[i:]
                if self.t.search(temp):
                    self.possibleWord.append(temp)
                else:
                    self.new_modified.append(temp)
                j+=1
    def Transposition(self, word):
        for i in range(len(word)-1):
            temp = word[:i] + word[i + 1] + word[i] +word[i+2:]
            if self.t.search(temp):
                self.possibleWord.append(temp)
            else:
                self.new_modified.append(temp)
    def Alteration(self, word):
        for i in range(len(word)):
            j = ord('a')
            while (j - ord('a') < 26):
                temp = word[:i] + chr(j) + word[i+1:]
                j+=1
                if self.t.search(temp):
                    self.possibleWord.append(temp)
                else:
                    self.new_modified.append(temp)

    def suggestion(self):
        if self.word == '' or self.word ==' ':
            return self.word
        if self.t.search(self.word):
            return self.word
        else:
            self.Deletion(self.word)
            self.Insertion(self.word)
            self.Transposition(self.word)
            self.Alteration(self.word)
            self.previous_modified = self.new_modified
            self.new_modified = []
            for i in range(len(self.word)):
                if self.t.search(self.word[:i]):
                    if self.t.search(self.word[i:]):
                        self.possibleWord.append(self.word[:i]+' '+self.word[i:])
            if not self.possibleWord:
                while True:
                    for i in range(len(self.word)):
                        if self.t.search(self.word[:i]):
                            first_half = self.word[:i]
                            self.previous_two_words = [self.word[i:]]
                            for word in self.previous_two_words:
                                self.Deletion(word)
                                self.Insertion(word)
                                self.Transposition(word)
                                self.Alteration(word)
                            self.previous_two_words = self.new_modified
                            self.new_modified = []
                            self.possibleWord_two_words.extend([first_half+ ' '+ i for i in self.possibleWord])
                            self.possibleWord=[]
                    if self.possibleWord_two_words:
                        self.possibleWord=self.possibleWord_two_words
                        break

                    for word in self.previous_modified:
                        self.Deletion(word)
                        self.Insertion(word)
                        self.Transposition(word)
                        self.Alteration(word)
                    self.previous_modified = self.new_modified
                    self.new_modified = []
                    if self.possibleWord:
                        break

            distance_dict = {}
            for w2 in self.possibleWord:
                # d = self.edit_distance(self.word, w2)
                d = self.levenshteinDistance(self.word, w2)
                distance_dict[w2] = d

            minval = min(distance_dict.values())
            res = [k for k, v in distance_dict.items() if v == minval]

            count_dict = {}
            for r in res:
                l = r.split()
                count = 0
                for w in l:
                    count+= self.t.word_count(w)
                count_dict[r]= count
            minval = max(count_dict.values())
            res = [k for k, v in count_dict.items() if v == minval]
            return res

if __name__ == "__main__":
    keys = ["honda", "accord", "accura", "accord","handai"]  # keys to form the trie structure.
    status = ["Not found", "Found"]
    trie = Trie()
    for word in keys:
        trie.insert(word)
    corrector = SpellCorrection(trie,'accur')
    result = corrector.suggestion()
    print(result[0])

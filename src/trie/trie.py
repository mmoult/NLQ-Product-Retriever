# Adapted from:
"https://medium.com/@info.gildacademy/a-simpler-way-to-implement-trie-data-structure-in-python-efa6a958a4f2"


class TrieNode():

    def __init__(self):
        self.children = dict()
        self.terminating = False
        self.count = 0

class Trie():

    def __init__(self):
        self.root = self.get_node()
        self.wordSet = set()

    def get_node(self):
        return TrieNode()

    def get_index(self, ch):
        return ord(ch) - ord('a')

    def insert(self, word):
        root = self.root
        len1 = len(word)

        for i in range(len1):
            index = self.get_index(word[i])
            if index not in root.children:
                root.children[index] = self.get_node()
            root = root.children.get(index)
            root.count += 1
            if root.count == 1:
                self.wordSet.add(word)
        root.terminating = True

    def word_count(self, word):
        root = self.root
        for c in word:
            index = self.get_index(c)
            if not root:
                return 0
            root = root.children.get(index)
        return root.count

    def search(self, word) -> bool:
        root = self.root

        for c in word:
            index = self.get_index(c)
            if root is None:
                break
            root = root.children.get(index)

        # Return what we got so far. If the request is for a word longer than in the
        #  trie, None is returned. If the request is for a word shorter or the same
        #  length as in the trie, the progress will be returned.
        return root
    
    def __contains__(self, word):
        res = self.searc(word)
        if res is None:
            return None
        elif res.terminating:
            return True
        return False

    def delete(self, word) -> bool:
        '''
        Deletes the specified token, if found.
        Returns whether the token was present before deletion.
        '''
        root = self.root
        len1 = len(word)

        for i in range(len1):
            index = self.get_index(word[i])

            if not root:
                return False
            root = root.children.get(index)
            self.wordSet.remove(word)

        if not root:
            return False
        root.terminating = False
        return True

    def update(self, old_word, new_word):
        # If the word was present before deletion, insert the replacement
        if self.delete(old_word):
            self.insert(new_word)

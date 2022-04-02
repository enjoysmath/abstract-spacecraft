
class TrieNode:
    def __init__(self, value, end=False):
        self.end = end
        self.value = value
        self.children = {}

    def __repr__(self):
        children = list(self.children.keys())
        return f'{self.value} => {children} {"<- end of word" if self.end else ""}'


class Trie:
    def __init__(self):
        self.root = TrieNode(None)

    def get_child(self, node: TrieNode, char: str):
        try:
            return node.children[char]
        except KeyError as e:
            return None

    def __print_trie(self, node: TrieNode, space=0, indent=4):
        print(f'{" " * space} {node}')
        for key in node.children:
            self.__print_trie(node.children[key], space=space+indent, indent=indent)

    def print(self, indent=4):
        """
        Prints the trie
        :param indent: while printing the trie, the amount of indent for each level
        :return:
        """
        node = self.root
        self.__print_trie(node, indent=indent)

    def insert(self, string: str, value=None) -> None:
        """
        Inserts a string inside the trie
        :param string: the word you want to enter in the trie
        :return:
        """
        if string == "":
            return

        node = self.root
        for index, char in enumerate(string):
            is_last = index == (len(string) - 1)
            next_node = self.get_child(node, char)
            if next_node is None:
                node.children[char] = TrieNode(char, end=is_last)

            node = node.children[char]
            if not node.end:
                node.end = is_last
                
        node.value = value

    def search(self, string: str) -> bool:
        """
        Checks whether the given string exists in the trie
        :param string: the input word you want to search
        :return: True if the word exists otherwise false
        """
        if string == "":
            return False

        node = self.root
        for index, char in enumerate(string):
            node = self.get_child(node, char)
            if node is None:
                return False

        return node.end

    def prefix_search(self, prefix: str) -> bool:
        """
        Checks whether this prefix exists in the string
        :param prefix: the prefix you want to search in the trie
        :returns: True if any word with the input prefix exists otherwise false
        """
        if prefix == "":
            return False

        node = self.root
        for char in prefix:
            node = self.get_child(node, char)
            if node is None:
                return False

        return node is not None

    def all_suffixes(self, node: TrieNode,  suffix=''):
        """
        Starting at any node, it generates all possible suffixes according to trie
        :param node: the node from which you want all the suffixes
        :param suffix: the initial string which is extended for each possibility
        :return: A generator that yields all possible suffixes
        """
        if len(node.children) == 0:
            return
        else:
            children = list(node.children.keys())
            for char in children:
                next_node = self.get_child(node, char)
                next_suffix = suffix + char
                if next_node.end:
                    yield next_suffix

                yield from self.all_suffixes(next_node, suffix=next_suffix)

    def autocomplete(self, prefix: str, count=10) -> list:
        """
        Return a list of autocomplete words for a given prefix. Returns empty if prefix does not match
        :param prefix: Search prefix for searching all the words
        :param count: number of results to return
        :return res: A list of words in the trie with the input prefix
        """
        node = self.root
        for char in prefix:
            node = self.get_child(node, char)
            if node is None:
                # Prefix not present
                break

        if node is None:
            return []

        res = []
        if node.end:
            res.append(prefix)

        cnt = 0
        for i in self.all_suffixes(node, suffix=prefix):
            res.append(i)
            cnt += 1
            if cnt > count:
                break

        return res

    def delete(self, word: str):
        """
        Deletes a word from the trie and raises a valueerror if the word does not exist
        :param word: the word to delete
        :return:
        """
        node = self.root
        stack = []
        stack.append(node)
        for char in word:
            node = self.get_child(node, char)
            if node is None:
                break
            stack.append(node)

        if node is None or not node.end:
            raise ValueError(f'"{word}" not found in trie to delete')

        node.end = False
        if len(node.children) > 0:
            return

        while len(stack) > 0:
            node = stack.pop(len(stack) - 1)
            if not node.end and len(node.children) == 0:
                if len(stack) > 0:
                    del stack[-1].children[node.value]
                    continue

            break
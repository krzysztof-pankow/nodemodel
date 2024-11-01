from nodemodel.utils import node


def test_node_decorator_without_brackets():
    @node
    def test():
        '''test_doc'''
        return 1

    assert test.__doc__ == "test_doc"
    assert test.__name__ == "test"
    assert test() == 1
    assert hasattr(test,"node_tag")
    assert not hasattr(test,"forced_nodes")

def test_node_decorator_with_brackets():
    @node()
    def test():
        '''test_doc'''
        return 1

    assert test.__doc__ == "test_doc"
    assert test.__name__ == "test"
    assert test() == 1
    assert hasattr(test,"node_tag")
    assert not hasattr(test,"forced_nodes")

def test_node_decorator_with_tag_argument():
    @node(tag = "my_tag")
    def test():
        '''test_doc'''
        return 1

    assert test.__doc__ == "test_doc"
    assert test.__name__ == "test"
    assert test() == 1
    assert hasattr(test,"node_tag")
    assert test.node_tag == "my_tag"
    assert not hasattr(test,"forced_nodes")


def test_node_decorator_with_tag_argument_and_forced_nodes():
    @node(tag = "my_tag",a = 5,b = "c")
    def test():
        '''test_doc'''
        return 1

    assert test.__doc__ == "test_doc"
    assert test.__name__ == "test"
    assert test() == 1
    assert hasattr(test,"node_tag")
    assert test.node_tag == "my_tag"
    assert hasattr(test,"forced_nodes")
    assert test.forced_nodes == {'a':5,'b':"c"}

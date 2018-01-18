from autoskip.util import flatten_imports


def test_module_reconvergence():
    #       A
    #      / \
    #     B   C
    #      \ /
    #       D
    import_tree = {
        'D': {'B', 'C'},
        'C': {'A'},
        'B': {'A'},
        'A': set(),
    }

    assert flatten_imports('D', import_tree) == {'A', 'B', 'C', 'D'}

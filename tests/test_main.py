from typing import Any, Callable, Dict, List, Union
import async

def get_testing_print_function(calls: List[List[Union[str, Dict[str, Any]]]]) -> Callable[..., Any]:
    def new_print(*args):
        data = [arg for arg in args]
        calls.append(data)

    return new_print

def test_pending_repr():
    assert str(asyncer._main.Pending) == "AsyncerPending"
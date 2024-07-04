from stretchable import Node

class ContainerNode(Node):
    def __init__(self, *args, **kwargs) -> None:
        super(ContainerNode, self).__init__(*args, **kwargs)

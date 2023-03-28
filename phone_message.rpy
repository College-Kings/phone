init python:
    class BaseMessage:
        def __init__(self, contact: Contact, content: str):
            self.contact = contact
            self.content = content
            self.message = content
            self.image = content
            self.replies: list[BaseReply] = []
            self.reply: Optional[BaseReply] = None

        def __repr__(self):
            return f"<{self.__class__.__name__}({self.content})>"


    @dataclass
    class Reply(BaseMessage):
        content: str
        next_message: Optional[MessageBuilder] = None

        def send(self):
            self.contact.text_messages.append(self)

    class ImgReply(BaseMessage):
        def __init__(
            self,
            image: str,
            func: Optional[Callable[[], None]] = None,
        ):
            super().__init__(mc, image)

            self.func = func

    @dataclass
    class Message:
        contact: NonPlayableCharacter
        content: str
        replies: list[Reply] = field(default_factory=list)

        def send(self):
            self.contact.text_messages.append(self)

    class ImageMessage(BaseMessage):
        def __init__(self, contact: Contact, image: str):
            super().__init__(contact, image)


    BaseReply = Union[Reply, ImgReply]

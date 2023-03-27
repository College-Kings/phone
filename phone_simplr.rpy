init python:
    class SimplrContact:
        def __init__(self, name: str, user: Union[PlayableCharacter, NonPlayableCharacter]):
            super().__init__(name, user)
            self.condition = True

            self._notification = False

            self.sent_messages = []
            self.pending_messages = []

            simplr_app.unlock()

        def __repr__(self):
            return f"<SimplrContact({self.name})>"

        @property
        def notification(self):
            if not self.sent_messages and not self.pending_messages:
                return False

            if self.replies:
                return True

            return self._notification

        @notification.setter
        def notification(self, value):
            self._notification = value

        @property
        def profile_picture(self):
            return self.profile_pictures[0]

        @property
        def profile_pictures(self):
            # noinspection PyUnresolvedReferences
            return [
                file
                for file in renpy.list_files()
                if file.startswith(
                    f"images/characters/{self.name.lower()}/large_profile_pictures/"
                )
            ]

        def removeContact(self):
            try:
                simplr_app.pending_contacts.remove(self)
            except ValueError:
                pass

        def likedContact(self):
            simplr_app.pending_contacts.remove(self)

            if self.condition:
                simplr_app.contacts.append(self)

        def newMessage(self, message, force_send=False):
            message = Message(self, message)

            # Moves contact to the top when receiving a new message
            if self in simplr_app.contacts:
                simplr_app.contacts.insert(
                    0, simplr_app.contacts.pop(simplr_app.contacts.index(self))
                )

            # Add message to queue
            if not force_send:
                self.pending_messages.append(message)
            else:
                self.pending_messages = []
                self.sent_messages.append(message)

            return message

        def newImgMessage(self, img, force_send=False):
            message = ImageMessage(self, img)

            # Moves contact to the top when receiving a new message
            if self in simplr_app.contacts:
                simplr_app.contacts.insert(
                    0, simplr_app.contacts.pop(simplr_app.contacts.index(self))
                )

            # Add message to queue
            if not force_send:
                self.pending_messages.append(message)
            else:
                self.pending_messages = []
                self.sent_messages.append(message)

            return message

        def addReply(
            self,
            message: str,
            func: Optional[Callable[[], None]] = None,
            new_message: bool = False,
        ):
            reply = Reply(message, func)

            # Append reply to last sent message
            try:
                if self.pending_messages:
                    self.pending_messages[-1].replies.append(reply)
                else:
                    self.sent_messages[-1].replies.append(reply)
            except IndexError:
                message = self.new_message("", force_send=True)
                message.replies.append(reply)

        def addImgReply(
            self,
            image: str,
            func: Optional[Callable[[], None]] = None,
            new_message: bool = False,
        ):
            reply = ImgReply(image, func)

            # Append reply to last sent message
            try:
                if self.pending_messages:
                    self.pending_messages[-1].replies.append(reply)
                else:
                    self.sent_messages[-1].replies.append(reply)
            except IndexError:
                self.new_message("", force_send=True)
                self.pending_messages[-1].replies.append(reply)

        def getMessage(self, message):
            for msg in self.sent_messages:
                try:
                    if message == msg.message:
                        return msg
                except AttributeError:
                    if message == msg.image:
                        return msg
            return False


screen simplr_home():
    tag phone_tag
    modal True
    
    python:
        try: simplr_contact = simplr_app.pending_contacts[0]
        except IndexError: simplr_contact = None

    use base_phone:
        frame:
            background "simplr_background"
            
            # Top UI
            imagebutton:
                pos (340, 100)
                idle "simplr_message_icon_idle"
                hover "simplr_message_icon_hover"
                action Show("simplr_contacts")

            if simplr_contact is not None:
                frame:
                    background simplr_contact.profile_picture
                    xysize (370, 593)
                    xalign 0.5
                    ypos 200
                    
                    hbox:
                        align (0.5, 1.0)
                        yoffset -10
                        spacing 10

                        imagebutton:
                            idle "simplr_like_button_idle"
                            hover "simplr_like_button_hover"
                            action Function(simplr_contact.likedContact)

                        imagebutton:
                            idle "simplr_no_button_idle"
                            hover "simplr_no_button_hover"
                            action Function(simplr_contact.removeContact)

            else:
                text _("No new profiles to show...\nYou can however still chat with your matches!\n\nBe sure to check back soon!"):
                    style "simplr_no_more_profiles"
                    align (0.5, 0.5)
                    xsize 340


screen simplr_contacts():
    tag phone_tag

    use base_phone:
        frame:
            background "simplr_contacts_background"
            xysize (433, 918)

            viewport:
                mousewheel True
                draggable True
                pos (11, 134)
                xysize (416, 709)

                vbox:
                    spacing 5

                    null height 10

                    for contact in simplr_app.contacts:
                        button:
                            action [Function(renpy.retain_after_load), SetField(contact, "notification", False), Show("simplr_messenger", contact=contact)]
                            ysize 80

                            add Transform(contact.user.profile_picture, xysize=(65, 65)) xpos 20 yalign 0.5
                            
                            text contact.name style "nametext" xpos 100 yalign 0.5

                            if contact.notification:
                                add "phone_contact_notification" align (1.0, 0.5) xoffset -25


screen simplr_messenger(contact):
    tag phone_tag
    modal True

    use base_phone:
        frame:
            background "simplr_conversation_background"
            xysize (433, 918)

            hbox:
                pos (41, 62)
                ysize 93
                spacing 15

                imagebutton:
                    idle "phone_back_button"
                    action [Hide("message_reply"), Show("simplr_home")]
                    yalign 0.5

                add Transform(contact.user.profile_picture, xysize=(65, 65)) yalign 0.5

                text contact.name style "nametext" yalign 0.5

            viewport:
                yadjustment inf_adj
                mousewheel True
                pos (11, 157)
                xysize (416, 686)

                vbox:
                    spacing 5

                    null height 5

                    for message in contact.sent_messages:
                        frame:
                            padding (50, 50)

                            if isinstance(message, Message) and message.message.strip():
                                background "phone_message_background"

                                text message.message style "message_text"

                            elif isinstance(message, ImageMessage):
                                background "phone_message_background"

                                imagebutton:
                                    idle Transform(message.image, ysize=216)
                                    action Show("phone_image", img=message.image)

                            elif isinstance(message, Reply):
                                padding (50, 35)
                                background "phone_reply_background"
                                xalign 1.0

                                text message.message  style "reply_text"

                            elif isinstance(message, ImgReply):
                                padding (25, 25)
                                background "phone_reply_background"
                                xalign 1.0

                                imagebutton:
                                    idle Transform(message.image, zoom=0.15)
                                    action Show("phone_image", img=message.image)

            if contact.replies:
                fixed:
                    xysize (416, 63)
                    ypos 780

                    imagebutton:
                        idle "phone_reply_button_idle"
                        hover "simplr_reply_button_hover"
                        selected_idle "simplr_reply_button_hover"
                        action Show("message_reply", contact=contact)
                        align (0.5, 0.5)

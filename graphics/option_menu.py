# -*- encoding: utf-8 -*-
import termbox

from drawing import *


class OptionMenu:
    def __init__(self, t, options, title=""):
        self.t = t

        self.title = title
        self.options = options
        self.selected = 0
        self.open = True

    def show(self):
        self.draw_menu()

        while self.open:
            event = self.t.poll_event()
            while event:
                (kind, ch, key, mod, w, h, x, y) = event
                if kind == termbox.EVENT_KEY and key == termbox.KEY_ESC:
                    self.selected = -1
                    self.open = False
                if kind == termbox.EVENT_KEY:
                    if key == termbox.KEY_ARROW_UP:
                        self.selected = (self.selected - 1) % len(self.options)
                    elif key == termbox.KEY_ARROW_DOWN:
                        self.selected = (self.selected + 1) % len(self.options)
                    elif key == termbox.KEY_ENTER:
                        self.open = False
                event = self.t.peek_event()

            if self.open:
                self.draw_menu()

        return self.selected

    def draw_menu(self):
        self.update_dimensions()

        # Clear
        fill(self.t, self.x0 + 1, self.y0 + 1, self.width - 2, self.height - 2, 32)

        offset_y = 0  # Vertical offset if a title is present
        offset_x = 0  # Horizontal negative offset if a scroll bar is present

        # If there's a title, add a separator in the box
        h_seps = []
        if self.title != "":
            offset_y = 2
            h_seps.append(2)
        # Draw box, with eventual separator
        draw_box(self.t, self.x0, self.y0, self.width, self.height, h_seps=h_seps)

        # Centered title
        # FIXME: Account for title in widget width
        draw_text(self.t, self.x0 + 1, self.y0 + 1, " " * ((self.width - 2 - len(self.title)) / 2) + self.title)

        # Figure out if we need to limit the view due to too many options
        view = self.options
        max_items = self.height - offset_y - 2
        offset_selected = 0
        # If too many options..
        if len(view) > max_items:
            # If selected option is further than the first half of first visible part the list,
            if self.selected > max_items / 2:
                # Start offsetting the view
                offset_selected = self.selected - (max_items / 2)
            # If we reach the end of the list,
            if self.selected > len(view) - (max_items / 2):
                # Keep a fixed offset
                offset_selected = len(view) - max_items

            view = view[offset_selected:max_items + offset_selected]
            offset_x = 1

        # Draw all options
        for y, item in enumerate(view):
            text = " " + item                                           # Prepend a space for visual prettiness
            if len(text) < self.width - 2 - offset_x:                   # If option too short,
                text += " " * (self.width - 2 - len(text) - offset_x)   # add spaces for highlight when selected
            elif len(text) > self.width - 3 - offset_x:                 # If too long,
                text = text[:self.width - 6 - offset_x] + "... "        # truncate
            if y == self.selected - offset_selected:                    # If it's the selected option,
                text = "$" + text                                       # highlight using custom markup

            draw_text(self.t, self.x0 + 1, self.y0 + offset_y + y + 1, text)

        # Draw scrollbar if present
        if offset_x != 0:
            draw_scroll_bar(self.t, self.x0 + self.width - 2, self.y0 + 1 + offset_y, self.height - 2 - offset_y,
                            max_items, len(self.options), self.selected)

        self.t.present()

    def update_dimensions(self):
        # Prevent menu from taking the whole screen
        max_width = 2 * self.t.width() / 5
        max_height = 2 * self.t.height() / 3

        longest = len(max(self.options, key=len))
        # Fit menu to option lengths if small enough, else use proportions
        self.width = (max_width if longest >= max_width else longest) + 4
        self.height = (max_height if len(self.options) >= max_height else len(self.options)) + 2

        # If a title is displayed, add more height
        if self.title != "":
            self.height += 2
        # If a scroll bar will be displayed, add more width
        if len(self.options) > self.height - (4 if self.title == "" else 2):
            self.width += 1

        # Center the menu
        self.x0 = (self.t.width() - self.width) / 2
        self.y0 = (self.t.height() - self.height) / 2
